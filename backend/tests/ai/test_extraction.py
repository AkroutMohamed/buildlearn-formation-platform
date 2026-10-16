from __future__ import annotations

from dataclasses import asdict

import pytest

from app.ai.extraction.base import (
    ExtractionBackend,
    ExtractionFailedError,
    ExtractionResult,
    UnsupportedBackendError,
)
from app.ai.extraction.layout_backend import LayoutBackend
from app.ai.extraction.ocr_backend import OCRBackend
from app.ai.extraction.pymupdf_backend import PyMuPDFBackend
from app.ai.extraction.router import (
    ExtractionRouter,
    route_classification,
    route_page,
)
from app.ai.ingestion.pdf_inspector import PageClassification


class DummyBackend(ExtractionBackend):
    @property
    def name(self) -> str:
        return "dummy"

    def extract_page(self, file_path: str, page_number: int) -> ExtractionResult:
        return ExtractionResult(
            page_number=page_number,
            content=f"dummy page {page_number}",
            backend_name=self.name,
            success=True,
        )


class TestExtractionResult:
    def test_default_fields(self):
        result = ExtractionResult(page_number=1, content="hello")
        assert result.page_number == 1
        assert result.content == "hello"
        assert result.metadata == {}
        assert result.warnings == []
        assert result.errors == []
        assert result.backend_name == ""
        assert result.success is True

    def test_custom_fields(self):
        result = ExtractionResult(
            page_number=2,
            content="text",
            metadata={"key": "val"},
            warnings=["warn"],
            errors=["err"],
            backend_name="test",
            success=False,
        )
        assert result.page_number == 2
        assert result.content == "text"
        assert result.metadata == {"key": "val"}
        assert result.warnings == ["warn"]
        assert result.errors == ["err"]
        assert result.backend_name == "test"
        assert result.success is False

    def test_serializable(self):
        result = ExtractionResult(page_number=1, content="hi", backend_name="x")
        d = asdict(result)
        assert d["page_number"] == 1
        assert d["content"] == "hi"
        assert isinstance(d["warnings"], list)
        assert isinstance(d["errors"], list)


class TestExtractionBackendAbstract:
    def test_cannot_instantiate_without_impl(self):
        with pytest.raises(TypeError):
            ExtractionBackend()  # type: ignore[abstract]

    def test_subclass_must_implement_name(self):
        class Bad(ExtractionBackend):
            def extract_page(self, file_path: str, page_number: int) -> ExtractionResult:
                return ExtractionResult(page_number=page_number, content="")

        with pytest.raises(TypeError):
            Bad()

    def test_subclass_must_implement_extract_page(self):
        class Bad(ExtractionBackend):
            @property
            def name(self) -> str:
                return "bad"

        with pytest.raises(TypeError):
            Bad()

    def test_concrete_subclass_works(self):
        backend = DummyBackend()
        assert backend.name == "dummy"
        result = backend.extract_page("test.pdf", 1)
        assert result.success is True
        assert result.content == "dummy page 1"


class TestPyMuPDFBackend:
    def test_backend_name(self):
        backend = PyMuPDFBackend()
        assert backend.name == "pymupdf"

    def test_extract_page_digital_simple(self, tmp_path):
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "This is test content for extraction.")
        pdf_path = tmp_path / "test.pdf"
        doc.save(str(pdf_path))
        doc.close()

        backend = PyMuPDFBackend()
        result = backend.extract_page(str(pdf_path), 1)
        assert result.success is True
        assert "test content" in result.content.lower()
        assert result.backend_name == "pymupdf"
        assert result.metadata["text_length"] > 0

    def test_extract_page_out_of_range(self, tmp_path):
        import fitz
        doc = fitz.open()
        doc.new_page()
        pdf_path = tmp_path / "test.pdf"
        doc.save(str(pdf_path))
        doc.close()

        backend = PyMuPDFBackend()
        result = backend.extract_page(str(pdf_path), 5)
        assert result.success is False
        assert len(result.errors) > 0

    def test_extract_page_encrypted_no_password(self, tmp_path):
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Secret text")
        pdf_path = tmp_path / "encrypted.pdf"
        doc.save(str(pdf_path), encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="secret")
        doc.close()

        backend = PyMuPDFBackend()
        result = backend.extract_page(str(pdf_path), 1)
        assert result.success is False
        assert any("encrypted" in e.lower() for e in result.errors)

    def test_extract_page_encrypted_with_password(self, tmp_path):
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Secret text")
        pdf_path = tmp_path / "encrypted.pdf"
        doc.save(str(pdf_path), encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="secret")
        doc.close()

        backend = PyMuPDFBackend(password="secret")
        result = backend.extract_page(str(pdf_path), 1)
        assert result.success is True
        assert "secret text" in result.content.lower()


