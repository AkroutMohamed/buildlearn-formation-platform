from __future__ import annotations

import logging
from typing import Any

from app.ai.acquisition.deduplicator import DocumentRecord

logger = logging.getLogger(__name__)


class DocumentClassifier:
    """Classifies documents into categories based on validation and processing results.

    Classification values:
        - accessible: HTTP 200, correct content-type, valid PDF magic bytes
        - broken: HTTP error or missing content-type
        - invalid: Downloaded but content is not a valid PDF
        - duplicate: Same content hash as another document
        - image_only: PDF is valid but has no extractable text (OCR required)
        - text_extractable: PDF text was extracted successfully without OCR
    """

    @staticmethod
    def classify(record: DocumentRecord) -> str:
        """Return the primary classification for a document record."""
        if record.duplicate_of:
            return "duplicate"

        if not record.is_pdf or record.validation_error:
            if record.http_status and record.http_status != 200:
                return "broken"
            if record.content_type and "pdf" not in record.content_type.lower():
                return "invalid"
            if record.validation_error and "magic" in record.validation_error.lower():
                return "invalid"
            if record.validation_error:
                return "broken"
            return "invalid"

        if not record.downloadable:
            return "broken"

        if record.ocr_required:
            return "image_only"

        if record.text_extractable or record.processed:
            return "text_extractable"

        return "accessible"

    @staticmethod
    def summarize_classification(records: list[DocumentRecord]) -> dict[str, int]:
        counts: dict[str, int] = {
            "accessible": 0,
            "broken": 0,
            "invalid": 0,
            "duplicate": 0,
            "image_only": 0,
            "text_extractable": 0,
        }
        for record in records:
            label = DocumentClassifier.classify(record)
            counts[label] = counts.get(label, 0) + 1
        return counts

    @staticmethod
    def should_index(record: DocumentRecord) -> bool:
        """Determine whether a document should be indexed into Qdrant.

        Only HIGH and MEDIUM confidence documents that are accessible
        and text-extractable (or OCR-succeeded) should be indexed.
        LOW confidence documents go to the missing-documents report.
        """
        if record.duplicate_of and not record.text_extractable and not record.processed:
            return False

        if record.confidence and record.confidence.lower() == "low":
            return False

        classification = DocumentClassifier.classify(record)
        if classification in ("broken", "invalid", "duplicate"):
            return False

        if classification == "image_only":
            return record.ocr_succeeded

        return record.text_extractable or record.processed
