from __future__ import annotations

import pytest

from app.ai.extraction.schema import (
    SCHEMA_VERSION,
    CanonicalDocument,
    CanonicalElement,
    CanonicalPage,
    TableData,
)
from app.ai.extraction.renderer import (
    DEGRADED_TABLE_MARKER,
    PAGE_MARKER_PREFIX,
    PAGE_MARKER_SUFFIX,
    UNKNOWN_ELEMENT_MARKER,
    render_document,
    render_element,
    render_pages,
    render_table,
)


def make_table() -> TableData:
    return TableData(
        table_id="table-1",
        caption="Technical specifications",
        headers=["Property", "Value"],
        rows=[["Thickness", "12.5 mm"], ["Density", "650 kg/m3"]],
        page_number=1,
        bounding_box=[10.0, 20.0, 300.0, 180.0],
        extraction_warnings=["Table structure requires review"],
    )


def make_document() -> CanonicalDocument:
    element = CanonicalElement(
        element_id="element-1",
        element_type="table",
        text="Thickness 12.5 mm; Density 650 kg/m3",
        page_number=1,
        reading_order=2,
        bounding_box=[10.0, 20.0, 300.0, 180.0],
        confidence=0.96,
        metadata={"backend": "pymupdf"},
        table=make_table(),
    )
    page = CanonicalPage(
        page_number=1,
        page_width=595.0,
        page_height=842.0,
        classification="DIGITAL_SIMPLE",
        backend_used="pymupdf",
        extraction_status="success",
        raw_text="Technical specifications\nThickness 12.5 mm; Density 650 kg/m3",
        ordered_elements=[element],
        warnings=["Page warning"],
        errors=[],
    )
    return CanonicalDocument(
        schema_version=SCHEMA_VERSION,
        document_id="document-1",
        source_path="/documents/product.pdf",
        source_url="https://example.com/product.pdf",
        file_name="product.pdf",
        file_hash="sha256:example",
        page_count=1,
        extraction_status="success",
        warnings=["Document warning"],
        errors=[],
        pages=[page],
    )


class TestRenderTable:
    def test_render_table_with_headers_and_rows(self):
        table = make_table()
        md = render_table(table)

        assert "| Property | Value |" in md
        assert "|---|---|" in md
        assert "| Thickness | 12.5 mm |" in md
        assert "| Density | 650 kg/m3 |" in md

    def test_render_table_escapes_pipes_in_cells(self):
        table = TableData(
            table_id="table-2",
            headers=["A|B", "C"],
            rows=[["x|y", "z"]],
            page_number=1,
        )
        md = render_table(table)
        assert "A\\|B" in md
        assert "x\\|y" in md

    def test_render_degraded_table_no_headers_no_rows(self):
        table = TableData(table_id="table-3", headers=[], rows=[], page_number=1)
        md = render_table(table)
        assert DEGRADED_TABLE_MARKER in md

    def test_render_table_empty_headers_with_rows_pads_columns(self):
        table = TableData(
            table_id="table-4",
            headers=[],
            rows=[["A", "B"], ["C"]],
            page_number=1,
        )
        md = render_table(table)
        assert "| A | B |" in md
        assert "| C |  |" in md