class TestOCRBackend:
    def test_backend_name(self):
        backend = OCRBackend()
        assert backend.name == "ocr"

    def test_is_unavailable_placeholder(self):
        backend = OCRBackend()
        result = backend.extract_page("any.pdf", 1)
        assert result.success is False
        assert result.backend_name == "ocr"
        assert len(result.errors) > 0 or len(result.warnings) > 0


class TestOCRBackendMocked:
    """Focused unit tests for OCRBackend with mocked OCR execution."""

    def test_successful_ocr_result(self, tmp_path, monkeypatch):
        """Test successful OCR extraction returns proper result."""
        import fitz
        from unittest.mock import patch, MagicMock

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Test document content")
        pdf_path = tmp_path / "test.pdf"
        doc.save(str(pdf_path))
        doc.close()

        with patch("app.ai.extraction.ocr_backend.shutil.which", return_value="/fake/tesseract"):
            with patch("app.ai.extraction.ocr_backend.subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(stdout="tesseract 5.3.0", returncode=0),
                    MagicMock(stdout="List of available languages (3):\neng\nfra\nosd\n", returncode=0),
                ]
                backend = OCRBackend(language="eng", tesseract_cmd="/fake/tesseract")
                assert backend.is_available

        with patch("app.ai.extraction.ocr_backend.fitz.open") as mock_open:
            mock_page = MagicMock()
            mock_page.rect.width = 612
            mock_page.rect.height = 792
            mock_pix = MagicMock()
            mock_pix.tobytes.return_value = b"fake_png_bytes"
            mock_page.get_pixmap.return_value = mock_pix
            mock_doc = MagicMock()
            mock_doc.page_count = 1
            mock_doc.__getitem__.return_value = mock_page
            mock_doc.close = MagicMock()
            mock_open.return_value = mock_doc

            with patch("app.ai.extraction.ocr_backend.Image.open") as mock_img_open:
                mock_img = MagicMock()
                mock_img_open.return_value = mock_img

                with patch("app.ai.extraction.ocr_backend.pytesseract.image_to_string", return_value="Extracted text content"):
                    result = backend.extract_page(str(pdf_path), 1)

        assert result.success is True
        assert result.content == "Extracted text content"
        assert result.backend_name == "ocr"
        assert result.metadata["language"] == "eng"
        assert result.metadata["dpi"] == 300
        assert result.metadata["text_length"] > 0

    def test_missing_tesseract(self, monkeypatch):
        """Test OCR backend reports missing Tesseract."""
        import shutil
        from unittest.mock import patch

        with patch("app.ai.extraction.ocr_backend.shutil.which", return_value=None):
            with patch.dict("os.environ", {}, clear=True):
                backend = OCRBackend(language="eng", tesseract_cmd=None)
                assert not backend.is_available
                assert "not found" in backend.availability_error.lower()

    def test_missing_language_data(self, monkeypatch):
        """Test OCR backend reports missing language data."""
        from unittest.mock import patch, MagicMock

        with patch("app.ai.extraction.ocr_backend.shutil.which", return_value="/fake/tesseract"):
            with patch("app.ai.extraction.ocr_backend.subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(stdout="tesseract 5.3.0", returncode=0),
                    MagicMock(stdout="List of available languages (2):\neng\nosd\n", returncode=0),
                ]
                backend = OCRBackend(language="fra+eng", tesseract_cmd="/fake/tesseract")
                assert not backend.is_available
                assert "language data not available" in backend.availability_error.lower()
                assert "fra" in backend.availability_error.lower()

    def test_invalid_file(self):
        """Test OCR backend handles missing file."""
        backend = OCRBackend()
        backend._available = True
        backend._error = None
        backend._tesseract_path = "/fake/tesseract"

        result = backend.extract_page("/nonexistent/file.pdf", 1)
        assert result.success is False
        assert any("not found" in e.lower() for e in result.errors)
        assert result.backend_name == "ocr"

    def test_invalid_page_number(self, tmp_path):
        """Test OCR backend handles invalid page number."""
        import fitz
        from unittest.mock import patch, MagicMock

        doc = fitz.open()
        doc.new_page()
        pdf_path = tmp_path / "test.pdf"
        doc.save(str(pdf_path))
        doc.close()

        backend = OCRBackend()
        backend._available = True
        backend._error = None
        backend._tesseract_path = "/fake/tesseract"

        with patch("app.ai.extraction.ocr_backend.fitz.open") as mock_open:
            mock_doc = MagicMock()
            mock_doc.page_count = 1
            mock_doc.close = MagicMock()
            mock_open.return_value = mock_doc

            result = backend.extract_page(str(pdf_path), 5)
            assert result.success is False
            assert any("out of range" in e.lower() for e in result.errors)
            assert result.backend_name == "ocr"

    def test_ocr_runtime_failure(self, tmp_path):
        """Test OCR backend handles Tesseract runtime errors."""
        import fitz
        from unittest.mock import patch, MagicMock
        import pytesseract

        doc = fitz.open()
        doc.new_page()
        pdf_path = tmp_path / "test.pdf"
        doc.save(str(pdf_path))
        doc.close()

        backend = OCRBackend()
        backend._available = True
        backend._error = None
        backend._tesseract_path = "/fake/tesseract"

        with patch("app.ai.extraction.ocr_backend.fitz.open") as mock_open:
            mock_page = MagicMock()
            mock_page.rect.width = 612
            mock_page.rect.height = 792
            mock_pix = MagicMock()
            mock_pix.tobytes.return_value = b"fake_png_bytes"
            mock_page.get_pixmap.return_value = mock_pix
            mock_doc = MagicMock()
            mock_doc.page_count = 1
            mock_doc.__getitem__.return_value = mock_page
            mock_doc.close = MagicMock()
            mock_open.return_value = mock_doc

            with patch("app.ai.extraction.ocr_backend.Image.open"):
                with patch("app.ai.extraction.ocr_backend.pytesseract.image_to_string", side_effect=pytesseract.TesseractError(1, "OCR failed")):
                    result = backend.extract_page(str(pdf_path), 1)

        assert result.success is False
        assert any("ocr failed" in e.lower() for e in result.errors)
        assert result.backend_name == "ocr"

    def test_empty_ocr_output(self, tmp_path):
        """Test OCR backend handles empty OCR output."""
        import fitz
        from unittest.mock import patch, MagicMock

        doc = fitz.open()
        doc.new_page()
        pdf_path = tmp_path / "test.pdf"
        doc.save(str(pdf_path))
        doc.close()

        backend = OCRBackend()
        backend._available = True
        backend._error = None
        backend._tesseract_path = "/fake/tesseract"

        with patch("app.ai.extraction.ocr_backend.fitz.open") as mock_open:
            mock_page = MagicMock()
            mock_page.rect.width = 612
            mock_page.rect.height = 792
            mock_pix = MagicMock()
            mock_pix.tobytes.return_value = b"fake_png_bytes"
            mock_page.get_pixmap.return_value = mock_pix
            mock_doc = MagicMock()
            mock_doc.page_count = 1
            mock_doc.__getitem__.return_value = mock_page
            mock_doc.close = MagicMock()
            mock_open.return_value = mock_doc

            with patch("app.ai.extraction.ocr_backend.Image.open"):
                with patch("app.ai.extraction.ocr_backend.pytesseract.image_to_string", return_value="   \n\t  "):
                    result = backend.extract_page(str(pdf_path), 1)

        assert result.success is True
        assert result.content == ""
        assert any("empty" in w.lower() for w in result.warnings)
        assert result.backend_name == "ocr"

    def test_metadata_and_warnings(self, tmp_path):
        """Test OCR backend returns proper metadata and warnings."""
        import fitz
        from unittest.mock import patch, MagicMock

        doc = fitz.open()
        doc.new_page()
        pdf_path = tmp_path / "test.pdf"
        doc.save(str(pdf_path))
        doc.close()

        backend = OCRBackend(language="fra+eng", dpi=200)
        backend._available = True
        backend._error = None
        backend._tesseract_path = "/fake/tesseract"

        with patch("app.ai.extraction.ocr_backend.fitz.open") as mock_open:
            mock_page = MagicMock()
            mock_page.rect.width = 595
            mock_page.rect.height = 842
            mock_pix = MagicMock()
            mock_pix.tobytes.return_value = b"fake_png_bytes"
            mock_page.get_pixmap.return_value = mock_pix
            mock_doc = MagicMock()
            mock_doc.page_count = 1
            mock_doc.__getitem__.return_value = mock_page
            mock_doc.close = MagicMock()
            mock_open.return_value = mock_doc

            with patch("app.ai.extraction.ocr_backend.Image.open"):
                with patch("app.ai.extraction.ocr_backend.pytesseract.image_to_string", return_value="Test content"):
                    result = backend.extract_page(str(pdf_path), 1)

        assert result.success is True
        assert result.metadata["language"] == "fra+eng"
        assert result.metadata["dpi"] == 200
        assert result.metadata["page_width"] == 595
        assert result.metadata["page_height"] == 842
        assert result.metadata["text_length"] == len("Test content")
        assert result.backend_name == "ocr"


