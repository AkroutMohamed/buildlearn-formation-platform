from pathlib import Path

from app.ai.ingestion.cleaner import BaseCleaner
from app.ai.ingestion.ocr_processor import OcrProcessor, is_ocr_available
from app.ai.ingestion.pdf_downloader import _content_hash, _is_pdf, _safe_filename
from app.ai.ingestion.pdf_processor import PdfProcessor


def test_safe_filename():
    assert _safe_filename("HYDRO 13 FRA.pdf") == "HYDRO_13_FRA.pdf"
    assert _safe_filename("normal.pdf") == "normal.pdf"
    assert _safe_filename("") == "document.pdf"
    assert _safe_filename("spaces.pdf") == "spaces.pdf"


def test_content_hash():
    assert _content_hash(b"hello") == _content_hash(b"hello")
    assert _content_hash(b"hello") != _content_hash(b"world")


def test_is_pdf_valid():
    assert _is_pdf(b"%PDF-1.4\n...", "application/pdf") is True
    assert _is_pdf(b"%PDF-1.4\n...", None) is True


def test_is_pdf_invalid_content_type():
    assert _is_pdf(b"%PDF-1.4\n...", "text/html") is False


def test_is_pdf_invalid_magic():
    assert _is_pdf(b"<!DOCTYPE html>", "text/html") is False


def test_base_cleaner_removes_extra_whitespace():
    cleaner = BaseCleaner()
    raw = "Hello   world\n\n\n\nHow are you?"
    cleaned = cleaner.clean(raw)
    assert cleaned == "Hello world\n\nHow are you?"


def test_base_cleaner_strips_html_entities():
    cleaner = BaseCleaner()
    raw = "Hello&nbsp;world&#160;test"
    cleaned = cleaner.clean(raw)
    assert "  " not in cleaned


def test_ocr_availability_returns_bool_and_error():
    available, error = is_ocr_available()
    assert isinstance(available, bool)
    assert error is None or isinstance(error, str)


def test_ocr_processor_reports_unavailable_gracefully():
    processor = OcrProcessor()
    assert processor.available == (processor.error is None)
    result = processor.process("nonexistent.pdf")
    assert "available" in result
    assert "error" in result
    assert result["pages"] == []


def test_pdf_processor_marks_ocr_required_when_no_text():
    pdf_path = Path(__file__).resolve().parent.parent.parent / "ai_data" / "raw" / "gypsobat" / "documents" / "LIKA-FINA.pdf"
    if not pdf_path.exists():
        return
    processor = PdfProcessor(cleaner=BaseCleaner(), ocr_processor=OcrProcessor())
    result = processor.extract(str(pdf_path))
    assert result["ocr"]["required"] is True
    assert result["page_count"] >= 1
    assert len(result["cleaned_text"]) == 0


def test_pdf_processor_does_not_attempt_ocr_when_text_present():
    pdf_path = Path(__file__).resolve().parent.parent.parent / "ai_data" / "raw" / "gypsobat" / "documents" / "fiche_technique_pap2.pdf"
    if not pdf_path.exists():
        return
    processor = PdfProcessor(cleaner=BaseCleaner(), ocr_processor=OcrProcessor())
    result = processor.extract(str(pdf_path))
    assert result["ocr"]["required"] is False
    assert result["ocr"]["attempted"] is False
    assert len(result["cleaned_text"]) > 0


def test_pdf_processor_extracts_text():
    pdf_path = Path(__file__).resolve().parent.parent.parent / "ai_data" / "raw" / "gypsobat" / "documents" / "fiche_technique_pap2.pdf"
    if not pdf_path.exists():
        return
    processor = PdfProcessor(cleaner=BaseCleaner())
    result = processor.extract(str(pdf_path))
    assert result["page_count"] >= 1
    assert len(result["cleaned_text"]) > 0
    assert "%PDF" not in result["cleaned_text"]
