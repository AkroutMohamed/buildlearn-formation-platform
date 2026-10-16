from app.ai.extraction.base import ExtractionBackend, ExtractionResult, ExtractionFailedError, UnsupportedBackendError
from app.ai.extraction.schema import (
    CanonicalDocument,
    CanonicalElement,
    CanonicalPage,
    DocumentExtraction,
    ElementExtraction,
    PageExtraction,
    SCHEMA_VERSION,
    SUPPORTED_ELEMENT_TYPES,
    TableData,
    TableExtraction,
)
from app.ai.extraction.pymupdf_backend import PyMuPDFBackend
from app.ai.extraction.ocr_backend import OCRBackend
from app.ai.extraction.layout_backend import LayoutBackend
from app.ai.extraction.router import ExtractionRouter, route_classification, route_page
