from __future__ import annotations

import logging
from typing import Any

import fitz

from app.ai.extraction.base import ExtractionBackend, ExtractionResult

logger = logging.getLogger(__name__)


class PyMuPDFBackend(ExtractionBackend):
    def __init__(self, password: str | None = None) -> None:
        self._password = password

    @property
    def name(self) -> str:
        return "pymupdf"

    def extract_page(self, file_path: str, page_number: int) -> ExtractionResult:
        try:
            doc = fitz.open(file_path)
            if doc.is_encrypted:
                if self._password:
                    doc.authenticate(self._password)
                else:
                    doc.close()
                    return ExtractionResult(
                        page_number=page_number,
                        content="",
                        errors=["PDF is encrypted and no password provided"],
                        backend_name=self.name,
                        success=False,
                    )

            zero_index = page_number - 1
            if zero_index < 0 or zero_index >= doc.page_count:
                doc.close()
                return ExtractionResult(
                    page_number=page_number,
                    content="",
                    errors=[f"Page {page_number} out of range (0-{doc.page_count - 1})"],
                    backend_name=self.name,
                    success=False,
                )

            page = doc[zero_index]
            text = page.get_text("text") or ""
            metadata: dict[str, Any] = {
                "text_length": len(text),
                "page_width": page.rect.width,
                "page_height": page.rect.height,
            }
            doc.close()

            return ExtractionResult(
                page_number=page_number,
                content=text,
                metadata=metadata,
                backend_name=self.name,
                success=True,
            )

        except Exception as e:
            logger.exception("PyMuPDF extraction failed for page %d", page_number)
            return ExtractionResult(
                page_number=page_number,
                content="",
                errors=[str(e)],
                backend_name=self.name,
                success=False,
            )
