from __future__ import annotations

import math
from typing import Any, Literal, Self

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StrictFloat,
    StrictStr,
    field_validator,
)

from app.ai.extraction.base import ExtractionResult

SCHEMA_VERSION = "1.0"

ElementType = Literal[
    "title",
    "heading",
    "paragraph",
    "list",
    "table",
    "table_caption",
    "figure",
    "figure_caption",
    "header",
    "footer",
    "unknown",
]

SUPPORTED_ELEMENT_TYPES = (
    "title",
    "heading",
    "paragraph",
    "list",
    "table",
    "table_caption",
    "figure",
    "figure_caption",
    "header",
    "footer",
    "unknown",
)


class CanonicalModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def to_json(self, **kwargs: Any) -> str:
        return self.model_dump_json(**kwargs)

    @classmethod
    def from_json(cls, value: str) -> Self:
        return cls.model_validate_json(value)


class TableData(CanonicalModel):
    table_id: StrictStr
    caption: StrictStr | None = None
    headers: list[StrictStr] = Field(default_factory=list)
    rows: list[list[StrictStr]] = Field(default_factory=list)
    page_number: int = Field(ge=1)
    bounding_box: list[float] | None = None
    warnings: list[StrictStr] = Field(
        default_factory=list,
        validation_alias=AliasChoices("warnings", "extraction_warnings"),
    )

    @property
    def extraction_warnings(self) -> list[StrictStr]:
        return self.warnings

    @field_validator("bounding_box", mode="before")
    @classmethod
    def validate_bounding_box(cls, value: Any) -> list[float] | None:
        if value is None:
            return None
        if not isinstance(value, (list, tuple)) or len(value) != 4:
            raise ValueError("bounding_box must contain four coordinates")

        coordinates: list[float] = []
        for coordinate in value:
            if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
                raise ValueError("bounding_box coordinates must be finite numbers")
            number = float(coordinate)
            if not math.isfinite(number):
                raise ValueError("bounding_box coordinates must be finite numbers")
            coordinates.append(number)
        return coordinates


class CanonicalElement(CanonicalModel):
    element_id: StrictStr
    element_type: ElementType
    text: StrictStr
    page_number: int = Field(ge=1)
    reading_order: int = Field(ge=0)
    bounding_box: list[float] | None = None
    confidence: StrictFloat | None = Field(
        default=None,
        ge=0,
        le=1,
        allow_inf_nan=False,
    )
    metadata: dict[str, JsonValue] | None = None
    table: TableData | None = Field(
        default=None,
        validation_alias=AliasChoices("table", "table_data"),
    )

    @field_validator("bounding_box", mode="before")
    @classmethod
    def validate_bounding_box(cls, value: Any) -> list[float] | None:
        if value is None:
            return None
        if not isinstance(value, (list, tuple)) or len(value) != 4:
            raise ValueError("bounding_box must contain four coordinates")

        coordinates: list[float] = []
        for coordinate in value:
            if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
                raise ValueError("bounding_box coordinates must be finite numbers")
            number = float(coordinate)
            if not math.isfinite(number):
                raise ValueError("bounding_box coordinates must be finite numbers")
            coordinates.append(number)
        return coordinates

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict[str, JsonValue] | None) -> dict[str, JsonValue] | None:
        return value

    @property
    def table_data(self) -> TableData | None:
        return self.table


class CanonicalPage(CanonicalModel):
    page_number: int = Field(ge=1)
    page_width: StrictFloat = Field(ge=0, allow_inf_nan=False)
    page_height: StrictFloat = Field(ge=0, allow_inf_nan=False)
    classification: StrictStr
    backend_used: StrictStr
    extraction_status: StrictStr
    raw_text: StrictStr
    ordered_elements: list[CanonicalElement] = Field(default_factory=list)
    warnings: list[StrictStr] = Field(default_factory=list)
    errors: list[StrictStr] = Field(default_factory=list)

    @classmethod
    def from_extraction_result(
        cls,
        result: ExtractionResult,
        *,
        classification: StrictStr,
        page_width: float,
        page_height: float,
    ) -> Self:
        return cls(
            page_number=result.page_number,
            page_width=page_width,
            page_height=page_height,
            classification=classification,
            backend_used=result.backend_name,
            extraction_status="success" if result.success else "failed",
            raw_text=result.content,
            warnings=list(result.warnings),
            errors=list(result.errors),
        )


class CanonicalDocument(CanonicalModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    document_id: StrictStr
    source_path: StrictStr
    source_url: StrictStr | None = None
    file_name: StrictStr
    file_hash: StrictStr | None = None
    page_count: int = Field(ge=0)
    extraction_status: StrictStr
    warnings: list[StrictStr] = Field(default_factory=list)
    errors: list[StrictStr] = Field(default_factory=list)
    pages: list[CanonicalPage] = Field(default_factory=list)


DocumentExtraction = CanonicalDocument
PageExtraction = CanonicalPage
ElementExtraction = CanonicalElement
TableExtraction = TableData

Document = CanonicalDocument
Page = CanonicalPage
Element = CanonicalElement
Table = TableData

DocumentSchema = CanonicalDocument
PageSchema = CanonicalPage
ElementSchema = CanonicalElement
TableSchema = TableData

__all__ = [
    "SCHEMA_VERSION",
    "ElementType",
    "SUPPORTED_ELEMENT_TYPES",
    "CanonicalModel",
    "TableData",
    "CanonicalElement",
    "CanonicalPage",
    "CanonicalDocument",
    "DocumentExtraction",
    "PageExtraction",
    "ElementExtraction",
    "TableExtraction",
    "Document",
    "Page",
    "Element",
    "Table",
    "DocumentSchema",
    "PageSchema",
    "ElementSchema",
    "TableSchema",
]
