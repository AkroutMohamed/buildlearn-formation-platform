from __future__ import annotations

from app.ai.acquisition.classifier import DocumentClassifier
from app.ai.acquisition.deduplicator import DocumentRecord


class TestDocumentClassifier:
    def test_classify_accessible_document(self):
        record = DocumentRecord(
            document_url="https://gypsobat.fr/doc.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=True,
            confidence="high",
        )
        assert DocumentClassifier.classify(record) == "accessible"

    def test_classify_broken_http_error(self):
        record = DocumentRecord(
            document_url="https://example.com/broken.pdf",
            source="gypsobat",
            source_type="official",
            http_status=404,
            is_pdf=False,
            downloadable=False,
            validation_error="HTTP 404",
        )
        assert DocumentClassifier.classify(record) == "broken"

    def test_classify_invalid_content_type(self):
        record = DocumentRecord(
            document_url="https://example.com/page.html",
            source="gypsobat",
            source_type="official",
            content_type="text/html",
            is_pdf=False,
            downloadable=False,
            validation_error="Unexpected Content-Type: text/html",
        )
        assert DocumentClassifier.classify(record) == "invalid"

    def test_classify_duplicate(self):
        record = DocumentRecord(
            document_url="https://example.com/dup.pdf",
            duplicate_of="https://canonical.com/doc.pdf",
            is_pdf=True,
            downloadable=True,
            confidence="high",
        )
        assert DocumentClassifier.classify(record) == "duplicate"

    def test_classify_image_only(self):
        record = DocumentRecord(
            document_url="https://example.com/image.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=True,
            ocr_required=True,
        )
        assert DocumentClassifier.classify(record) == "image_only"

    def test_classify_text_extractable(self):
        record = DocumentRecord(
            document_url="https://example.com/text.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=True,
            text_extractable=True,
            processed=True,
            confidence="high",
        )
        assert DocumentClassifier.classify(record) == "text_extractable"

    def test_classify_not_downloadable_broken(self):
        record = DocumentRecord(
            document_url="https://example.com/nodef.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=False,
        )
        assert DocumentClassifier.classify(record) == "broken"

    def test_summarize_classification(self):
        records = [
            DocumentRecord(document_url="u1", is_pdf=True, downloadable=True),
            DocumentRecord(document_url="u2", is_pdf=False, downloadable=False, http_status=404, validation_error="HTTP 404"),
            DocumentRecord(document_url="u3", duplicate_of="u1"),
        ]
        summary = DocumentClassifier.summarize_classification(records)
        assert summary["accessible"] == 1
        assert summary["broken"] == 1
        assert summary["duplicate"] == 1

    def test_should_index_high_confidence_accessible(self):
        record = DocumentRecord(
            document_url="https://gypsobat.fr/doc.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=True,
            confidence="high",
            text_extractable=True,
            processed=True,
        )
        assert DocumentClassifier.should_index(record) is True

    def test_should_index_medium_confidence(self):
        record = DocumentRecord(
            document_url="https://example.com/doc.pdf",
            source="external",
            source_type="distributor",
            is_pdf=True,
            downloadable=True,
            confidence="medium",
            text_extractable=True,
            processed=True,
        )
        assert DocumentClassifier.should_index(record) is True

    def test_should_index_low_confidence_excluded(self):
        record = DocumentRecord(
            document_url="https://example.com/doc.pdf",
            source="external",
            source_type="unknown",
            confidence="low",
        )
        assert DocumentClassifier.should_index(record) is False

    def test_should_index_broken_excluded(self):
        record = DocumentRecord(
            document_url="https://example.com/broken.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=False,
            downloadable=False,
            validation_error="HTTP 404",
            confidence="high",
        )
        assert DocumentClassifier.should_index(record) is False

    def test_should_index_image_only_without_ocr(self):
        record = DocumentRecord(
            document_url="https://example.com/image.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=True,
            confidence="high",
            ocr_required=True,
            ocr_succeeded=False,
        )
        assert DocumentClassifier.should_index(record) is False

    def test_should_index_image_only_with_ocr(self):
        record = DocumentRecord(
            document_url="https://example.com/image.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=True,
            confidence="high",
            ocr_required=True,
            ocr_attempted=True,
            ocr_succeeded=True,
            text_extractable=True,
            processed=True,
        )
        assert DocumentClassifier.should_index(record) is True
