from __future__ import annotations

import json
from dataclasses import asdict

import pytest
from pydantic import ValidationError

from app.ai.extraction.base import ExtractionResult
from app.ai.extraction.schema import (
    SCHEMA_VERSION,
    CanonicalDocument,
    CanonicalElement,
    CanonicalPage,
    TableData,
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


class TestCanonicalDocument:
    def test_valid_document_result(self):
        document = make_document()

        assert document.schema_version == "1.0"
        assert document.document_id == "document-1"
        assert document.source_path == "/documents/product.pdf"
        assert document.source_url == "https://example.com/product.pdf"
        assert document.file_name == "product.pdf"
        assert document.file_hash == "sha256:example"
        assert document.page_count == 1
        assert document.extraction_status == "success"
        assert document.warnings == ["Document warning"]
        assert document.errors == []
        assert len(document.pages) == 1

    def test_json_serialization_and_deserialization(self):
        document = make_document()

        payload = document.to_dict()
        assert json.loads(json.dumps(payload, allow_nan=False)) == payload
        restored = CanonicalDocument.from_json(document.to_json())

        assert restored == document
        assert restored.pages[0].ordered_elements[0].table is not None

    def test_missing_optional_fields(self):
        element = CanonicalElement(
            element_id="element-1",
            element_type="unknown",
            text="",
            page_number=1,
            reading_order=0,
        )
        page = CanonicalPage(
            page_number=1,
            page_width=1.0,
            page_height=1.0,
            classification="MANUAL_REVIEW",
            backend_used="manual_review",
            extraction_status="failed",
            raw_text="",
            ordered_elements=[element],
        )
        document = CanonicalDocument(
            document_id="document-1",
            source_path="/documents/empty.pdf",
            file_name="empty.pdf",
            page_count=1,
            extraction_status="failed",
            pages=[page],
        )

        assert document.source_url is None
        assert document.file_hash is None
        assert element.bounding_box is None
        assert element.confidence is None
        assert element.metadata is None
        assert element.table is None


class TestCanonicalPage:
    def test_valid_page_result(self):
        page = make_document().pages[0]

        assert page.page_number == 1
        assert page.page_width == 595.0
        assert page.page_height == 842.0
        assert page.classification == "DIGITAL_SIMPLE"
        assert page.backend_used == "pymupdf"
        assert page.extraction_status == "success"
        assert page.raw_text.startswith("Technical specifications")

    def test_ordered_elements(self):
        page = make_document().pages[0]

        assert [element.reading_order for element in page.ordered_elements] == [2]
        assert page.ordered_elements[0].element_id == "element-1"

    def test_warnings_and_errors_are_preserved(self):
        page = CanonicalPage(
            page_number=1,
            page_width=1.0,
            page_height=2.0,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="failed",
            raw_text="raw",
            warnings=["page warning"],
            errors=["page error"],
        )

        assert page.warnings == ["page warning"]
        assert page.errors == ["page error"]

    def test_failed_extraction_result_compatibility(self):
        legacy_result = ExtractionResult(
            page_number=3,
            content="raw legacy text",
            metadata={"legacy": True},
            warnings=["legacy warning"],
            errors=["legacy error"],
            backend_name="pymupdf",
            success=False,
        )

        page = CanonicalPage.from_extraction_result(
            legacy_result,
            classification="EXTRACTION_FAILED",
            page_width=0.0,
            page_height=0.0,
        )

        assert page.page_number == 3
        assert page.raw_text == "raw legacy text"
        assert page.backend_used == "pymupdf"
        assert page.extraction_status == "failed"
        assert page.warnings == ["legacy warning"]
        assert page.errors == ["legacy error"]
        assert legacy_result.metadata == {"legacy": True}


class TestTableData:
    def test_table_structure(self):
        table = make_table()

        assert table.table_id == "table-1"
        assert table.caption == "Technical specifications"
        assert table.headers == ["Property", "Value"]
        assert table.rows == [["Thickness", "12.5 mm"], ["Density", "650 kg/m3"]]
        assert table.page_number == 1
        assert table.bounding_box == [10.0, 20.0, 300.0, 180.0]
        assert table.warnings == ["Table structure requires review"]
        assert table.extraction_warnings == table.warnings

    def test_table_optional_fields_and_warning_alias(self):
        table = TableData(
            table_id="table-1",
            headers=[],
            rows=[],
            page_number=2,
            extraction_warnings=["No table structure detected"],
        )

        assert table.caption is None
        assert table.bounding_box is None
        assert table.warnings == ["No table structure detected"]


class TestExtractionResultCompatibility:
    def test_existing_result_remains_a_dataclass_result(self):
        result = ExtractionResult(
            page_number=1,
            content="legacy content",
            metadata={"key": "value"},
            warnings=["warning"],
            errors=["error"],
            backend_name="test",
            success=False,
        )

        assert asdict(result) == {
            "page_number": 1,
            "content": "legacy content",
            "metadata": {"key": "value"},
            "warnings": ["warning"],
            "errors": ["error"],
            "backend_name": "test",
            "success": False,
        }


def test_unsupported_element_type_is_rejected():
    with pytest.raises(ValidationError):
        CanonicalElement(
            element_id="element-1",
            element_type="image",
            text="not supported",
            page_number=1,
            reading_order=0,
        )


@pytest.mark.parametrize("field", ["page_width", "page_height"])
@pytest.mark.parametrize(
    "value",
    ["1.0", True, -1.0, float("inf"), float("-inf"), float("nan")],
)
def test_page_dimensions_reject_strings_bools_and_non_finite_values(field, value):
    values = {"page_width": 1.0, "page_height": 1.0}
    values[field] = value

    with pytest.raises(ValidationError):
        CanonicalPage(
            page_number=1,
            classification="DIGITAL_SIMPLE",
            backend_used="pymupdf",
            extraction_status="success",
            raw_text="",
            **values,
        )


@pytest.mark.parametrize(
    "value",
    ["0.5", True, -0.1, 1.1, float("inf"), float("-inf"), float("nan")],
)
def test_confidence_rejects_strings_bools_and_non_finite_values(value):
    with pytest.raises(ValidationError):
        CanonicalElement(
            element_id="element-1",
            element_type="paragraph",
            text="text",
            page_number=1,
            reading_order=0,
            confidence=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        ["1.0", 2.0, 3.0, 4.0],
        [True, 2.0, 3.0, 4.0],
        [1.0, 2.0, 3.0],
        [1.0, 2.0, 3.0, float("inf")],
        [1.0, 2.0, 3.0, float("nan")],
    ],
)
def test_bounding_box_rejects_strings_bools_and_non_finite_values(value):
    with pytest.raises(ValidationError):
        CanonicalElement(
            element_id="element-1",
            element_type="paragraph",
            text="text",
            page_number=1,
            reading_order=0,
            bounding_box=value,
        )
