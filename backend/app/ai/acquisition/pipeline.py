from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

from app.ai.chunking.technical_chunker import TechnicalDocumentChunker
from app.ai.acquisition.deduplicator import DocumentRecord, DocumentDeduplicator
from app.ai.acquisition.classifier import DocumentClassifier
from app.ai.acquisition.external_search import (
    BaseExternalSearcher,
    SearchCandidate,
    WebExternalSearcher,
    build_search_queries,
    is_gyproc_alias_match,
    _VERIFIED_MANUFACTURER_DOMAINS,
    _GYPROC_ALIASES,
)
from app.ai.acquisition.registry_builder import MissingDataRegistry, MissingItem
from app.ai.acquisition.manifest_builder import DatasetManifest
from app.ai.acquisition.reporter import ReportGenerator
from app.ai.acquisition.validator import DocumentValidator, ValidationResult
from app.ai.ingestion.cleaner import BaseCleaner
from app.ai.ingestion.ocr_processor import OcrProcessor
from app.ai.ingestion.pdf_processor import PdfProcessor
from app.ai.schemas.product import ProductCreate
from app.ai.config import AI_RAW_DIR, AI_REPORTS_DIR

logger = logging.getLogger(__name__)

_PIPELINE_VERSION = "6.5.0"
_BASE_REPORT_DIR = AI_REPORTS_DIR
_BASE_RAW_DIR = AI_RAW_DIR


@dataclass
class PipelineResult:
    products_by_brand: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    document_records: list[DocumentRecord] = field(default_factory=list)
    missing_items: list[MissingItem] = field(default_factory=list)
    manifest_path: str = ""
    registry_path: str = ""
    report_path: str = ""
    stats: dict[str, int] = field(default_factory=dict)


