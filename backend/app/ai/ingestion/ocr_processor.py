from __future__ import annotations

import logging
import os
import shutil
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

_OCR_AVAILABLE: bool | None = None
_OCR_ERROR: str | None = None


def is_ocr_available() -> tuple[bool, str | None]:
    global _OCR_AVAILABLE, _OCR_ERROR
    if _OCR_AVAILABLE is not None:
        return _OCR_AVAILABLE, _OCR_ERROR

    _OCR_AVAILABLE = False
    _OCR_ERROR = "OCR engine not detected"

    try:
        import pytesseract  # noqa: F401
        from pdf2image import convert_from_path  # noqa: F401
    except ImportError as exc:
        _OCR_ERROR = f"OCR Python packages not installed: {exc}"
        return _OCR_AVAILABLE, _OCR_ERROR

    tesseract_cmd = os.environ.get("TESSERACT_CMD") or shutil.which("tesseract")
    if not tesseract_cmd:
        _OCR_ERROR = "Tesseract executable not found in PATH"
        return _OCR_AVAILABLE, _OCR_ERROR

    try:
        subprocess.run([tesseract_cmd, "--version"], capture_output=True, check=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        _OCR_ERROR = f"Tesseract executable failed: {exc}"
        return _OCR_AVAILABLE, _OCR_ERROR

    _OCR_AVAILABLE = True
    _OCR_ERROR = None
    return _OCR_AVAILABLE, _OCR_ERROR


class OcrProcessor:
    def __init__(self, language: str = "fra", engine: str = "tesseract") -> None:
        self.language = language
        self.engine = engine
        self.available, self.error = is_ocr_available()

    def process(self, file_path: str) -> dict[str, Any]:
        if not self.available:
            return {
                "available": False,
                "error": self.error or "OCR engine not available",
                "language": self.language,
                "engine": self.engine,
                "pages": [],
                "raw_text": "",
                "cleaned_text": "",
            }

        try:
            from pdf2image import convert_from_path
            import pytesseract
        except ImportError as exc:
            return {
                "available": False,
                "error": f"OCR packages missing: {exc}",
                "language": self.language,
                "engine": self.engine,
                "pages": [],
                "raw_text": "",
                "cleaned_text": "",
            }

        tesseract_cmd = os.environ.get("TESSERACT_CMD") or shutil.which("tesseract")
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        pages: list[dict[str, Any]] = []
        raw_text_parts: list[str] = []

        try:
            images = convert_from_path(file_path, dpi=300)
        except Exception as exc:
            logger.error("Failed to convert PDF to images for OCR: %s", exc)
            return {
                "available": True,
                "error": f"PDF to image conversion failed: {exc}",
                "language": self.language,
                "engine": self.engine,
                "pages": [],
                "raw_text": "",
                "cleaned_text": "",
            }

        for page_number, image in enumerate(images, start=1):
            try:
                text = pytesseract.image_to_string(image, lang=self.language)
            except Exception as exc:
                logger.error("OCR failed on page %d: %s", page_number, exc)
                text = ""

            raw_text_parts.append(text)
            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                    "char_count": len(text),
                }
            )

        raw_text = "\n\n".join(raw_text_parts)
        return {
            "available": True,
            "error": None,
            "language": self.language,
            "engine": self.engine,
            "pages": pages,
            "raw_text": raw_text,
            "cleaned_text": raw_text.strip(),
        }