class TestRenderElement:
    def test_render_title(self):
        element = CanonicalElement(
            element_id="e1",
            element_type="title",
            text="Document Title",
            page_number=1,
            reading_order=0,
        )
        md = render_element(element)
        assert md == "# Document Title"

    def test_render_heading(self):
        element = CanonicalElement(
            element_id="e2",
            element_type="heading",
            text="Section Heading",
            page_number=1,
            reading_order=1,
        )
        md = render_element(element)
        assert md == "## Section Heading"

    def test_render_paragraph(self):
        element = CanonicalElement(
            element_id="e3",
            element_type="paragraph",
            text="Paragraph text.",
            page_number=1,
            reading_order=2,
        )
        md = render_element(element)
        assert md == "Paragraph text."

    def test_render_list_multiple_lines(self):
        element = CanonicalElement(
            element_id="e4",
            element_type="list",
            text="Item 1\nItem 2\nItem 3",
            page_number=1,
            reading_order=3,
        )
        md = render_element(element)
        assert "- Item 1" in md
        assert "- Item 2" in md
        assert "- Item 3" in md

    def test_render_list_preserves_existing_bullets(self):
        element = CanonicalElement(
            element_id="e5",
            element_type="list",
            text="- First\n* Second\n• Third",
            page_number=1,
            reading_order=4,
        )
        md = render_element(element)
        assert "- First" in md
        assert "* Second" in md
        assert "• Third" in md

    def test_render_table_element_with_table_data(self):
        element = CanonicalElement(
            element_id="e6",
            element_type="table",
            text="fallback",
            page_number=1,
            reading_order=5,
            table=make_table(),
        )
        md = render_element(element)
        assert "| Property | Value |" in md
        assert "| Thickness | 12.5 mm |" in md

    def test_render_table_element_fallback_when_no_table_data(self):
        element = CanonicalElement(
            element_id="e7",
            element_type="table",
            text="raw table text",
            page_number=1,
            reading_order=6,
            table=None,
        )
        md = render_element(element)
        assert DEGRADED_TABLE_MARKER in md
        assert "raw table text" in md

    def test_render_table_caption(self):
        element = CanonicalElement(
            element_id="e8",
            element_type="table_caption",
            text="Table 1: Specs",
            page_number=1,
            reading_order=7,
        )
        md = render_element(element)
        assert md == "*Table 1: Specs*"

    def test_render_figure(self):
        element = CanonicalElement(
            element_id="e9",
            element_type="figure",
            text="figure1.png",
            page_number=1,
            reading_order=8,
        )
        md = render_element(element)
        assert md == "![figure1.png](figure1.png)"

    def test_render_figure_caption(self):
        element = CanonicalElement(
            element_id="e10",
            element_type="figure_caption",
            text="Figure 1: Diagram",
            page_number=1,
            reading_order=9,
        )
        md = render_element(element)
        assert md == "*Figure: Figure 1: Diagram*"

    def test_render_header(self):
        element = CanonicalElement(
            element_id="e11",
            element_type="header",
            text="Header text",
            page_number=1,
            reading_order=10,
        )
        md = render_element(element)
        assert md == "<!-- header: Header text -->"

    def test_render_footer(self):
        element = CanonicalElement(
            element_id="e12",
            element_type="footer",
            text="Footer text",
            page_number=1,
            reading_order=11,
        )
        md = render_element(element)
        assert md == "<!-- footer: Footer text -->"

    def test_render_unknown_element(self):
        element = CanonicalElement(
            element_id="e13",
            element_type="unknown",
            text="unknown content",
            page_number=1,
            reading_order=12,
        )
        md = render_element(element)
        assert UNKNOWN_ELEMENT_MARKER in md
        assert "unknown content" in md


class TestRenderPage:
    def test_render_page_includes_page_marker(self):
        page = CanonicalPage(
            page_number=3,
            page_width=595.0,
            page_height=842.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="page content",
            ordered_elements=[],
        )
        md = render_pages([page])
        assert f"{PAGE_MARKER_PREFIX}3{PAGE_MARKER_SUFFIX}" in md

    def test_render_page_preserves_reading_order(self):
        elements = [
            CanonicalElement(
                element_id="e1",
                element_type="paragraph",
                text="First",
                page_number=1,
                reading_order=2,
            ),
            CanonicalElement(
                element_id="e2",
                element_type="paragraph",
                text="Second",
                page_number=1,
                reading_order=1,
            ),
        ]
        page = CanonicalPage(
            page_number=1,
            page_width=595.0,
            page_height=842.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="",
            ordered_elements=elements,
        )
        md = render_pages([page])
        first_pos = md.index("First")
        second_pos = md.index("Second")
        assert second_pos < first_pos

    def test_render_page_includes_warnings(self):
        page = CanonicalPage(
            page_number=1,
            page_width=595.0,
            page_height=842.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="",
            ordered_elements=[],
            warnings=["Page warning 1", "Page warning 2"],
        )
        md = render_pages([page])
        assert "**Warning:** Page warning 1" in md
        assert "**Warning:** Page warning 2" in md

    def test_render_page_raw_text_fallback_when_no_elements(self):
        page = CanonicalPage(
            page_number=1,
            page_width=595.0,
            page_height=842.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="Raw fallback text",
            ordered_elements=[],
        )
        md = render_pages([page])
        assert "### Raw text fallback" in md
        assert "Raw fallback text" in md

    def test_render_page_no_raw_text_fallback_when_elements_exist(self):
        page = CanonicalPage(
            page_number=1,
            page_width=595.0,
            page_height=842.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="Should not appear",
            ordered_elements=[
                CanonicalElement(
                    element_id="e1",
                    element_type="paragraph",
                    text="Real content",
                    page_number=1,
                    reading_order=0,
                )
            ],
        )
        md = render_pages([page])
        assert "Should not appear" not in md
        assert "Real content" in md

    def test_render_failed_page_includes_errors_and_raw_text(self):
        page = CanonicalPage(
            page_number=1,
            page_width=595.0,
            page_height=842.0,
            classification="EXTRACTION_FAILED",
            backend_used="pymupdf",
            extraction_status="failed",
            raw_text="Raw text from failed extraction",
            ordered_elements=[],
            errors=["Extraction error"],
            warnings=["Extraction warning"],
        )
        md = render_pages([page])
        assert "**Extraction status:** failed" in md
        assert "**Error:** Extraction error" in md
        assert "**Warning:** Extraction warning" in md
        assert "### Raw text fallback" in md
        assert "Raw text from failed extraction" in md