class TestLayoutBackend:
    def test_backend_name(self):
        backend = LayoutBackend()
        assert backend.name == "layout"

    def test_is_unavailable_placeholder(self):
        backend = LayoutBackend()
        result = backend.extract_page("any.pdf", 1)
        assert result.success is False
        assert result.backend_name == "layout"
        assert len(result.errors) > 0


class TestRouteClassification:
    def test_digital_simple_routes_to_pymupdf(self):
        assert route_classification("DIGITAL_SIMPLE") == "pymupdf"

    def test_digital_complex_routes_to_layout(self):
        assert route_classification("DIGITAL_COMPLEX") == "layout"

    def test_image_only_routes_to_ocr(self):
        assert route_classification("IMAGE_ONLY") == "ocr"

    def test_image_heavy_routes_to_ocr(self):
        assert route_classification("IMAGE_HEAVY") == "ocr"

    def test_ocr_required_routes_to_ocr(self):
        assert route_classification("OCR_REQUIRED") == "ocr"

    def test_extraction_failed_is_terminal(self):
        assert route_classification("EXTRACTION_FAILED") == "failure"

    def test_manual_review_is_terminal(self):
        assert route_classification("MANUAL_REVIEW") == "manual_review"

    def test_unknown_classification_raises(self):
        with pytest.raises(UnsupportedBackendError):
            route_classification("UNKNOWN_CLASSIFICATION")


