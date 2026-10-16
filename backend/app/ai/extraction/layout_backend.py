from __future__ import annotations

import logging
from typing import Any

import fitz

from app.ai.extraction.base import ExtractionBackend, ExtractionResult

logger = logging.getLogger(__name__)


class LayoutBackend(ExtractionBackend):
    """Layout-aware extraction backend using PyMuPDF's built-in layout analysis.

    Uses:
    - page.get_text("dict") for structured text blocks with font info
    - page.find_tables() for table detection and extraction
    """

    def __init__(self) -> None:
        self._available = True
        self._error: str | None = None

    @property
    def name(self) -> str:
        return "layout"

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def availability_error(self) -> str | None:
        return self._error

    def extract_page(self, file_path: str, page_number: int) -> ExtractionResult:
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

            # Extract structured text blocks
            text_dict = page.get_text("dict")
            blocks = text_dict.get("blocks", [])

            # Extract tables
            table_finder = page.find_tables()
            tables = table_finder.tables if hasattr(table_finder, "tables") else []

            # Process text blocks into elements
            elements = []
            reading_order = 0

            # First, collect table bounding boxes to avoid duplicating table text
            table_bboxes = [t.bbox for t in tables]

            for block in blocks:
                if block.get("type") != 0:  # Only text blocks (type 0)
                    continue

                bbox = block.get("bbox", [0, 0, 0, 0])
                block_text = self._extract_block_text(block)

                if not block_text.strip():
                    continue

                # Skip if this block is inside a table
                if self._is_inside_any_table(bbox, table_bboxes):
                    continue

                element_type = self._classify_block(block, block_text)
                reading_order += 1

                elements.append({
                    "element_type": element_type,
                    "text": block_text,
                    "bbox": bbox,
                    "reading_order": reading_order,
                })

            # Add table elements
            for table in tables:
                reading_order += 1
                table_data = self._extract_table_data(table, page_number, reading_order)
                if table_data:
                    elements.append(table_data)

            # Sort elements by reading order (top to bottom, left to right)
            elements.sort(key=lambda e: (e["reading_order"], e.get("bbox", [0, 0, 0, 0])[1]))

            # Build raw text for backward compatibility
            raw_text = "\n\n".join(e["text"] for e in elements if "text" in e)

            # Prepare metadata with structured elements
            metadata: dict[str, Any] = {
                "page_width": page_width,
                "page_height": page_height,
                "text_length": len(raw_text),
                "element_count": len(elements),
                "structured_elements": elements,
            }

            doc.close()

            return ExtractionResult(
                page_number=page_number,
                content=raw_text,
                metadata=metadata,
                backend_name=self.name,
                success=True,
            )

        except Exception as exc:
            logger.exception("Layout extraction failed for page %d", page_number)
            doc.close()
            return ExtractionResult(
                page_number=page_number,
                content="",
                errors=[str(exc)],
                backend_name=self.name,
                success=False,
            )

    def _extract_block_text(self, block: dict) -> str:
        """Extract text from a text block dict."""
        lines = []
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if spans:
                line_text = "".join(span.get("text", "") for span in spans)
                lines.append(line_text)
        return "\n".join(lines)

    def _is_inside_any_table(self, bbox: list[float], table_bboxes: list[tuple]) -> bool:
        """Check if a bbox is inside any table bbox."""
        bx1, by1, bx2, by2 = bbox
        for tb in table_bboxes:
            tx1, ty1, tx2, ty2 = tb
            if bx1 >= tx1 and by1 >= ty1 and bx2 <= tx2 and by2 <= ty2:
                return True
        return False

    def _classify_block(self, block: dict, text: str) -> str:
        """Classify a text block into an element type."""
        lines = block.get("lines", [])
        if not lines:
            return "paragraph"

        # Get the first span to check font properties
        first_span = lines[0].get("spans", [{}])[0]
        font_size = first_span.get("size", 11)
        font_name = first_span.get("font", "").lower()
        bbox = block.get("bbox", [0, 0, 0, 0])

        # Heuristics for element classification
        text_stripped = text.strip()

        # Check for list markers
        if text_stripped.startswith(("- ", "* ", "• ", "· ")) or any(
            line.strip().startswith(("- ", "* ", "• ", "· ")) for line in text_stripped.split("\n")
        ):
            return "list"

        # Check for heading by font size (larger than body text)
        if font_size > 14:
            return "heading"

        # Check for title (large font, near top of page)
        if font_size > 18 and bbox[1] < 150:
            return "title"

        # Check for figure caption
        if text_stripped.lower().startswith(("figure ", "fig. ", "fig ", "image ")):
            return "figure_caption"

        # Check for table caption
        if text_stripped.lower().startswith(("table ", "tab. ")):
            return "table_caption"

        # Check for header/footer by position
        if bbox[1] < 50:
            return "header"
        if bbox[3] > 800:  # Near bottom of typical page
            return "footer"

        return "paragraph"

    def _extract_table_data(self, table: Any, page_number: int, reading_order: int) -> dict | None:
        """Extract table data into canonical format."""
        try:
            extracted = table.extract()
            if not extracted or len(extracted) < 1:
                return None

            headers = extracted[0] if len(extracted) > 0 else []
            rows = extracted[1:] if len(extracted) > 1 else []

            # Clean up cells (remove extra newlines) - handle None cells
            headers = [(h or "").replace("\n", " ").strip() for h in headers]
            rows = [[(cell or "").replace("\n", " ").strip() for cell in row] for row in rows]

            # Build text representation
            table_text_parts = [" | ".join(headers)] if headers else []
            for row in rows:
                table_text_parts.append(" | ".join(row))
            table_text = "\n".join(table_text_parts)

            return {
                "element_type": "table",
                "text": table_text,
                "bbox": list(table.bbox),
                "reading_order": reading_order,
                "table_data": {
                    "headers": headers,
                    "rows": rows,
                    "bbox": list(table.bbox),
                },
            }
        except Exception as exc:
            logger.warning("Failed to extract table: %s", exc)
            return None