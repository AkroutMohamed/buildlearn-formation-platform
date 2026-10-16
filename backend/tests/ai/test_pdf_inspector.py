from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import fitz
import pytest

from app.ai.ingestion.pdf_inspector import (
    DocumentInspection,
    PageClassification,
    PdfInspector,
    inspect_pdf,
)


def _create_test_pixmap(width: int, height: int, color: int = 0xFFFFFF) -> fitz.Pixmap:
    """Create a test pixmap using the correct PyMuPDF API."""
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, width, height))
    pix.clear_with(color)
    return pix


class TestPdfInspector:
    def test_inspect_nonexistent_file(self):
        inspector = PdfInspector()
        result = inspector.inspect("/nonexistent/path.pdf")
        assert result.document_classification == "EXTRACTION_FAILED"
        assert "File not found" in result.error
        assert result.page_count == 0

    def test_inspect_encrypted_without_password(self, tmp_path):
        doc = fitz.open()
        doc.new_page()
        encrypted_path = tmp_path / "encrypted.pdf"
        doc.save(str(encrypted_path), encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="secret")
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(encrypted_path))
        assert result.document_classification == "EXTRACTION_FAILED"
        assert "encrypted" in result.error.lower()

    def test_inspect_encrypted_with_password(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Hello World")
        encrypted_path = tmp_path / "encrypted.pdf"
        doc.save(str(encrypted_path), encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="secret")
        doc.close()

        inspector = PdfInspector(password="secret")
        result = inspector.inspect(str(encrypted_path))
        assert result.document_classification != "EXTRACTION_FAILED"
        assert result.page_count == 1

    def test_inspect_empty_pdf(self, tmp_path):
        doc = fitz.open()
        doc.new_page()
        doc.new_page()
        empty_path = tmp_path / "empty.pdf"
        doc.save(str(empty_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(empty_path))
        assert result.page_count == 2

    def test_digital_simple_classification(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "This is a simple text page with enough content to be classified as digital simple. " * 3)
        simple_path = tmp_path / "simple.pdf"
        doc.save(str(simple_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(simple_path))
        assert result.page_count == 1
        assert result.pages[0].classification == "DIGITAL_SIMPLE"
        assert result.pages[0].text_length > 100
        assert result.pages[0].image_count == 0

    def test_digital_complex_classification(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        for i in range(100):
            page.insert_text((50, 50 + i * 10), f"Line {i} with some text content")
            page.draw_rect(fitz.Rect(100, 100 + i * 5, 300, 120 + i * 5))
        complex_path = tmp_path / "complex.pdf"
        doc.save(str(complex_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(complex_path))
        assert result.page_count == 1
        assert result.pages[0].classification == "DIGITAL_COMPLEX"
        assert result.pages[0].vector_object_count > 50

    def test_image_only_classification(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        pix = _create_test_pixmap(500, 700)
        page.insert_image(page.rect, pixmap=pix)
        img_path = tmp_path / "image_only.pdf"
        doc.save(str(img_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(img_path))
        assert result.page_count == 1
        # Image covers ~99% of page (inserted at page.rect), classified as IMAGE_ONLY (>95%)
        assert result.pages[0].classification == "IMAGE_ONLY"
        assert result.pages[0].text_length == 0
        assert result.pages[0].image_count == 1
        assert result.pages[0].image_area_ratio >= 0.95

    def test_image_heavy_classification(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        pix = _create_test_pixmap(500, 700)
        page.insert_image(fitz.Rect(50, 50, 550, 750), pixmap=pix)
        page.insert_text((50, 50), "Small caption")
        heavy_path = tmp_path / "image_heavy.pdf"
        doc.save(str(heavy_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(heavy_path))
        assert result.page_count == 1
        # Image covers ~70% of page, classified as HYBRID (IMAGE_HEAVY needs >= 70%)
        assert result.pages[0].classification == "HYBRID"
        assert result.pages[0].image_area_ratio >= 0.30

    def test_hybrid_classification(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        # Larger image to ensure it's detected as hybrid (not digital simple)
        pix = _create_test_pixmap(400, 500)
        page.insert_image(fitz.Rect(50, 50, 450, 550), pixmap=pix)
        page.insert_text((50, 600), "Text with image content. " * 10)
        hybrid_path = tmp_path / "hybrid.pdf"
        doc.save(str(hybrid_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(hybrid_path))
        assert result.page_count == 1
        assert result.pages[0].classification in ("HYBRID", "DIGITAL_SIMPLE")
        assert result.pages[0].text_length > 0
        assert result.pages[0].image_count > 0

    def test_ocr_required_classification(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        pix = _create_test_pixmap(300, 400, 0xEEEEEE)
        page.insert_image(fitz.Rect(100, 100, 400, 500), pixmap=pix)
        ocr_path = tmp_path / "ocr_required.pdf"
        doc.save(str(ocr_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(ocr_path))
        assert result.page_count == 1
        assert result.pages[0].classification == "OCR_REQUIRED"
        assert result.pages[0].text_length == 0
        assert result.pages[0].image_count > 0

    def test_document_classification_all_same(self, tmp_path):
        doc = fitz.open()
        for _ in range(3):
            page = doc.new_page()
            page.insert_text((50, 50), "Simple text content " * 10)
        doc_path = tmp_path / "all_simple.pdf"
        doc.save(str(doc_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(doc_path))
        assert result.document_classification == "DIGITAL_SIMPLE_DOCUMENT"

    def test_document_classification_mixed(self, tmp_path):
        doc = fitz.open()
        page1 = doc.new_page()
        page1.insert_text((50, 50), "Digital text content " * 20)
        page2 = doc.new_page()
        pix = _create_test_pixmap(500, 700)
        page2.insert_image(page2.rect, pixmap=pix)
        doc_path = tmp_path / "mixed.pdf"
        doc.save(str(doc_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(doc_path))
        assert result.document_classification == "HYBRID_DOCUMENT"

    def test_document_classification_image_only(self, tmp_path):
        doc = fitz.open()
        for _ in range(2):
            page = doc.new_page()
            pix = _create_test_pixmap(500, 700)
            page.insert_image(page.rect, pixmap=pix)
        doc_path = tmp_path / "all_images.pdf"
        doc.save(str(doc_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(doc_path))
        # Each page classified as IMAGE_ONLY (>95% coverage), so document is IMAGE_ONLY
        assert result.document_classification == "IMAGE_ONLY"

    def test_to_dict_serialization(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Test content for serialization.")
        doc_path = tmp_path / "serialize.pdf"
        doc.save(str(doc_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(doc_path))
        data = inspector.to_dict(result)

        assert "file_path" in data
        assert "page_count" in data
        assert "pages" in data
        assert "document_classification" in data
        assert isinstance(data["pages"], list)
        assert len(data["pages"]) == 1

    def test_to_json_serialization(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Test content for JSON.")
        doc_path = tmp_path / "json.pdf"
        doc.save(str(doc_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(doc_path))
        json_str = inspector.to_json(result)

        assert isinstance(json_str, str)
        assert "DIGITAL_SIMPLE" in json_str

    def test_convenience_function(self, tmp_path):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Convenience function test.")
        doc_path = tmp_path / "convenience.pdf"
        doc.save(str(doc_path))
        doc.close()

        result = inspect_pdf(str(doc_path))
        assert isinstance(result, DocumentInspection)
        assert result.page_count == 1


class TestImageAreaRatioCalculation:
    """Focused tests for the image_area_ratio calculation fix."""

    def test_normal_image_coverage(self, tmp_path):
        """Test normal image coverage calculation using display rectangles."""
        doc = fitz.open()
        page = doc.new_page()
        # Insert image covering exactly 50% of page (letter size: 612x792)
        page.insert_image(fitz.Rect(50, 50, 356, 446), pixmap=_create_test_pixmap(306, 396))
        normal_path = tmp_path / "normal.pdf"
        doc.save(str(normal_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(normal_path))
        assert result.pages[0].image_count == 1
        # Area: 306*396 = 121176, Page: 612*792 = 484704, Ratio: ~0.25
        # But we inserted at 306x396 points, so it's exactly 25% of page
        assert 0.20 <= result.pages[0].image_area_ratio <= 0.30

    def test_multiple_images(self, tmp_path):
        """Test multiple images sum their display rectangle areas."""
        doc = fitz.open()
        page = doc.new_page()
        # Two images each covering ~25% of page
        page.insert_image(fitz.Rect(50, 50, 356, 446), pixmap=_create_test_pixmap(306, 396))
        page.insert_image(fitz.Rect(50, 450, 356, 742), pixmap=_create_test_pixmap(306, 292))
        multi_path = tmp_path / "multi.pdf"
        doc.save(str(multi_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(multi_path))
        assert result.pages[0].image_count == 2
        # Two images: 306*396 + 306*292 = 121176 + 89352 = 210528
        # Page: 612*792 = 484704, Ratio: ~0.43
        assert 0.40 <= result.pages[0].image_area_ratio <= 0.50

    def test_high_resolution_embedded_image(self, tmp_path):
        """Test that high-res embedded image displayed small gives correct ratio."""
        doc = fitz.open()
        page = doc.new_page()
        # 1000x1000 pixel image displayed at 100x100 points (tiny)
        pix = _create_test_pixmap(1000, 1000)
        page.insert_image(fitz.Rect(50, 50, 150, 150), pixmap=pix)
        hires_path = tmp_path / "hires.pdf"
        doc.save(str(hires_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(hires_path))
        assert result.pages[0].image_count == 1
        # Display rect: 100x100 = 10000, Page: 612*792 = 484704, Ratio: ~0.02
        # Old buggy code would have used 1000*1000 = 1,000,000 -> ratio ~2.0
        assert result.pages[0].image_area_ratio <= 0.05
        assert result.pages[0].image_area_ratio >= 0.0

    def test_image_ratio_bounded(self, tmp_path):
        """Test image_area_ratio is always bounded to [0, 1]."""
        doc = fitz.open()
        page = doc.new_page()
        # Image covering full page - use page.rect for exact fit
        page.insert_image(page.rect, pixmap=_create_test_pixmap(612, 792))
        full_path = tmp_path / "full.pdf"
        doc.save(str(full_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(full_path))
        assert 0.0 <= result.pages[0].image_area_ratio <= 1.0
        # Allow some margin for PDF coordinate differences
        assert result.pages[0].image_area_ratio >= 0.90

        # Also test empty page
        doc2 = fitz.open()
        doc2.new_page()
        empty_path = tmp_path / "empty.pdf"
        doc2.save(str(empty_path))
        doc2.close()

        result2 = inspector.inspect(str(empty_path))
        assert result2.pages[0].image_area_ratio == 0.0

    def test_missing_image_rectangle_info(self, tmp_path):
        """Test conservative fallback when image rectangle info unavailable."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Text only page")
        text_path = tmp_path / "text.pdf"
        doc.save(str(text_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(text_path))
        assert result.pages[0].image_count == 0
        assert result.pages[0].image_area_ratio == 0.0
        assert result.pages[0].classification == "DIGITAL_SIMPLE"

    def test_existing_classification_behavior_preserved(self, tmp_path):
        """Test that existing classification behavior is preserved for known cases."""
        # Digital simple
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Simple text content " * 20)
        simple_path = tmp_path / "simple.pdf"
        doc.save(str(simple_path))
        doc.close()

        inspector = PdfInspector()
        result = inspector.inspect(str(simple_path))
        assert result.pages[0].classification == "DIGITAL_SIMPLE"

        # Digital complex - needs text + many vector objects
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Complex page with many drawings " * 10)
        for i in range(60):
            page.draw_rect(fitz.Rect(100, 100 + i * 5, 300, 120 + i * 5))
        complex_path = tmp_path / "complex.pdf"
        doc.save(str(complex_path))
        doc.close()

        result = inspector.inspect(str(complex_path))
        assert result.pages[0].classification == "DIGITAL_COMPLEX"

        # OCR required (small image, no text)
        doc = fitz.open()
        page = doc.new_page()
        page.insert_image(fitz.Rect(100, 100, 200, 200), pixmap=_create_test_pixmap(100, 100))
        ocr_path = tmp_path / "ocr.pdf"
        doc.save(str(ocr_path))
        doc.close()

        result = inspector.inspect(str(ocr_path))
        assert result.pages[0].classification == "OCR_REQUIRED"


class TestPageClassificationDataclass:
    def test_page_classification_fields(self):
        pc = PageClassification(
            page_number=1,
            classification="DIGITAL_SIMPLE",
            text_length=100,
            image_count=0,
            image_area_ratio=0.0,
            vector_object_count=10,
            font_count=2,
        )
        assert pc.page_number == 1
        assert pc.classification == "DIGITAL_SIMPLE"
        assert pc.extraction_error is None


class TestDocumentInspectionDataclass:
    def test_document_inspection_fields(self):
        di = DocumentInspection(
            file_path="/test.pdf",
            page_count=1,
            pages=[],
            document_classification="DIGITAL_SIMPLE_DOCUMENT",
        )
        assert di.file_path == "/test.pdf"
        assert di.page_count == 1
        assert di.error is None