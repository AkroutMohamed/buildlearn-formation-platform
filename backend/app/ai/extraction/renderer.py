from __future__ import annotations

from typing import Any, Iterable

from app.ai.extraction.schema import (
    CanonicalDocument,
    CanonicalElement,
    CanonicalPage,
    ElementType,
    TableData,
)

PAGE_MARKER_PREFIX = "[Page "
PAGE_MARKER_SUFFIX = "]"
DEGRADED_TABLE_MARKER = "[DEGRADED TABLE]"
UNKNOWN_ELEMENT_MARKER = "[UNKNOWN ELEMENT]"


def _escape_md_table_cell(text: str) -> str:
    """Escape pipe characters and newlines inside Markdown table cells."""
    if not text:
        return ""
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _render_table(table: TableData) -> list[str]:
    """Render a TableData object as Markdown table lines.

    If the table has no headers and no rows, returns a degraded marker with
    the raw text fallback so content is never silently discarded.
    """
    lines: list[str] = []
    if not table.headers and not table.rows:
        lines.append(DEGRADED_TABLE_MARKER)
        return lines

    headers = list(table.headers)
    rows = [list(row) for row in table.rows]

    max_cols = max((len(headers), *(len(r) for r in rows)))
    if max_cols == 0:
        lines.append(DEGRADED_TABLE_MARKER)
        return lines

    # Pad headers and rows to the same width without inventing content.
    headers = headers + [""] * (max_cols - len(headers))
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    header_line = "| " + " | ".join(_escape_md_table_cell(h) for h in headers) + " |"
    separator_line = "|" + "|".join(["---"] * max_cols) + "|"
    lines.append(header_line)
    lines.append(separator_line)

    for row in rows:
        row_line = "| " + " | ".join(_escape_md_table_cell(c) for c in row) + " |"
        lines.append(row_line)

    return lines


def _render_element(element: CanonicalElement) -> list[str]:
    """Render a single CanonicalElement to Markdown lines."""
    etype = element.element_type
    text = element.text

    if etype == "title":
        return [f"# {text}"]
    if etype == "heading":
        return [f"## {text}"]
    if etype == "paragraph":
        return [text]
    if etype == "list":
        items = text.splitlines()
        rendered: list[str] = []
        for item in items:
            stripped = item.strip()
            if not stripped:
                continue
            if stripped.startswith(("-", "*", "•")):
                rendered.append(stripped)
            else:
                rendered.append(f"- {stripped}")
        if not rendered:
            rendered.append(f"- {text}")
        return rendered
    if etype == "table":
        if element.table is not None:
            return _render_table(element.table)
        # Fallback: preserve raw text with a degradation marker.
        return [DEGRADED_TABLE_MARKER, text]
    if etype == "table_caption":
        return [f"*{text}*"]
    if etype == "figure":
        return [f"![{text}]({text})"]
    if etype == "figure_caption":
        return [f"*Figure: {text}*"]
    if etype == "header":
        return [f"<!-- header: {text} -->"]
    if etype == "footer":
        return [f"<!-- footer: {text} -->"]
    # unknown
    return [f"{UNKNOWN_ELEMENT_MARKER} {text}"]


def _render_page(
    page: CanonicalPage,
    *,
    include_raw_text_fallback: bool = True,
) -> list[str]:
    """Render a single CanonicalPage to Markdown lines."""
    lines: list[str] = []
    lines.append(f"{PAGE_MARKER_PREFIX}{page.page_number}{PAGE_MARKER_SUFFIX}")

    if page.extraction_status != "success":
        lines.append(f"**Extraction status:** {page.extraction_status}")
        if page.errors:
            for err in page.errors:
                lines.append(f"**Error:** {err}")
        if page.warnings:
            for warn in page.warnings:
                lines.append(f"**Warning:** {warn}")
        if include_raw_text_fallback and page.raw_text:
            lines.append("### Raw text fallback")
            lines.append(page.raw_text)
        return lines

    ordered = sorted(
        page.ordered_elements,
        key=lambda e: (e.reading_order, e.element_id),
    )
    for element in ordered:
        lines.extend(_render_element(element))

    if page.warnings:
        for warn in page.warnings:
            lines.append(f"**Warning:** {warn}")

    if include_raw_text_fallback and page.raw_text and not page.ordered_elements:
        lines.append("### Raw text fallback")
        lines.append(page.raw_text)

    return lines


def render_document(
    document: CanonicalDocument,
    *,
    include_raw_text_fallback: bool = True,
) -> str:
    """Render a CanonicalDocument to a Markdown string.

    Preserves document and page order, element reading order, page numbers,
    titles, headings, paragraphs, lists, tables, figure captions, headers/
    footers, raw text fallback, and extraction warnings.

    The renderer only produces text. It does not split, overlap, embed, index,
    or send data to Qdrant.
    """
    lines: list[str] = []

    lines.append(f"# Document: {document.file_name}")
    lines.append("")
    lines.append(f"**Document ID:** {document.document_id}")
    lines.append(f"**Schema version:** {document.schema_version}")
    lines.append(f"**Extraction status:** {document.extraction_status}")
    lines.append(f"**Page count:** {document.page_count}")
    if document.source_path:
        lines.append(f"**Source path:** {document.source_path}")
    if document.source_url:
        lines.append(f"**Source URL:** {document.source_url}")
    if document.warnings:
        for warn in document.warnings:
            lines.append(f"**Warning:** {warn}")
    if document.errors:
        for err in document.errors:
            lines.append(f"**Error:** {err}")
    lines.append("")

    for page in document.pages:
        lines.extend(_render_page(page, include_raw_text_fallback=include_raw_text_fallback))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_pages(
    pages: Iterable[CanonicalPage],
    *,
    include_raw_text_fallback: bool = True,
) -> str:
    """Render an iterable of CanonicalPage objects to a Markdown string."""
    lines: list[str] = []
    for page in pages:
        lines.extend(_render_page(page, include_raw_text_fallback=include_raw_text_fallback))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_element(element: CanonicalElement) -> str:
    """Render a single CanonicalElement to a Markdown string."""
    return "\n".join(_render_element(element))


def render_table(table: TableData) -> str:
    """Render a single TableData object to a Markdown string."""
    return "\n".join(_render_table(table))