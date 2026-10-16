from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from app.ai.ingestion.cleaner import BaseCleaner
from app.ai.ingestion.ocr_processor import OcrProcessor

logger = logging.getLogger(__name__)


class PdfProcessor:
    def __init__(self, cleaner: BaseCleaner | None = None, ocr_processor: OcrProcessor | None = None) -> None:
        self.cleaner = cleaner
        self.ocr_processor = ocr_processor

    def extract(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        raw_text = "\n\n".join(pages)
        cleaned = self.cleaner.clean(raw_text) if self.cleaner else raw_text

        result: dict[str, Any] = {
            "file_path": str(path),
            "page_count": len(reader.pages),
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "metadata": {
                "producer": reader.metadata.get("/Producer") if reader.metadata else None,
                "creator": reader.metadata.get("/Creator") if reader.metadata else None,
            },
            "ocr": {
                "required": False,
                "attempted": False,
                "available": False,
                "error": None,
                "pages": [],
                "raw_text": "",
                "cleaned_text": "",
            },
        }

        extracted_char_count = len(cleaned.strip())
        if extracted_char_count == 0 and len(reader.pages) > 0 and self.ocr_processor:
            result["ocr"]["required"] = True
            result["ocr"]["available"] = self.ocr_processor.available
            if self.ocr_processor.available:
                result["ocr"]["attempted"] = True
                ocr_result = self.ocr_processor.process(file_path)
                result["ocr"]["pages"] = ocr_result.get("pages", [])
                result["ocr"]["raw_text"] = ocr_result.get("raw_text", "")
                result["ocr"]["cleaned_text"] = ocr_result.get("cleaned_text", "")
                result["ocr"]["error"] = ocr_result.get("error")

                if ocr_result.get("cleaned_text"):
                    result["raw_text"] = ocr_result["cleaned_text"]
                    result["cleaned_text"] = self.cleaner.clean(ocr_result["cleaned_text"]) if self.cleaner else ocr_result["cleaned_text"]
            else:
                result["ocr"]["error"] = self.ocr_processor.error or "OCR engine not available"

        return result
