from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.ai.acquisition.deduplicator import DocumentRecord
from app.ai.acquisition.classifier import DocumentClassifier
from app.ai.acquisition.registry_builder import MissingDataRegistry
from app.ai.acquisition.manifest_builder import DatasetManifest
from app.ai.config import DOCS_AI_DIR

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates the human-readable DATA_ACQUISITION_REPORT.md.

    Output: docs/ai/DATA_ACQUISITION_REPORT.md
    """

    DEFAULT_PATH = DOCS_AI_DIR / "DATA_ACQUISITION_REPORT.md"

    def __init__(self, output_path: str | Path | None = None) -> None:
        self._output_path = Path(output_path) if output_path else self.DEFAULT_PATH

    def generate(
        self,
        products_by_brand: dict[str, list[dict[str, Any]]],
        document_records: list[DocumentRecord],
        missing_registry: MissingDataRegistry,
        manifest: DatasetManifest,
    ) -> str:
        self._output_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        now = datetime.now(timezone.utc).isoformat()

        lines.append("# BuildLearn AI — Data Acquisition Report")
        lines.append("")
        lines.append(f"**Generated:** {now}")
        lines.append(f"**Pipeline version:** {manifest._pipeline_version or '6.5.0'}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Summary statistics
        lines.append("## Summary")
        lines.append("")
        summary = manifest._brands
        lines.append("| Brand | Products | With Docs | Without Docs | Documents | Accessible | Broken | Duplicates | OCR Required | Indexed Chunks |")
        lines.append("|-------|----------|-----------|--------------|-----------|------------|--------|------------|--------------|----------------|")
        for brand, stats in summary.items():
            d = stats.to_dict()
            lines.append(
                f"| {d['source']} | {d['total_products']} | {d['products_with_documents']} | "
                f"{d['products_without_documents']} | {d['total_documents_discovered']} | "
                f"{d['accessible_documents']} | {d['broken_documents']} | "
                f"{d['duplicate_documents']} | {d['ocr_required_documents']} | "
                f"{d['successfully_indexed_chunks']} |"
            )
        lines.append("")

        # Classification breakdown
        classification = DocumentClassifier.summarize_classification(document_records)
        lines.append("## Document Classification Breakdown")
        lines.append("")
        lines.append("| Classification | Count |")
        lines.append("|---------------|-------|")
        for label, count in classification.items():
            lines.append(f"| {label} | {count} |")
        lines.append("")

        # Missing documents table
        missing_items = missing_registry.get_items()
        if missing_items:
            lines.append("## Products Without Usable Technical Documents")
            lines.append("")
            lines.append("| Brand | Product | Product URL | Problem | Search Performed | External Candidate | Confidence | Action |")
            lines.append("|-------|---------|-------------|---------|------------------|---------------------|------------|--------|")
            for item in missing_items:
                candidates_str = ""
                if item.external_candidates:
                    for cand in item.external_candidates[:3]:
                        candidates_str += f"- `[{cand.get('confidence','')}] {cand.get('title','')} ({cand.get('domain','')}) `"
                    if len(item.external_candidates) > 3:
                        candidates_str += f"... +{len(item.external_candidates) - 3} more"
                else:
                    candidates_str = "None"

                search_performed = "Yes" if item.external_search_attempted else "No"
                product_url = item.product_url or "N/A"
                if len(product_url) > 60:
                    product_url = product_url[:57] + "..."

                lines.append(
                    f"| {item.brand} | {item.product_name} | {product_url} | "
                    f"{item.missing_type} ({item.status}) | {search_performed} | "
                    f"{candidates_str} | {item.external_candidates[0].get('confidence','N/A') if item.external_candidates else 'N/A'} | "
                    f"{_truncate(item.recommended_action, 50)} |"
                )
            lines.append("")

        # Successfully processed products
        processed = [r for r in document_records if r.processed and not r.duplicate_of]
        lines.append("### Successfully Processed Products")
        lines.append("")
        if processed:
            lines.append("| Brand | Product | Document | Pages | Chunks | Indexed |")
            lines.append("|-------|---------|----------|-------|--------|---------|")
            for record in processed:
                brand = record.supplier or record.source or "Unknown"
                product_name = record.product_name or "N/A"
                doc_url = record.document_url or "N/A"
                if len(doc_url) > 50:
                    doc_url = doc_url[:47] + "..."
                lines.append(
                    f"| {brand} | {product_name} | {doc_url} | "
                    f"{record.page_count or '-'} | {record.chunk_count} | "
                    f"{'Yes' if record.indexed else 'No'} |"
                )
        else:
            lines.append("No documents have been successfully processed yet.")
        lines.append("")

        # Broken official documents
        broken = [r for r in document_records
                  if DocumentClassifier.classify(r) in ("broken", "invalid")
                  and r.source_type == "official"]
        lines.append("### Products with Broken Official Documents")
        lines.append("")
        if broken:
            lines.append("| Brand | Product | Document URL | Error |")
            lines.append("|-------|---------|-------------|-------|")
            for record in broken:
                brand = record.supplier or record.source or "Unknown"
                product_name = record.product_name or "N/A"
                lines.append(
                    f"| {brand} | {product_name} | {record.document_url} | "
                    f"{record.validation_error or 'N/A'} |"
                )
        else:
            lines.append("No broken official documents found.")
        lines.append("")

        # Products with no documents found
        no_docs_items = [item for item in missing_items if item.missing_type == "technical_document" and item.status == "not_found"]
        lines.append("### Products with No Documents Found")
        lines.append("")
        if no_docs_items:
            lines.append("| Brand | Product | Product URL |")
            lines.append("|-------|---------|-------------|")
            for item in no_docs_items:
                lines.append(f"| {item.brand} | {item.product_name} | {item.product_url or 'N/A'} |")
        else:
            lines.append("All products have at least one document candidate.")
        lines.append("")

        # External official documents
        ext_official = [r for r in document_records
                        if r.source_type == "external_official"
                        and r.confidence in ("high", "medium")]
        lines.append("### Products with External Official Documents")
        lines.append("")
        if ext_official:
            lines.append("| Brand | Product | Document URL | Confidence | Evidence |")
            lines.append("|-------|---------|-------------|------------|----------|")
            for record in ext_official:
                brand = record.supplier or record.source or "Unknown"
                product_name = record.product_name or "N/A"
                lines.append(
                    f"| {brand} | {product_name} | {record.document_url or 'N/A'} | "
                    f"{record.confidence or 'N/A'} | {_truncate(record.evidence or 'N/A', 80)} |"
                )
        else:
            lines.append("No external official documents found.")
        lines.append("")

        # Distributor documents
        ext_distributor = [r for r in document_records
                           if r.source_type == "external_distributor"
                           and r.confidence in ("high", "medium")]
        lines.append("### Products with Distributor Documents")
        lines.append("")
        if ext_distributor:
            lines.append("| Brand | Product | Document URL | Confidence | Evidence |")
            lines.append("|-------|---------|-------------|------------|----------|")
            for record in ext_distributor:
                brand = record.supplier or record.source or "Unknown"
                product_name = record.product_name or "N/A"
                lines.append(
                    f"| {brand} | {product_name} | {record.document_url or 'N/A'} | "
                    f"{record.confidence or 'N/A'} | {_truncate(record.evidence or 'N/A', 80)} |"
                )
        else:
            lines.append("No distributor documents found.")
        lines.append("")

        # OCR documents
        ocr_docs = [r for r in document_records if r.ocr_required or (r.ocr_attempted and r.ocr_succeeded)]
        lines.append("### Documents Requiring OCR")
        lines.append("")
        if ocr_docs:
            lines.append("| Brand | Product | Document | OCR Attempted | OCR Succeeded | Error |")
            lines.append("|-------|---------|----------|---------------|---------------|-------|")
            for record in ocr_docs:
                brand = record.supplier or record.source or "Unknown"
                product_name = record.product_name or "N/A"
                doc_url = record.document_url or "N/A"
                if len(doc_url) > 50:
                    doc_url = doc_url[:47] + "..."
                lines.append(
                    f"| {brand} | {product_name} | {doc_url} | "
                    f"{'Yes' if record.ocr_attempted else 'No'} | "
                    f"{'Yes' if record.ocr_succeeded else 'No'} | "
                    f"{record.ocr_error or 'N/A'} |"
                )
        else:
            lines.append("No documents required OCR.")
        lines.append("")

        # Duplicate documents
        duplicates = [r for r in document_records if r.duplicate_of]
        lines.append("### Duplicate Documents")
        lines.append("")
        if duplicates:
            lines.append("| Canonical URL | Duplicate URL | Content Hash |")
            lines.append("|----------------|---------------|--------------|")
            for record in duplicates:
                lines.append(
                    f"| {record.canonical_url or 'N/A'} | {record.document_url or 'N/A'} | "
                    f"{record.content_hash or 'N/A'} |"
                )
        else:
            lines.append("No duplicate documents found.")
        lines.append("")

        # External sources used
        lines.append("### External Sources Used")
        lines.append("")
        ext_sources = set()
        for record in document_records:
            if record.source_type and record.source_type != "official":
                domain = _extract_domain(record.document_url or "")
                if domain:
                    ext_sources.add(domain)
        for item in missing_items:
            for cand in item.external_candidates:
                domain = cand.get("domain", "")
                if domain:
                    ext_sources.add(domain)

        if ext_sources:
            lines.append("| Domain |")
            lines.append("|--------|")
            for source in sorted(ext_sources):
                lines.append(f"| {source} |")
        else:
            lines.append("No external sources were used.")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## Known Limitations")
        lines.append("")
        lines.append("1. EMTOP product pages typically do not include direct PDF technical document downloads on the product page itself.")
        lines.append("   Technical documents for EMTOP products are only available in the general catalogue or via external search.")
        lines.append("2. SOFAP product pages include PDF download links, but the WordPress REST API content field may be empty.")
        lines.append("3. External search results are classified by domain trust level. LOW-confidence candidates are not indexed automatically.")
        lines.append("4. OCR processing depends on local tesseract installation. Image-only PDFs without OCR will remain unprocessed.")
        lines.append("5. Re-running the pipeline will not create duplicate vectors due to deterministic chunk IDs and SHA-256 deduplication.")
        lines.append("6. Documents discovered from Gypsobat documentation pages that reference SOFAP, SIPS, GYPROC, SINIAT, or TACER products")
        lines.append("   are attributed to their actual supplier, not to Gypsobat.")
        lines.append("")

        content = "\n".join(lines)
        self._output_path.write_text(content, encoding="utf-8")
        logger.info("Report generated at %s", self._output_path)
        return str(self._output_path)


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def _extract_domain(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc
