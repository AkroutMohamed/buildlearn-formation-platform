from __future__ import annotations

import warnings
from pathlib import Path

import fitz
import pytest

from app.ai.extraction.layout_backend import LayoutBackend
from app.ai.extraction.ocr_backend import OCRBackend
from app.ai.extraction.pymupdf_backend import PyMuPDFBackend
from app.ai.extraction.renderer import render_document
from app.ai.extraction.router import ExtractionRouter, route_page
from app.ai.extraction.schema import CanonicalDocument, CanonicalPage
from app.ai.ingestion.pdf_inspector import PdfInspector

warnings.filterwarnings("ignore")


def _make_digital_simple_pdf(path: Path) -> None:
    """Create a 3-page digital-simple PDF with technical values and a table block."""
    doc = fitz.open()
    for idx in range(3):
        page = doc.new_page(width=595, height=842)
        if idx == 0:
            text = (
                "Technical Data Sheet\n"
                "Model: XT-200 Thermal Insulation Panel\n\n"
                "Description: The XT-200 is a high-performance rigid foam "
                "insulation board\n"
                "designed for roof and wall applications. It provides excellent "
                "thermal\n"
                "resistance with low moisture absorption.\n"
            )
        elif idx == 1:
            text = (
                "Technical Specifications\n\n"
                "Property                Value\n"
                "Thickness               12.5 mm\n"
                "Width                   1200 mm\n"
                "Density                 650 kg/m3\n"
                "Thermal Conductivity    0.032 W/(m·K)\n"
                "Compressive Strength    180 kPa\n"
                "Fire Rating             B-s1, d0\n"
            )
        else:
            text = (
                "Performance Characteristics\n\n"
                "The XT-200 panel achieves a thermal conductivity of 0.032 W/(m·K) "
                "and a\n"
                "compressive strength of 180 kPa. The closed-cell structure "
                "provides excellent\n"
                "dimensional stability. Operating temperature: -50 C to +100 C.\n"
            )
        page.insert_text((50, 80), text, fontsize=11)
    doc.save(str(path))
    doc.close()


def _run_full_chain(pdf_path: Path) -> tuple[CanonicalDocument, str]:
    """Run inspection -> classification -> routing -> extraction
    -> canonical schema -> renderer on a single PDF."""
    inspector = PdfInspector()
    inspection = inspector.inspect(str(pdf_path))

    doc = fitz.open(str(pdf_path))
    dims = [(page.rect.width, page.rect.height) for page in doc]
    doc.close()

    router = ExtractionRouter()
    pages: list[CanonicalPage] = []
    errors: list[str] = []

    for page in inspection.pages:
        w, h = dims[page.page_number - 1] if page.page_number - 1 < len(dims) else (0.0, 0.0)
        result = router.extract_page(str(pdf_path), page)
        pw = result.metadata.get("page_width", w)
        ph = result.metadata.get("page_height", h)
        cp = CanonicalPage.from_extraction_result(
            result,
            classification=page.classification,
            page_width=float(pw),
            page_height=float(ph),
        )
        pages.append(cp)
        if not result.success:
            errors.extend(result.errors)

    status = (
        "success"
        if all(p.extraction_status == "success" for p in pages)
        else "failed" if all(p.extraction_status == "failed" for p in pages)
        else "partial"
    )

    document = CanonicalDocument(
        document_id="e2e-test-doc",
        source_path=str(pdf_path),
        file_name=pdf_path.name,
        page_count=len(pages),
        extraction_status=status,
        errors=errors,
        pages=pages,
    )
    markdown = render_document(document)
    return document, markdown


class TestExtractionE2EChain:
    def test_digital_simple_full_chain_success(self, tmp_path):
        pdf_path = tmp_path / "digital_simple.pdf"
        _make_digital_simple_pdf(pdf_path)

        document, markdown = _run_full_chain(pdf_path)

        # Document-level
        assert document.extraction_status == "success"
        assert document.page_count == 3
        assert document.file_name == "digital_simple.pdf"

        # Page order and markers
        page_markers = [f"[Page {p.page_number}]" for p in document.pages]
        assert page_markers == ["[Page 1]", "[Page 2]", "[Page 3]"]
        import re
        md_markers = re.findall(r"\[Page (\d+)\]", markdown)
        assert md_markers == ["1", "2", "3"]

        # Each page: DIGITAL_SIMPLE -> pymupdf -> success
        for page in document.pages:
            assert page.classification == "DIGITAL_SIMPLE"
            assert page.backend_used == "pymupdf"
            assert page.extraction_status == "success"
            assert page.errors == []

        # Technical values preserved in rendered markdown
        for value in ["12.5 mm", "650 kg/m3", "0.032 W/(m·K)", "180 kPa", "B-s1, d0"]:
            assert value in markdown

    def test_technical_values_in_raw_text(self, tmp_path):
        pdf_path = tmp_path / "digital_simple.pdf"
        _make_digital_simple_pdf(pdf_path)

        document, _ = _run_full_chain(pdf_path)

        page2 = document.pages[1]
        assert "Thickness" in page2.raw_text
        assert "12.5 mm" in page2.raw_text
        assert "650 kg/m3" in page2.raw_text

    def test_routing_classification_to_backend_mapping(self, tmp_path):
        pdf_path = tmp_path / "digital_simple.pdf"
        _make_digital_simple_pdf(pdf_path)

        inspector = PdfInspector()
        inspection = inspector.inspect(str(pdf_path))

        for page in inspection.pages:
            assert page.classification == "DIGITAL_SIMPLE"
            assert route_page(page) == "pymupdf"

    def test_ocr_backend_unavailable(self, tmp_path):
        pdf_path = tmp_path / "digital_simple.pdf"
        _make_digital_simple_pdf(pdf_path)

        inspector = PdfInspector()
        inspection = inspector.inspect(str(pdf_path))
        router = ExtractionRouter()

        page = inspection.pages[0]
        # Simulate an OCR_REQUIRED page by overriding classification
        from app.ai.ingestion.pdf_inspector import PageClassification
        ocr_page = PageClassification(
            page_number=page.page_number,
            classification="OCR_REQUIRED",
            text_length=0,
            image_count=1,
            image_area_ratio=0.99,
            vector_object_count=0,
            font_count=0,
        )

        result = router.extract_page(str(pdf_path), ocr_page)
        assert result.backend_name == "ocr"
        assert result.success is False
        assert len(result.errors) > 0

    def test_layout_backend_unavailable(self):
        backend = LayoutBackend()
        result = backend.extract_page("any.pdf", 1)
        assert result.backend_name == "layout"
        assert result.success is False
        # Now that layout backend is implemented, it tries to open the file
        assert "not found" in result.errors[0].lower() or "no such file" in result.errors[0].lower()

    def test_canonical_page_metadata_backend_provenance(self, tmp_path):
        pdf_path = tmp_path / "digital_simple.pdf"
        _make_digital_simple_pdf(pdf_path)

        document, _ = _run_full_chain(pdf_path)

        for page in document.pages:
            assert page.backend_used == "pymupdf"
            assert page.page_width > 0
            assert page.page_height > 0
            assert page.raw_text  # non-empty
