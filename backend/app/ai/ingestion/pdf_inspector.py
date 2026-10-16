from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import fitz

logger = logging.getLogger(__name__)


@dataclass
class PageClassification:
    page_number: int
    classification: str
    text_length: int
    image_count: int
    image_area_ratio: float
    vector_object_count: int
    font_count: int
    extraction_error: str | None = None


@dataclass
class DocumentInspection:
    file_path: str
    page_count: int
    pages: list[PageClassification]
    document_classification: str
    error: str | None = None


class PdfInspector:
    """Deterministic page-level PDF classification using PyMuPDF.

    Classifications:
        - DIGITAL_SIMPLE: Text-based page with simple layout, minimal vector objects
        - DIGITAL_COMPLEX: Text-based page with complex layout, many vector objects
        - IMAGE_ONLY: Page contains only images, no extractable text
        - IMAGE_HEAVY: Page dominated by images with little text
        - HYBRID: Mix of text and images, balanced content
        - OCR_REQUIRED: Page appears to be scanned (image-based) but OCR may extract text
        - EXTRACTION_FAILED: Failed to inspect page due to corruption or password
        - MANUAL_REVIEW: Ambiguous page requiring human review
    """

    # Thresholds for classification
    IMAGE_AREA_RATIO_IMAGE_ONLY = 0.95
    IMAGE_AREA_RATIO_IMAGE_HEAVY = 0.70
    IMAGE_AREA_RATIO_HYBRID_MIN = 0.30
    IMAGE_AREA_RATIO_HYBRID_MAX = 0.70
    TEXT_LENGTH_DIGITAL_SIMPLE_MIN = 100
    TEXT_LENGTH_DIGITAL_COMPLEX_MIN = 50
    VECTOR_OBJECTS_DIGITAL_SIMPLE_MAX = 50
    VECTOR_OBJECTS_DIGITAL_COMPLEX_MIN = 50
    FONT_COUNT_SIMPLE_MAX = 3

    def __init__(self, password: str | None = None) -> None:
        self.password = password

    def inspect(self, file_path: str) -> DocumentInspection:
        """Inspect a PDF file and classify each page.

        Args:
            file_path: Path to the PDF file.

        Returns:
            DocumentInspection with page-level classifications and document-level summary.
        """
        path = Path(file_path)
        if not path.exists():
            return DocumentInspection(
                file_path=str(path),
                page_count=0,
                pages=[],
                document_classification="EXTRACTION_FAILED",
                error=f"File not found: {file_path}",
            )

        try:
            doc = fitz.open(str(path))
            if doc.is_encrypted:
                if self.password:
                    doc.authenticate(self.password)
                else:
                    doc.close()
                    return DocumentInspection(
                        file_path=str(path),
                        page_count=0,
                        pages=[],
                        document_classification="EXTRACTION_FAILED",
                        error="PDF is encrypted and no password provided",
                    )

            pages: list[PageClassification] = []
            for page_num in range(doc.page_count):
                page = doc[page_num]
                classification = self._classify_page(page, page_num + 1)
                pages.append(classification)

            doc.close()

            document_classification = self._aggregate_document_classification(pages)

            return DocumentInspection(
                file_path=str(path),
                page_count=len(pages),
                pages=pages,
                document_classification=document_classification,
            )

        except Exception as e:
            logger.exception("Failed to inspect PDF: %s", file_path)
            return DocumentInspection(
                file_path=str(path),
                page_count=0,
                pages=[],
                document_classification="EXTRACTION_FAILED",
                error=str(e),
            )

    def _classify_page(self, page: fitz.Page, page_number: int) -> PageClassification:
        """Classify a single PDF page."""
        try:
            text = page.get_text("text") or ""
            text_length = len(text.strip())

            image_list = page.get_images(full=True)
            image_count = len(image_list)

            page_rect = page.rect
            page_area = page_rect.width * page_rect.height
            image_area = 0.0
            for img in image_list:
                xref = img[0]
                try:
                    rects = page.get_image_rects(xref)
                    for r in rects:
                        img_area = r.width * r.height
                        image_area += img_area
                except Exception:
                    pass

            image_area_ratio = image_area / page_area if page_area > 0 else 0.0
            if image_area_ratio > 1.0:
                image_area_ratio = 1.0

            drawings = page.get_drawings()
            vector_object_count = len(drawings)

            fonts = page.get_fonts()
            font_count = len(fonts)

            classification = self._determine_classification(
                text_length=text_length,
                image_count=image_count,
                image_area_ratio=image_area_ratio,
                vector_object_count=vector_object_count,
                font_count=font_count,
            )

            return PageClassification(
                page_number=page_number,
                classification=classification,
                text_length=text_length,
                image_count=image_count,
                image_area_ratio=round(image_area_ratio, 4),
                vector_object_count=vector_object_count,
                font_count=font_count,
                extraction_error=None,
            )

        except Exception as e:
            logger.exception("Failed to classify page %d", page_number)
            return PageClassification(
                page_number=page_number,
                classification="EXTRACTION_FAILED",
                text_length=0,
                image_count=0,
                image_area_ratio=0.0,
                vector_object_count=0,
                font_count=0,
                extraction_error=str(e),
            )

    def _determine_classification(
        self,
        text_length: int,
        image_count: int,
        image_area_ratio: float,
        vector_object_count: int,
        font_count: int,
    ) -> str:
        """Determine page classification based on deterministic rules."""

        if text_length == 0 and image_count == 0:
            return "EXTRACTION_FAILED"

        if text_length == 0 and image_count > 0:
            if image_area_ratio >= self.IMAGE_AREA_RATIO_IMAGE_ONLY:
                return "IMAGE_ONLY"
            return "OCR_REQUIRED"

        if text_length > 0 and image_count == 0:
            if vector_object_count <= self.VECTOR_OBJECTS_DIGITAL_SIMPLE_MAX and font_count <= self.FONT_COUNT_SIMPLE_MAX:
                return "DIGITAL_SIMPLE"
            return "DIGITAL_COMPLEX"

        if image_count > 0:
            if image_area_ratio >= self.IMAGE_AREA_RATIO_IMAGE_HEAVY:
                return "IMAGE_HEAVY"
            if self.IMAGE_AREA_RATIO_HYBRID_MIN <= image_area_ratio < self.IMAGE_AREA_RATIO_IMAGE_HEAVY:
                return "HYBRID"
            if text_length >= self.TEXT_LENGTH_DIGITAL_SIMPLE_MIN and vector_object_count <= self.VECTOR_OBJECTS_DIGITAL_SIMPLE_MAX:
                return "DIGITAL_SIMPLE"
            if text_length >= self.TEXT_LENGTH_DIGITAL_COMPLEX_MIN:
                return "DIGITAL_COMPLEX"
            return "HYBRID"

        return "MANUAL_REVIEW"

    def _aggregate_document_classification(self, pages: list[PageClassification]) -> str:
        """Aggregate page classifications into document-level classification."""
        if not pages:
            return "EXTRACTION_FAILED"

        classifications = [p.classification for p in pages]

        if all(c == "EXTRACTION_FAILED" for c in classifications):
            return "EXTRACTION_FAILED"

        if any(c == "EXTRACTION_FAILED" for c in classifications):
            return "MANUAL_REVIEW"

        unique_classifications = set(classifications)

        if len(unique_classifications) == 1:
            single = unique_classifications.pop()
            if single in ("IMAGE_ONLY", "OCR_REQUIRED"):
                return single
            return f"{single}_DOCUMENT"

        has_images = any(c in ("IMAGE_ONLY", "IMAGE_HEAVY", "HYBRID", "OCR_REQUIRED") for c in classifications)
        has_digital = any(c in ("DIGITAL_SIMPLE", "DIGITAL_COMPLEX") for c in classifications)

        if has_images and has_digital:
            return "HYBRID_DOCUMENT"
        if has_images:
            return "IMAGE_HEAVY_DOCUMENT"
        if has_digital:
            return "DIGITAL_DOCUMENT"

        return "MANUAL_REVIEW"

    def to_json(self, inspection: DocumentInspection) -> str:
        """Serialize DocumentInspection to JSON string."""
        return json.dumps(self.to_dict(inspection), ensure_ascii=False, indent=2)

    def to_dict(self, inspection: DocumentInspection) -> dict[str, Any]:
        """Convert DocumentInspection to JSON-serializable dict."""
        return {
            "file_path": inspection.file_path,
            "page_count": inspection.page_count,
            "pages": [asdict(page) for page in inspection.pages],
            "document_classification": inspection.document_classification,
            "error": inspection.error,
        }


def inspect_pdf(file_path: str, password: str | None = None) -> DocumentInspection:
    """Convenience function to inspect a PDF file."""
    inspector = PdfInspector(password=password)
    return inspector.inspect(file_path)