class TestRoutePage:
    def test_hybrid_routes_to_pymupdf_when_text_dominant(self):
        page = PageClassification(
            page_number=1,
            classification="HYBRID",
            text_length=500,
            image_count=2,
            image_area_ratio=0.4,
            vector_object_count=10,
            font_count=3,
        )
        assert route_page(page) == "pymupdf"

    def test_hybrid_routes_to_ocr_when_image_dominant(self):
        page = PageClassification(
            page_number=1,
            classification="HYBRID",
            text_length=100,
            image_count=3,
            image_area_ratio=0.6,
            vector_object_count=20,
            font_count=2,
        )
        assert route_page(page) == "ocr"

    def test_hybrid_routes_to_layout_for_balanced(self):
        page = PageClassification(
            page_number=1,
            classification="HYBRID",
            text_length=100,
            image_count=3,
            image_area_ratio=0.45,
            vector_object_count=100,
            font_count=5,
        )
        assert route_page(page) == "layout"

    def test_digital_simple_direct(self):
        page = PageClassification(
            page_number=1, classification="DIGITAL_SIMPLE", text_length=200,
            image_count=0, image_area_ratio=0.0, vector_object_count=5, font_count=2,
        )
        assert route_page(page) == "pymupdf"

    def test_image_heavy_direct(self):
        page = PageClassification(
            page_number=1, classification="IMAGE_HEAVY", text_length=10,
            image_count=5, image_area_ratio=0.8, vector_object_count=0, font_count=0,
        )
        assert route_page(page) == "ocr"


