from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.ai.chunking.config import ChunkConfig


class BlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    TABLE = "table"
    KEY_VALUE = "key_value"
    CAPTION = "caption"
    RAW_TEXT = "raw_text"
    PAGE_BREAK = "page_break"
    UNKNOWN = "unknown"


class HierarchyLevel(str, Enum):
    DOCUMENT = "document"
    SECTION = "section"
    SUBSECTION = "subsection"
    BLOCK = "block"


@dataclass
class SourceInfo:
    source_path: Optional[str] = None
    document_id: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    file_name: Optional[str] = None
    file_hash: Optional[str] = None


def _deterministic_id(*parts: str) -> str:
    raw = "|".join(str(p) for p in parts if p)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


@dataclass
class SemanticBlock:
    block_id: str
    block_type: BlockType
    text: str
    source: SourceInfo
    section_path: list[str] = field(default_factory=list)
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    parent_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    config: ChunkConfig = field(default_factory=ChunkConfig)

    @classmethod
    def from_text(
        cls,
        text: str,
        block_type: BlockType,
        source: SourceInfo,
        section_path: Optional[list[str]] = None,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
        parent_id: Optional[str] = None,
        config: ChunkConfig = field(default_factory=ChunkConfig),
    ) -> "SemanticBlock":
        block_id = _deterministic_id(
            source.document_id or "",
            source.source_path or "",
            str(page_start or ""),
            str(page_end or ""),
            block_type.value,
            text[:200],
        )
        return cls(
            block_id=block_id,
            block_type=block_type,
            text=text,
            source=source,
            section_path=section_path or [],
            page_start=page_start,
            page_end=page_end,
            parent_id=parent_id,
            config=config,
        )


@dataclass
class ParentChunk:
    chunk_id: str
    chunk_type: BlockType
    text: str
    source: SourceInfo
    section_path: list[str] = field(default_factory=list)
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    level: HierarchyLevel = HierarchyLevel.SECTION
    children: list[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    config: ChunkConfig = field(default_factory=ChunkConfig)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_block(
        cls,
        block: SemanticBlock,
        level: HierarchyLevel = HierarchyLevel.SECTION,
        children: Optional[list[str]] = None,
        parent_id: Optional[str] = None,
    ) -> "ParentChunk":
        chunk_id = _deterministic_id(
            block.source.document_id or "",
            block.source.source_path or "",
            str(block.page_start or ""),
            str(block.page_end or ""),
            "parent",
            block.block_type.value,
            block.text[:100],
            "|".join(block.section_path),
        )
        return cls(
            chunk_id=chunk_id,
            chunk_type=block.block_type,
            text=block.text,
            source=block.source,
            section_path=block.section_path,
            page_start=block.page_start,
            page_end=block.page_end,
            level=level,
            children=children or [],
            parent_id=parent_id,
            config=block.config,
            created_at=datetime.utcnow(),
        )

    @property
    def is_embeddable(self) -> bool:
        return False


@dataclass
class ChildChunk:
    chunk_id: str
    chunk_type: BlockType
    text: str
    source: SourceInfo
    section_path: list[str] = field(default_factory=list)
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    parent_id: Optional[str] = None
    parent_id_path: list[str] = field(default_factory=list)
    block_type: BlockType = BlockType.RAW_TEXT
    metadata: dict[str, Any] = field(default_factory=dict)
    config: ChunkConfig = field(default_factory=ChunkConfig)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_embeddable(self) -> bool:
        return True

    @property
    def char_count(self) -> int:
        return len(self.text)

    @property
    def word_count(self) -> int:
        return len(self.text.split())


@dataclass
class ChunkResult:
    parents: list[ParentChunk] = field(default_factory=list)
    children: list[ChildChunk] = field(default_factory=list)
    source_info: Optional[SourceInfo] = None
    config: ChunkConfig = field(default_factory=ChunkConfig)

    @property
    def total_parents(self) -> int:
        return len(self.parents)

    @property
    def total_children(self) -> int:
        return len(self.children)

    @property
    def size_distribution(self) -> dict[str, Any]:
        sizes = [c.char_count for c in self.children]
        if not sizes:
            return {"min": 0, "max": 0, "mean": 0, "count": 0}
        return {
            "min": min(sizes),
            "max": max(sizes),
            "mean": sum(sizes) / len(sizes),
            "count": len(sizes),
        }

    @property
    def structure_type_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for c in self.children:
            t = c.block_type.value
            dist[t] = dist.get(t, 0) + 1
        return dist

    def to_chunk_create_list(self) -> list:
        from app.ai.schemas.chunk import ChunkCreate
        result: list[ChunkCreate] = []
        for child in self.children:
            chunk = ChunkCreate(
                chunk_id=child.chunk_id,
                document_id=child.source.document_id,
                product_id=None,
                product_name=None,
                supplier=None,
                source=child.source.source_path,
                source_url=None,
                document_url=None,
                document_type=None,
                page_number=child.page_start,
                section_title=" / ".join(child.section_path) if child.section_path else None,
                chunk_index=0,
                text=child.text,
                language=None,
                content_hash=None,
                metadata={
                    **child.metadata,
                    "parent_id": child.parent_id,
                    "block_type": child.block_type.value,
                    "char_count": child.char_count,
                    "word_count": child.word_count,
                    "section_path": child.section_path,
                    "page_start": child.page_start,
                    "page_end": child.page_end,
                },
                source_type=None,
                discovery_provider=None,
                domain=None,
                confidence=None,
                evidence=None,
            )
            result.append(chunk)
        return result