class AcquisitionPipeline:
    """Orchestrates the complete data acquisition workflow.

    Workflow:
        Website → Product Discovery → Product Metadata →
        Document Discovery → Document Validation → PDF Download →
        Text Extraction / OCR → Cleaning → Chunking →
        Embedding → Qdrant
    """

    BRAND_SPECS = {
        "gypsobat": {
            "base_url": "https://www.gypsobat.com",
            "manufacturer": "Gypsobat",
            "language": "fr",
        },
        "emtop": {
            "base_url": "https://emtoptunisie.com",
            "manufacturer": "EMTOP",
            "language": "fr",
        },
        "sofap": {
            "base_url": "https://sofapbatiment.com",
            "manufacturer": "SOFAP",
            "language": "fr",
        },
    }

    def __init__(
        self,
        validator: DocumentValidator | None = None,
        deduplicator: DocumentDeduplicator | None = None,
        cleaner: BaseCleaner | None = None,
        ocr_processor: OcrProcessor | None = None,
        chunker: TechnicalDocumentChunker | None = None,
        embedding_provider: Any = None,
        vector_store: Any = None,
        external_searcher: Any = None,
        fallback_searcher_factory: Any = None,
        manifest: DatasetManifest | None = None,
        registry: MissingDataRegistry | None = None,
        reporter: ReportGenerator | None = None,
    ) -> None:
        self.validator = validator or DocumentValidator()
        self.deduplicator = deduplicator or DocumentDeduplicator()
        self.cleaner = cleaner or BaseCleaner()
        self.ocr_processor = ocr_processor or OcrProcessor()
        self.chunker = chunker or TechnicalDocumentChunker()
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.external_searcher = external_searcher
        self.fallback_searcher_factory = fallback_searcher_factory
        self.manifest = manifest or DatasetManifest()
        self.registry = registry or MissingDataRegistry()
        self.reporter = reporter or ReportGenerator()

        self._processed_hashes: set[str] = set()
        self._indexed_chunk_ids: set[str] = set()

    def run(self, brands: list[str] | None = None) -> PipelineResult:
        """Run the full acquisition pipeline for the specified brands."""
        brands = brands or list(self.BRAND_SPECS.keys())
        logger.info("Starting acquisition pipeline v%s for brands: %s", _PIPELINE_VERSION, brands)

        source_urls = []
        for brand in brands:
            spec = self.BRAND_SPECS.get(brand, {})
            source_urls.append(spec.get("base_url", ""))
        self.manifest.set_source_urls(source_urls)
        self.manifest.set_pipeline_version(_PIPELINE_VERSION)

        products_by_brand: dict[str, list[dict[str, Any]]] = {}
        all_records: list[DocumentRecord] = []
        all_missing_items: list[MissingItem] = []

        from app.ai.scraping.registry import get_scraper

        for brand in brands:
            logger.info("=== Processing brand: %s ===", brand)
            scraper = get_scraper(brand)
            spec = self.BRAND_SPECS.get(brand, {})

            products = self._discover_and_scrape_products(scraper, brand, spec)
            products_by_brand[brand] = products

            product_docs = self._process_brand_products(products, brand, spec)
            all_records.extend(product_docs["records"])

        for brand in brands:
            brand_records = [r for r in all_records if r.source and r.source.lower() == brand]
            missing_items, external_records = self._handle_missing_documents(
                products_by_brand.get(brand, []),
                brand_records,
                brand,
                self.BRAND_SPECS.get(brand, {}),
            )
            all_missing_items.extend(missing_items)
            if external_records:
                self._process_document_content(external_records)
                all_records.extend(external_records)

        self._process_document_content(all_records)
        self._index_documents(all_records)

        for brand in brands:
            brand_records = [r for r in all_records if r.source and r.source.lower() == brand]
            brand_records += [r for r in all_records if r.supplier and r.supplier.lower() == brand]
            brand_products = products_by_brand.get(brand, [])
            self.manifest.build_from_records(
                brand=brand,
                total_products=len(brand_products),
                products=brand_products,
                records=brand_records,
                deduplicator=self.deduplicator,
            )

        self.registry.add_items(all_missing_items)
        registry_path = self.registry.save()
        manifest_path = self.manifest.save()
        report_path = self.reporter.generate(
            products_by_brand=products_by_brand,
            document_records=all_records,
            missing_registry=self.registry,
            manifest=self.manifest,
        )

        stats = self._compute_final_stats(all_records, products_by_brand)

        result = PipelineResult(
            products_by_brand=products_by_brand,
            document_records=all_records,
            missing_items=all_missing_items,
            manifest_path=manifest_path,
            registry_path=registry_path,
            report_path=report_path,
            stats=stats,
        )

        logger.info("Acquisition pipeline complete. Stats: %s", stats)
        return result

    def _discover_and_scrape_products(
        self, scraper: Any, brand: str, spec: dict[str, Any]
    ) -> list[dict[str, Any]]:
        products_out: list[dict[str, Any]] = []

        discovered = scraper.discover_products()
        logger.info("%s: Discovered %d products", brand, len(discovered))

        for item in discovered:
            product_url = item.get("url", "")
            product_id = item.get("id", "")
            try:
                product = scraper.scrape_product(product_url)
                docs = scraper.discover_documents(product)
                product_dict = product.model_dump(mode="json", exclude_unset=True)
                product_dict["documents"] = docs
                products_out.append(product_dict)
                logger.info("%s: Scraped product %s with %d documents",
                            brand, product.name, len(docs))
            except Exception as exc:
                logger.warning("%s: Failed to scrape product %s: %s", brand, product_url, exc)
                products_out.append({
                    "product_url": product_url,
                    "product_id": product_id,
                    "name": None,
                    "brand": spec.get("manufacturer", brand),
                    "manufacturer": spec.get("manufacturer", brand),
                    "documents": [],
                    "error": str(exc),
                    "source_url": product_url,
                })
            time.sleep(1.0)

        return products_out

    def _process_brand_products(
        self, products: list[dict[str, Any]], brand: str, spec: dict[str, Any]
    ) -> dict[str, Any]:
        records: list[DocumentRecord] = []
        seen_product_keys: set[str] = set()

        for product in products:
            product_name = product.get("name") or "Unknown"
            product_url = product.get("source_url") or product.get("product_url") or ""
            docs = product.get("documents", []) or []

            if not docs:
                continue

            for doc in docs:
                doc_url = doc.get("document_url", "")
                if not doc_url:
                    continue

                result = self.validator.validate_and_download(doc_url, brand)

                record = DocumentRecord(
                    document_url=doc_url,
                    product_name=product_name,
                    source=brand,
                    source_url=doc.get("source_url", ""),
                    document_type=doc.get("document_type", "technical_sheet"),
                    title=doc.get("title", ""),
                    mime_type=doc.get("mime_type"),
                    supplier=doc.get("supplier", spec.get("manufacturer", brand)),
                    confidence=doc.get("confidence", "medium"),
                    source_type=doc.get("source_type", "official"),
                    evidence=doc.get("evidence", ""),
                    http_status=result.http_status,
                    content_type=result.content_type,
                    is_pdf=result.is_pdf,
                    downloadable=result.downloadable,
                    content_hash=result.content_hash,
                    file_path=result.file_path,
                    validation_error=result.error,
                    size_bytes=result.size_bytes,
                )

                is_new = self.deduplicator.register(record)
                if not is_new:
                    record.canonical_url = record.canonical_url or record.duplicate_of
                    existing = self._find_canonical_record(record.content_hash or "")
                    if existing:
                        record.processed = existing.processed
                        record.chunk_count = existing.chunk_count
                        record.indexed = existing.indexed
                        record.text_extractable = existing.text_extractable

                records.append(record)

        return {"records": records}

    def _process_document_content(self, records: list[DocumentRecord]) -> None:
        """Extract text and handle OCR for all downloaded PDFs.

        Updates each record with text_extractable, ocr_required,
        ocr_attempted, ocr_succeeded, ocr_error, page_count, processed.
        Skips duplicate records (those linked to a canonical).
        """
        processor = PdfProcessor(cleaner=self.cleaner, ocr_processor=self.ocr_processor)

        for record in records:
            if record.duplicate_of and not record.text_extractable:
                existing = self._find_canonical_record(record.content_hash or "")
                if existing:
                    record.text_extractable = existing.text_extractable
                    record.ocr_required = existing.ocr_required
                    record.ocr_attempted = existing.ocr_attempted
                    record.ocr_succeeded = existing.ocr_succeeded
                    record.ocr_error = existing.ocr_error
                    record.page_count = existing.page_count
                    record.processed = existing.processed
                    continue

            if not record.file_path or not record.is_pdf or not record.downloadable:
                if record.validation_error:
                    record.ocr_error = record.validation_error
                continue

            if not record.file_path or not Path(record.file_path).exists():
                continue

            try:
                result = processor.extract(record.file_path)
            except Exception as exc:
                record.ocr_error = f"PDF processing failed: {exc}"
                logger.warning("PDF processing failed for %s: %s",
                               record.document_url, exc)
                continue

            record.page_count = result.get("page_count", 0)
            raw_text = result.get("raw_text", "") or ""
            cleaned_text = result.get("cleaned_text", "") or ""
            record.text_extractable = len(cleaned_text.strip()) > 0

            ocr_info = result.get("ocr", {})
            record.ocr_required = ocr_info.get("required", False)
            record.ocr_attempted = ocr_info.get("attempted", False)
            record.ocr_succeeded = (
                ocr_info.get("attempted", False)
                and bool(ocr_info.get("cleaned_text", ""))
            )
            record.ocr_error = ocr_info.get("error")

            if record.text_extractable:
                record.processed = True
                record.extracted_content = cleaned_text
            elif record.ocr_succeeded:
                record.processed = True
                record.extracted_content = ocr_info.get("cleaned_text", "")

    def _find_canonical_record(self, content_hash: str) -> DocumentRecord | None:
        for r in self.deduplicator.all_records():
            if r.content_hash == content_hash and not r.duplicate_of:
                return r
        return None

    def _handle_missing_documents(
        self,
        products: list[dict[str, Any]],
        records: list[DocumentRecord],
        brand: str,
        spec: dict[str, Any],
    ) -> tuple[list[MissingItem], list[DocumentRecord]]:
        missing_items: list[MissingItem] = []
        external_records: list[DocumentRecord] = []

        processed_hashes = {r.content_hash for r in records if r.processed and r.content_hash}

        for product in products:
            product_name = product.get("name") or "Unknown"
            product_url = product.get("source_url") or product.get("product_url") or ""
            docs = product.get("documents", []) or []
            model = None
            ts = product.get("technical_specifications")
            if isinstance(ts, dict):
                model = ts.get("reference") or ts.get("model") or ts.get("sku")

            manufacturer = product.get("manufacturer") or spec.get("manufacturer", brand)

            has_valid_doc = False
            has_broken_doc = False
            original_doc_url = ""
            original_source = ""

            for doc in docs:
                doc_url = doc.get("document_url", "")
                if not doc_url:
                    continue
                original_doc_url = doc_url
                original_source = doc.get("source_url", "")

                record = self._find_record_by_url(doc_url, records)
                if record:
                    if record.processed and record.content_hash in processed_hashes:
                        has_valid_doc = True
                    elif DocumentClassifier.classify(record) in ("broken", "invalid"):
                        has_broken_doc = True
                else:
                    has_broken_doc = True

            if has_valid_doc:
                continue

            missing_type = "technical_document"
            status = "not_found" if not docs else "broken_link"

            if not docs:
                missing_type = "technical_document"
                status = "not_found"
            elif has_broken_doc:
                missing_type = "accessible_pdf"
                status = "broken_link"
            else:
                missing_type = "extractable_text"
                status = "external_candidate_found"

            external_candidates: list[dict[str, Any]] = []
            external_search_attempted = False
            primary_blocked = False

            if self.external_searcher is not None:
                external_search_attempted = True
                queries = build_search_queries(
                    product_name,
                    model if isinstance(model, str) else None,
                    manufacturer=manufacturer,
                )
                for query in queries[:5]:
                    try:
                        candidates = self.external_searcher.search(query, max_results=5)
                    except Exception as exc:
                        logger.warning("Primary external search failed for '%s': %s", query, exc)
                        primary_blocked = True
                        break

                    if hasattr(self.external_searcher, "provider_status") and self.external_searcher.provider_status == "blocked":
                        primary_blocked = True
                        break

                    for cand in candidates:
                        if self._is_relevant_candidate(cand, product_name, model, manufacturer=manufacturer):
                            external_candidates.append(cand.to_dict())
                            if len(external_candidates) >= 5:
                                break
                    if len(external_candidates) >= 5:
                        break

                    time.sleep(1.0)

            if (primary_blocked or not external_candidates) and self.fallback_searcher_factory is not None:
                fallback_searcher = self.fallback_searcher_factory(
                    manufacturer,
                    product_name,
                    model if isinstance(model, str) else None,
                )
                if fallback_searcher is not None:
                    external_search_attempted = True
                    queries = build_search_queries(
                        product_name,
                        model if isinstance(model, str) else None,
                        manufacturer=manufacturer,
                    )
                    for query in queries[:5]:
                        try:
                            candidates = fallback_searcher.search(query, max_results=5)
                        except Exception as exc:
                            logger.warning("Fallback external search failed for '%s': %s", query, exc)
                            break

                        for cand in candidates:
                            if self._is_relevant_candidate(cand, product_name, model, manufacturer=manufacturer):
                                candidate_dict = cand.to_dict()
                                candidate_dict.setdefault("discovery_provider", "manufacturer_targeted")
                                external_candidates.append(candidate_dict)
                                if len(external_candidates) >= 5:
                                    break
                        if len(external_candidates) >= 5:
                            break

                        time.sleep(1.0)

            if external_candidates:
                best = external_candidates[0]
                if best.get("confidence") == "high":
                    status = "external_document_verified"
                elif best.get("confidence") == "medium":
                    status = "external_candidate_found"
                else:
                    status = "requires_manual_review"

            for cand_dict in external_candidates:
                if cand_dict.get("discovery_provider") != "manufacturer_targeted":
                    continue
                if cand_dict.get("source_type") != "external_official":
                    continue

                url = cand_dict.get("url", "")
                if not url:
                    continue

                result = self.validator.validate_and_download(url, brand)

                record = DocumentRecord(
                    document_url=url,
                    product_name=product_name,
                    source=brand,
                    source_url=product_url,
                    document_type="technical_sheet",
                    title=cand_dict.get("title", ""),
                    supplier=manufacturer,
                    confidence=cand_dict.get("confidence", "medium"),
                    source_type=cand_dict.get("source_type", "external_official"),
                    evidence=f"Discovered via {cand_dict.get('discovery_provider', '')} from {cand_dict.get('domain', '')}; {cand_dict.get('evidence', '')}",
                    discovery_provider=cand_dict.get("discovery_provider"),
                    domain=cand_dict.get("domain"),
                    http_status=result.http_status,
                    content_type=result.content_type,
                    is_pdf=result.is_pdf,
                    downloadable=result.downloadable,
                    content_hash=result.content_hash,
                    file_path=result.file_path,
                    validation_error=result.error,
                    size_bytes=result.size_bytes,
                )

                self.deduplicator.register(record)
                external_records.append(record)

            recommended_action = self._recommend_action(
                missing_type, status, external_candidates
            )

            missing_item = MissingItem(
                product_name=product_name,
                brand=brand,
                product_url=product_url,
                missing_type=missing_type,
                original_source=original_source,
                original_document_url=original_doc_url,
                status=status,
                external_search_attempted=external_search_attempted,
                external_candidates=external_candidates,
                recommended_action=recommended_action,
            )
            missing_items.append(missing_item)

        return missing_items, external_records

    def _find_record_by_url(self, url: str, records: list[DocumentRecord]) -> DocumentRecord | None:
        if not url:
            return None
        normalized = self._normalize_url(url)
        for record in records:
            if self._normalize_url(record.document_url) == normalized:
                return record
        return None

    @staticmethod
    def _normalize_url(url: str) -> str:
        from urllib.parse import quote, urlparse
        parsed = urlparse(url)
        decoded_path = parsed.path
        for seq, char in (
            ("%20", " "), ("%21", "!"), ("%23", "#"), ("%24", "$"),
            ("%25", "%"), ("%26", "&"), ("%27", "'"), ("%28", "("),
            ("%29", ")"), ("%2B", "+"), ("%2C", ","), ("%3A", ":"),
            ("%3B", ";"), ("%3D", "="), ("%40", "@"), ("%5B", "["),
            ("%5D", "]"),
        ):
            decoded_path = decoded_path.replace(seq, char)
        encoded_path = quote(decoded_path, safe="/:")
        decoded_query = parsed.query
        for seq, char in (("%20", " "), ("%3D", "="), ("%26", "&")):
            decoded_query = decoded_query.replace(seq, char)
        encoded_query = quote(decoded_query, safe="=&")
        return urlparse(
            f"{parsed.scheme}://{parsed.netloc}{encoded_path}?{encoded_query}"
            if encoded_query
            else f"{parsed.scheme}://{parsed.netloc}{encoded_path}"
        ).geturl()

    def _is_relevant_candidate(
        self, candidate: SearchCandidate, product_name: str, model: Any, manufacturer: str | None = None
    ) -> bool:
        """Check if an external search candidate is relevant to the product."""
        candidate_text = (candidate.title + " " + candidate.evidence).lower()
        product_name_lower = product_name.lower()

        if not product_name:
            return True

        product_tokens = set(re.findall(r'\w+', product_name_lower))
        if not product_tokens:
            return False

        overlap = product_tokens & set(re.findall(r'\w+', candidate_text))
        if len(overlap) >= 2:
            return True

        if model and isinstance(model, str):
            model_lower = model.lower().strip()
            if model_lower and model_lower in candidate_text:
                return True

        if candidate.confidence == "high":
            return True

        if (
            (manufacturer == "GYPROC" or product_name.strip() in _GYPROC_ALIASES)
            and candidate.discovery_provider == "manufacturer_targeted"
            and candidate.source_type == "external_official"
            and candidate.domain in _VERIFIED_MANUFACTURER_DOMAINS.get("GYPROC", [])
            and is_gyproc_alias_match(candidate, product_name)
        ):
            return True

        return False

    def _recommend_action(
        self, missing_type: str, status: str, candidates: list[dict[str, Any]]
    ) -> str:
        if status == "external_document_verified":
            high_cands = [c for c in candidates if c.get("confidence") == "high"]
            if high_cands:
                return f"Download and index high-confidence external document from {high_cands[0].get('domain', 'unknown domain')}"
            return "Review external document before indexing"
        elif status == "external_candidate_found":
            return "Verify external document matches product before indexing"
        elif status == "requires_manual_review":
            return "Manual review required for low-confidence external candidate"
        elif status == "requires_ocr":
            return "Set up OCR engine (tesseract) to process this document"
        elif status == "unusable":
            return "Document cannot be recovered; mark product as having no technical documentation"
        elif status == "not_found":
            return "Contact manufacturer/supplier for technical documentation"
        elif status == "broken_link":
            return "Verify if document exists at new URL or replace with external source"
        return "Investigate and obtain technical documentation"

    def _index_documents(self, records: list[DocumentRecord]) -> None:
        """Index processed documents into Qdrant with deduplication."""
        if not self.embedding_provider or not self.vector_store:
            logger.warning("Embedding provider or vector store not configured; skipping indexing")
            return

        indexable = []
        for record in records:
            if record.duplicate_of:
                continue
            if not record.processed or not record.text_extractable:
                if not record.ocr_succeeded:
                    continue

            doc_dict = self._record_to_doc_dict(record)
            try:
                chunks = self.chunker.chunk(doc_dict, None)
            except Exception as exc:
                logger.error("Failed to chunk document %s: %s",
                             record.document_url, exc)
                continue

            seen_ids: set[str] = set()
            new_chunks = []
            for chunk in chunks:
                if chunk.chunk_id in self._indexed_chunk_ids or chunk.chunk_id in seen_ids:
                    continue
                seen_ids.add(chunk.chunk_id)
                new_chunks.append(chunk)

            if not new_chunks:
                continue

            texts = [c.text for c in new_chunks if c.text]
            if not texts:
                continue

            try:
                embeddings = self.embedding_provider.embed(texts)
            except Exception as exc:
                logger.error("Failed to generate embeddings for %s: %s",
                             record.document_url, exc)
                continue

            try:
                self.vector_store.upsert_chunks(new_chunks, embeddings)
            except Exception as exc:
                logger.error("Failed to upsert chunks for %s: %s",
                             record.document_url, exc)
                continue
            for chunk in new_chunks:
                self._indexed_chunk_ids.add(chunk.chunk_id)

            for chunk in new_chunks:
                record.chunk_count = max(record.chunk_count, chunk.chunk_index + 1)
            record.indexed = True

            logger.info("Indexed %d chunks for document %s", len(new_chunks), record.document_url)

        info = self.vector_store.collection_info()
        logger.info("Qdrant collection after indexing: %s", info)

    def _record_to_doc_dict(self, record: DocumentRecord) -> dict[str, Any]:
        content = ""
        if record.extracted_content:
            content = record.extracted_content
        elif record.file_path and Path(record.file_path).exists():
            processor = PdfProcessor(cleaner=self.cleaner, ocr_processor=self.ocr_processor)
            result = processor.extract(record.file_path)
            content = result.get("cleaned_text", "") or result.get("raw_text", "")
            if content:
                record.extracted_content = content

        return {
            "document_id": self._generate_document_id(record),
            "product_id": record.content_hash[:8] if record.content_hash else None,
            "product_name": record.product_name,
            "supplier": record.supplier,
            "source": record.source,
            "source_url": record.source_url,
            "document_url": record.document_url,
            "document_type": record.document_type,
            "language": "fr",
            "content": content,
            "content_hash": record.content_hash,
            "metadata": {
                "page_count": record.page_count or 1,
                "supplier": record.supplier,
                "product_name": record.product_name,
                "association_evidence": record.evidence,
                "source_type": record.source_type,
                "confidence": record.confidence,
                "discovery_provider": record.discovery_provider,
                "domain": record.domain,
            },
        }

    @staticmethod
    def _generate_document_id(record: DocumentRecord) -> str:
        source_id = hashlib.sha256(
            (record.document_url or "").encode("utf-8")
        ).hexdigest()[:16]
        return f"{record.source or 'unknown'}-{source_id}"

    def _compute_final_stats(
        self, records: list[DocumentRecord], products_by_brand: dict[str, list[dict[str, Any]]]
    ) -> dict[str, int]:
        classification = DocumentClassifier.summarize_classification(records)
        total_products = sum(len(p) for p in products_by_brand.values())
        products_with_docs = 0
        products_without_docs = 0
        for brand, products in products_by_brand.items():
            for p in products:
                if p.get("documents"):
                    products_with_docs += 1
                else:
                    products_without_docs += 1

        stats = {
            "total_products": total_products,
            "products_with_documents": products_with_docs,
            "products_without_documents": products_without_docs,
            "total_documents_discovered": len(records),
            "accessible_documents": classification.get("accessible", 0) + classification.get("text_extractable", 0),
            "broken_documents": classification.get("broken", 0) + classification.get("invalid", 0),
            "duplicate_documents": self.deduplicator.duplicate_count,
            "text_extractable_documents": classification.get("text_extractable", 0),
            "ocr_required_documents": classification.get("image_only", 0),
            "successfully_processed_documents": sum(1 for r in records if r.processed),
            "successfully_chunked_documents": sum(1 for r in records if r.chunk_count > 0),
            "successfully_embedded_documents": sum(1 for r in records if r.indexed),
            "successfully_indexed_chunks": sum(r.chunk_count for r in records if r.indexed),
            "products_without_technical_documentation": len(self.registry.get_items()),
            "external_official_documents": sum(1 for r in records if r.source_type == "external_official" and r.confidence in ("high", "medium")),
            "external_distributor_documents": sum(1 for r in records if r.source_type == "external_distributor" and r.confidence in ("high", "medium")),
            "external_sources_used": self._count_external_sources(records),
            "documents_requiring_manual_review": sum(1 for r in records if r.confidence and r.confidence.lower() == "low"),
        }
        return stats

    def _count_external_sources(self, records: list[DocumentRecord]) -> int:
        domains: set[str] = set()
        for record in records:
            if record.source_type and record.source_type != "official":
                parsed = urlparse(record.document_url or "")
                if parsed.netloc:
                    domains.add(parsed.netloc)
        return len(domains)
