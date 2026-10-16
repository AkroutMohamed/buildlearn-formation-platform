from __future__ import annotations

import io
import logging
import os
import shutil
import subprocess
from typing import Any, Optional

import fitz
import pytesseract
from PIL import Image

from app.ai.config import ai_settings
from app.ai.extraction.base import ExtractionBackend, ExtractionResult

logger = logging.getLogger(__name__)


class TesseractNotAvailableError(Exception):
    """Raised when Tesseract executable or language data is not available."""


class OCRBackend(ExtractionBackend):
    """OCR extraction backend using Tesseract and PyMuPDF page rendering."""

    def __init__(
        self,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        tesseract_cmd: Optional[str] = None,
        dpi: int = 300,
    ) -> None:
        self._language = language or ai_settings.ocr_language or "fra+eng"
        self._engine = engine or ai_settings.ocr_engine or "tesseract"
        self._tesseract_cmd = tesseract_cmd or os.environ.get("TESSERACT_CMD")
        self._dpi = dpi
        self._available = False
        self._error: Optional[str] = None
        self._tesseract_path: Optional[str] = None
        self._check_availability()

    def _check_availability(self) -> None:
        if self._engine != "tesseract":
            self._available = False
            self._error = f"Unsupported OCR engine: {self._engine}"
            return

        try:
            import pytesseract  # noqa: F401
        except ImportError as exc:
            self._available = False
            self._error = f"pytesseract not installed: {exc}"
            return

        tesseract_path = self._tesseract_cmd or shutil.which("tesseract")
        if not tesseract_path:
            self._available = False
            self._error = "Tesseract executable not found in PATH and TESSERACT_CMD not set"
            return

        try:
            result = subprocess.run(
                [tesseract_path, "--version"],
                capture_output=True,
                check=True,
                text=True,
                timeout=5,
            )
            version_line = result.stdout.split("\n")[0]
            logger.debug("Tesseract version: %s", version_line)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
            self._available = False
            self._error = f"Tesseract executable failed: {exc}"
            return

        try:
            lang_output = subprocess.run(
                [tesseract_path, "--list-langs"],
                capture_output=True,
                check=True,
                text=True,
                timeout=5,
            )
            available_langs = lang_output.stdout.strip().split("\n")[1:]
            available_langs = [lang.strip() for lang in available_langs if lang.strip()]
            logger.debug("Available Tesseract languages: %s", available_langs)
            requested = [l.strip() for l in self._language.split("+")]
            missing = [l for l in requested if l not in available_langs]
            if missing:
                self._available = False
                self._error = f"Tesseract language data not available: {', '.join(missing)}. Available: {', '.join(available_langs) if available_langs else 'none'}"
                return
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
            self._available = False
            self._error = f"Failed to list Tesseract languages: {exc}"
            return

        self._tesseract_path = tesseract_path
        self._available = True
        self._error = None

    @property
    def name(self) -> str:
        return "ocr"

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def availability_error(self) -> Optional[str]:
        return self._error

    def extract_page(self, file_path: str, page_number: int) -> ExtractionResult:
        if not self._available:
            return ExtractionResult(
                page_number=page_number,
                content="",
                errors=[self._error or "OCR engine not available"],
                backend_name=self.name,
                success=False,
            )

        if not os.path.exists(file_path):
            return ExtractionResult(
                page_number=page_number,
                content="",
                errors=[f"File not found: {file_path}"],
                backend_name=self.name,
                success=False,
            )

        try:
            doc = fitz.open(file_path)
        except Exception as exc:
            return ExtractionResult(
                page_number=page_number,
                content="",
                errors=[f"Failed to open PDF: {exc}"],
                backend_name=self.name,
                success=False,
            )

        try:
            zero_index = page_number - 1
            if zero_index < 0 or zero_index >= doc.page_count:
                doc.close()
                return ExtractionResult(
                    page_number=page_number,
                    content="",
                    errors=[f"Page {page_number} out of range (1-{doc.page_count})"],
                    backend_name=self.name,
                    success=False,
                )

            page = doc[zero_index]
            page_width = page.rect.width
            page_height = page.rect.height
            pix = page.get_pixmap(dpi=self._dpi)
            img_bytes = pix.tobytes("png")

            try:
                img = Image.open(io.BytesIO(img_bytes))
            except Exception as exc:
                doc.close()
                return ExtractionResult(
                    page_number=page_number,
                    content="",
                    errors=[f"Failed to load rendered image: {exc}"],
                    backend_name=self.name,
                    success=False,
                )

            try:
                old_tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
                pytesseract.pytesseract.tesseract_cmd = self._tesseract_path
                text = pytesseract.image_to_string(img, lang=self._language)
                pytesseract.pytesseract.tesseract_cmd = old_tesseract_cmd
            except pytesseract.TesseractNotFoundError as exc:
                doc.close()
                return ExtractionResult(
                    page_number=page_number,
                    content="",
                    errors=[f"Tesseract not found at runtime: {exc}"],
                    backend_name=self.name,
                    success=False,
                )
            except pytesseract.TesseractError as exc:
                doc.close()
                return ExtractionResult(
                    page_number=page_number,
                    content="",
                    errors=[f"Tesseract OCR failed: {exc}"],
                    backend_name=self.name,
                    success=False,
                )
            except Exception as exc:
                doc.close()
                return ExtractionResult(
                    page_number=page_number,
                    content="",
                    errors=[f"OCR processing error: {exc}"],
                    backend_name=self.name,
                    success=False,
                )

            doc.close()

            if not text or not text.strip():
                return ExtractionResult(
                    page_number=page_number,
                    content="",
                    warnings=["OCR produced empty text output"],
                    metadata={
                        "language": self._language,
                        "dpi": self._dpi,
                        "page_width": page_width,
                        "page_height": page_height,
                    },
                    backend_name=self.name,
                    success=True,
                )

            metadata: dict[str, Any] = {
                "language": self._language,
                "dpi": self._dpi,
                "page_width": page_width,
                "page_height": page_height,
                "text_length": len(text),
            }

            return ExtractionResult(
                page_number=page_number,
                content=text.strip(),
                metadata=metadata,
                backend_name=self.name,
                success=True,
            )

        except Exception as exc:
            logger.exception("OCR extraction failed for page %d", page_number)
            return ExtractionResult(
                page_number=page_number,
                content="",
                errors=[str(exc)],
                backend_name=self.name,
                success=False,
            )