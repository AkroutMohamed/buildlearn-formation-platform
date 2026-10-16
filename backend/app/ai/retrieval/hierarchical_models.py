"""Retrieval evidence, independent of generation and legacy ChunkResponse."""
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RetrievedChild:
    chunk_id: str
    score: float
    text: str
    document_id: str
    file_name: str
    source_path: str
    parent_id: str | None
    section_path: list[str]
    page_start: int | None
    page_end: int | None
    block_type: str
    parent_id_path: list[str] | None = None
    parent_id_path_source: str = "unavailable"
    payload_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParentEvidence:
    parent_id: str
    text: str
    document_id: str
    file_name: str
    source_path: str
    section_path: list[str]
    page_start: int | None
    page_end: int | None
    block_type: str


@dataclass
class SourceResolution:
    parent_id_path: list[str]
    parents: list[ParentEvidence] = field(default_factory=list)


@dataclass
class ContextFragment:
    text: str
    chunk_ids: list[str]
    page_start: int | None
    page_end: int | None
    block_type: str


@dataclass
class RetrievedContext:
    document_id: str
    file_name: str
    source_path: str
    parent_id: str | None
    parent_id_path: list[str] | None
    section_path: list[str]
    page_start: int | None
    page_end: int | None
    chunk_ids: list[str]
    fragments: list[ContextFragment]
    parents: list[ParentEvidence] = field(default_factory=list)


@dataclass
class RetrievalResponse:
    hits: list[RetrievedChild]
    contexts: list[RetrievedContext]
    context_text: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
