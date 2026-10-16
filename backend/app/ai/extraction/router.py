from __future__ import annotations

import logging
from typing import Any

from app.ai.extraction.base import (
    ExtractionBackend,
    ExtractionResult,
    UnsupportedBackendError,
)
from app.ai.extraction.ocr_backend import OCRBackend
from app.ai.extraction.layout_backend import LayoutBackend
from app.ai.extraction.pymupdf_backend import PyMuPDFBackend
from app.ai.ingestion.pdf_inspector import PageClassification

logger = logging.getLogger(__name__)

_BACKEND_REGISTRY: dict[str, type[ExtractionBackend]] = {
    "pymupdf": PyMuPDFBackend,
    "ocr": OCRBackend,
    "layout": LayoutBackend,
}

_CLASSIFICATION_TO_BACKEND: dict[str, str] = {
    "DIGITAL_SIMPLE": "pymupdf",
    "DIGITAL_COMPLEX": "layout",
    "IMAGE_ONLY": "ocr",
    "IMAGE_HEAVY": "ocr",
    "OCR_REQUIRED": "ocr",
    "EXTRACTION_FAILED": "failure",
    "MANUAL_REVIEW": "manual_review",
}


def route_classification(classification: str) -> str:
    if classification in _CLASSIFICATION_TO_BACKEND:
        return _CLASSIFICATION_TO_BACKEND[classification]
    raise UnsupportedBackendError(
        f"No backend route for classification: {classification}"
    )


def route_page(page: PageClassification) -> str:
    classification = page.classification

    if classification == "HYBRID":
        if page.image_area_ratio >= 0.5:
            return "ocr"
        if page.text_length >= 50 and page.vector_object_count <= 50:
            return "pymupdf"
        return "layout"

    return route_classification(classification)


class ExtractionRouter:
    def __init__(self) -> None:
        self._backends: dict[str, ExtractionBackend] = {}

    def register_backend(self, backend: ExtractionBackend) -> None:
        self._backends[backend.name] = backend

    def get_backend(self, backend_name: str) -> ExtractionBackend:
        if backend_name in self._backends:
            return self._backends[backend_name]
        if backend_name not in _BACKEND_REGISTRY:
            raise UnsupportedBackendError(f"Unknown backend: {backend_name}")
        backend_cls = _BACKEND_REGISTRY[backend_name]
        self._backends[backend_name] = backend_cls()
        return self._backends[backend_name]

    def route_page(self, page: PageClassification) -> ExtractionBackend:
        backend_name = route_page(page)
        if backend_name in ("failure", "manual_review"):
            raise UnsupportedBackendError(
                f"No extraction backend for classification: {page.classification}"
            )
        return self.get_backend(backend_name)

    def extract_page(
        self, file_path: str, page: PageClassification
    ) -> ExtractionResult:
        backend_name = route_page(page)
        if backend_name in ("failure", "manual_review"):
            if page.classification == "EXTRACTION_FAILED":
                return ExtractionResult(
                    page_number=page.page_number,
                    content="",
                    errors=page.extraction_error or ["Extraction failed"],
                    backend_name="failure",
                    success=False,
                )
            return ExtractionResult(
                page_number=page.page_number,
                content="",
                warnings=["Manual review required"],
                backend_name="manual_review",
                success=False,
            )

        backend = self.get_backend(backend_name)
        return backend.extract_page(file_path, page.page_number)