class TestExtractionRouter:
    def test_register_and_get_backend(self):
        router = ExtractionRouter()
        backend = DummyBackend()
        router.register_backend(backend)
        assert router.get_backend("dummy") is backend

    def test_get_backend_creates_on_demand(self):
        router = ExtractionRouter()
        b = router.get_backend("pymupdf")
        assert isinstance(b, PyMuPDFBackend)

    def test_get_unknown_backend_raises(self):
        router = ExtractionRouter()
        with pytest.raises(UnsupportedBackendError):
            router.get_backend("nonexistent")

    def test_route_page_digital_simple(self, tmp_path):
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Simple text content here.")
        pdf_path = tmp_path / "simple.pdf"
        doc.save(str(pdf_path))
        doc.close()

        from app.ai.ingestion.pdf_inspector import PdfInspector
        inspector = PdfInspector()
        inspection = inspector.inspect(str(pdf_path))

        router = ExtractionRouter()
        result = router.extract_page(str(pdf_path), inspection.pages[0])
        assert result.success is True
        assert result.backend_name == "pymupdf"
        assert "simple" in result.content.lower()

    def test_route_page_extraction_failed(self, tmp_path):
        import fitz
        doc = fitz.open()
        doc.new_page()
        pdf_path = tmp_path / "empty.pdf"
        doc.save(str(pdf_path))
        doc.close()

        from app.ai.ingestion.pdf_inspector import PdfInspector
        inspector = PdfInspector()
        inspection = inspector.inspect(str(pdf_path))

        router = ExtractionRouter()
        result = router.extract_page(str(pdf_path), inspection.pages[0])
        assert result.success is False

    def test_route_page_manual_review(self):
        page = PageClassification(
            page_number=1, classification="MANUAL_REVIEW", text_length=0,
            image_count=0, image_area_ratio=0.0, vector_object_count=0, font_count=0,
        )
        router = ExtractionRouter()
        result = router.extract_page("any.pdf", page)
        assert result.success is False
        assert result.backend_name == "manual_review"

    def test_extract_with_unsupported_backend_raises(self):
        router = ExtractionRouter()
        with pytest.raises(UnsupportedBackendError):
            router.get_backend("nonexistent_backend")


class TestExtractionFailureHandling:
    def test_extract_page_returns_failure_result(self):
        result = ExtractionResult(
            page_number=1, content="", errors=["test error"], backend_name="x", success=False,
        )
        assert result.success is False
        assert len(result.errors) == 1

    def test_pymupdf_backend_failure_on_missing_file(self):
        backend = PyMuPDFBackend()
        result = backend.extract_page("/nonexistent/file.pdf", 1)
        assert result.success is False
        assert len(result.errors) > 0
        assert result.backend_name == "pymupdf"

    def test_ocr_backend_failure_reports_unavailable(self):
        backend = OCRBackend()
        result = backend.extract_page("any.pdf", 1)
        assert result.success is False
        assert result.backend_name == "ocr"

    def test_layout_backend_failure_reports_unavailable(self):
        backend = LayoutBackend()
        result = backend.extract_page("any.pdf", 1)
        assert result.success is False
        assert result.backend_name == "layout"