class TestRenderDocument:
    def test_render_document_preserves_order(self):
        doc = make_document()
        md = render_document(doc)

        assert "# Document: product.pdf" in md
        assert "**Document ID:** document-1" in md
        assert "**Schema version:** 1.0" in md
        assert "**Extraction status:** success" in md
        assert "**Page count:** 1" in md
        assert "**Source path:** /documents/product.pdf" in md
        assert "**Source URL:** https://example.com/product.pdf" in md
        assert "**Warning:** Document warning" in md
        assert f"{PAGE_MARKER_PREFIX}1{PAGE_MARKER_SUFFIX}" in md
        assert "| Property | Value |" in md

    def test_render_document_page_order(self):
        page1 = CanonicalPage(
            page_number=1,
            page_width=595.0,
            page_height=842.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="Page 1",
            ordered_elements=[
                CanonicalElement(
                    element_id="e1",
                    element_type="paragraph",
                    text="Page 1 content",
                    page_number=1,
                    reading_order=0,
                )
            ],
        )
        page2 = CanonicalPage(
            page_number=2,
            page_width=595.0,
            page_height=842.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="Page 2",
            ordered_elements=[
                CanonicalElement(
                    element_id="e2",
                    element_type="paragraph",
                    text="Page 2 content",
                    page_number=2,
                    reading_order=0,
                )
            ],
        )
        doc = CanonicalDocument(
            schema_version=SCHEMA_VERSION,
            document_id="doc-1",
            source_path="/test.pdf",
            file_name="test.pdf",
            page_count=2,
            extraction_status="success",
            pages=[page1, page2],
        )
        md = render_document(doc)
        page1_pos = md.index("[Page 1]")
        page2_pos = md.index("[Page 2]")
        assert page1_pos < page2_pos

    def test_render_document_includes_document_warnings_and_errors(self):
        doc = CanonicalDocument(
            schema_version=SCHEMA_VERSION,
            document_id="doc-1",
            source_path="/test.pdf",
            file_name="test.pdf",
            page_count=1,
            extraction_status="success",
            warnings=["Doc warning"],
            errors=["Doc error"],
            pages=[
                CanonicalPage(
                    page_number=1,
                    page_width=595.0,
                    page_height=842.0,
                    classification="DIGITAL_SIMPLE",
                    backend_used="pymupdf",
                    extraction_status="success",
                    raw_text="",
                    ordered_elements=[],
                )
            ],
        )
        md = render_document(doc)
        assert "**Warning:** Doc warning" in md
        assert "**Error:** Doc error" in md


class TestRendererIntegration:
    def test_full_document_with_multiple_element_types(self):
        elements = [
            CanonicalElement(
                element_id="e1",
                element_type="title",
                text="Main Title",
                page_number=1,
                reading_order=0,
            ),
            CanonicalElement(
                element_id="e2",
                element_type="heading",
                text="Section",
                page_number=1,
                reading_order=1,
            ),
            CanonicalElement(
                element_id="e3",
                element_type="paragraph",
                text="Paragraph text.",
                page_number=1,
                reading_order=2,
            ),
            CanonicalElement(
                element_id="e4",
                element_type="list",
                text="Item 1\nItem 2",
                page_number=1,
                reading_order=3,
            ),
            CanonicalElement(
                element_id="e5",
                element_type="table",
                text="fallback",
                page_number=1,
                reading_order=4,
                table=make_table(),
            ),
            CanonicalElement(
                element_id="e6",
                element_type="table_caption",
                text="Table 1: Data",
                page_number=1,
                reading_order=5,
            ),
            CanonicalElement(
                element_id="e7",
                element_type="figure",
                text="diagram.png",
                page_number=1,
                reading_order=6,
            ),
            CanonicalElement(
                element_id="e8",
                element_type="figure_caption",
                text="Figure 1: Diagram",
                page_number=1,
                reading_order=7,
            ),
        ]
        page = CanonicalPage(
            page_number=1,
            page_width=595.0,
            page_height=842.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="",
            ordered_elements=elements,
        )
        doc = CanonicalDocument(
            schema_version=SCHEMA_VERSION,
            document_id="doc-1",
            source_path="/test.pdf",
            file_name="test.pdf",
            page_count=1,
            extraction_status="success",
            pages=[page],
        )
        md = render_document(doc)

        assert "# Main Title" in md
        assert "## Section" in md
        assert "Paragraph text." in md
        assert "- Item 1" in md
        assert "- Item 2" in md
        assert "| Property | Value |" in md
        assert "*Table 1: Data*" in md
        assert "![diagram.png](diagram.png)" in md
        assert "*Figure: Figure 1: Diagram*" in md

    def test_renderer_does_not_modify_technical_values(self):
        table = TableData(
            table_id="t1",
            headers=["Property", "Value"],
            rows=[["Density", "650 kg/m3"], ["Thickness", "12.5 mm"]],
            page_number=1,
        )
        md = render_table(table)
        assert "650 kg/m3" in md
        assert "12.5 mm" in md

    def test_renderer_output_ends_with_newline(self):
        doc = make_document()
        md = render_document(doc)
        assert md.endswith("\n")