from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.ai.acquisition.deduplicator import DocumentDeduplicator
from app.ai.acquisition.classifier import DocumentClassifier
from app.ai.config import AI_REPORTS_DIR

logger = logging.getLogger(__name__)


@dataclass
class BrandStats:
    source: str = ""
    total_products: int = 0
    products_with_documents: int = 0
    products_without_documents: int = 0
    total_documents_discovered: int = 0
    accessible_documents: int = 0
    broken_documents: int = 0
    duplicate_documents: int = 0
    text_extractable_documents: int = 0
    ocr_required_documents: int = 0
    successfully_processed_documents: int = 0
    successfully_chunked_documents: int = 0
    successfully_embedded_documents: int = 0
    successfully_indexed_chunks: int = 0
    external_official_documents: int = 0
    external_distributor_documents: int = 0
    low_confidence_candidates: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "total_products": self.total_products,
            "products_with_documents": self.products_with_documents,
            "products_without_documents": self.products_without_documents,
            "total_documents_discovered": self.total_documents_discovered,
            "accessible_documents": self.accessible_documents,
            "broken_documents": self.broken_documents,
            "duplicate_documents": self.duplicate_documents,
            "text_extractable_documents": self.text_extractable_documents,
            "ocr_required_documents": self.ocr_required_documents,
            "successfully_processed_documents": self.successfully_processed_documents,
            "successfully_chunked_documents": self.successfully_chunked_documents,
            "successfully_embedded_documents": self.successfully_embedded_documents,
            "successfully_indexed_chunks": self.successfully_indexed_chunks,
            "external_official_documents": self.external_official_documents,
            "external_distributor_documents": self.external_distributor_documents,
            "low_confidence_candidates": self.low_confidence_candidates,
        }


class DatasetManifest:
    """Builds and persists the dataset manifest.

    Output: backend/ai_data/reports/dataset_manifest.json
    """

    REPORT_DIR = AI_REPORTS_DIR

    def __init__(self) -> None:
        self.REPORT_DIR.mkdir(parents=True, exist_ok=True)
        self._brands: dict[str, BrandStats] = {}
        self._source_urls: list[str] = []
        self._pipeline_version: str = "6.5.0"

    def get_brand_stats(self, brand: str) -> BrandStats:
        if brand not in self._brands:
            self._brands[brand] = BrandStats(source=brand)
        return self._brands[brand]

    def set_source_urls(self, urls: list[str]) -> None:
        self._source_urls = list(urls)

    def set_pipeline_version(self, version: str) -> None:
        self._pipeline_version = version

    def build_from_records(
        self,
        brand: str,
        total_products: int,
        products: list[dict[str, Any]],
        records: list[Any],
        deduplicator: DocumentDeduplicator,
    ) -> None:
        """Populate brand stats from product list and document records."""
        stats = self.get_brand_stats(brand)
        stats.total_products = total_products

        products_with_docs = 0
        for product in products:
            docs = product.get("documents", [])
            if docs:
                products_with_docs += 1
        stats.products_with_documents = products_with_docs
        stats.products_without_documents = total_products - products_with_docs

        classification = DocumentClassifier.summarize_classification(records) if records else {}

        stats.total_documents_discovered = len(records)
        stats.accessible_documents = classification.get("accessible", 0)
        stats.broken_documents = classification.get("broken", 0)
        stats.duplicate_documents = classification.get("duplicate", 0)
        stats.text_extractable_documents = classification.get("text_extractable", 0)
        stats.ocr_required_documents = classification.get("image_only", 0)

        stats.successfully_processed_documents = sum(1 for r in records if r.processed)
        stats.successfully_chunked_documents = sum(1 for r in records if r.chunk_count > 0)
        stats.successfully_embedded_documents = sum(1 for r in records if r.indexed)
        stats.successfully_indexed_chunks = sum(r.chunk_count for r in records if r.indexed)

        stats.duplicate_documents = deduplicator.duplicate_count

        for record in records:
            if record.source_type == "external_official":
                stats.external_official_documents += 1
            elif record.source_type == "external_distributor":
                stats.external_distributor_documents += 1
            if record.confidence and record.confidence.lower() == "low":
                stats.low_confidence_candidates += 1

    def save(self, path: str | Path | None = None) -> str:
        target = Path(path) if path else self.REPORT_DIR / "dataset_manifest.json"
        target.parent.mkdir(parents=True, exist_ok=True)

        brand_totals = {b: s.to_dict() for b, s in self._brands.items()}

        total_products = sum(s.total_products for s in self._brands.values())
        products_with_docs = sum(s.products_with_documents for s in self._brands.values())
        products_without_docs = sum(s.products_without_documents for s in self._brands.values())
        total_docs = sum(s.total_documents_discovered for s in self._brands.values())
        accessible = sum(s.accessible_documents for s in self._brands.values())
        broken = sum(s.broken_documents for s in self._brands.values())
        duplicates = sum(s.duplicate_documents for s in self._brands.values())
        text_extractable = sum(s.text_extractable_documents for s in self._brands.values())
        ocr_required = sum(s.ocr_required_documents for s in self._brands.values())
        processed = sum(s.successfully_processed_documents for s in self._brands.values())
        chunked = sum(s.successfully_chunked_documents for s in self._brands.values())
        embedded = sum(s.successfully_embedded_documents for s in self._brands.values())
        indexed = sum(s.successfully_indexed_chunks for s in self._brands.values())

        payload = {
            "pipeline_version": self._pipeline_version,
            "last_run": datetime.now(timezone.utc).isoformat(),
            "source_urls": self._source_urls,
            "summary": {
                "total_products": total_products,
                "products_with_documents": products_with_docs,
                "products_without_documents": products_without_docs,
                "total_documents_discovered": total_docs,
                "accessible_documents": accessible,
                "broken_documents": broken,
                "duplicate_documents": duplicates,
                "text_extractable_documents": text_extractable,
                "ocr_required_documents": ocr_required,
                "successfully_processed_documents": processed,
                "successfully_chunked_documents": chunked,
                "successfully_embedded_documents": embedded,
                "successfully_indexed_chunks": indexed,
            },
            "brands": brand_totals,
        }

        with open(target, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)

        logger.info("Dataset manifest saved to %s", target)
        return str(target)
