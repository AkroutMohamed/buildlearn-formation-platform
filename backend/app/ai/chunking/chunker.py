from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime
from typing import Optional

from app.ai.chunking.config import ChunkConfig
from app.ai.chunking.hierarchy import build_hierarchy
from app.ai.chunking.models import (
    BlockType,
    ChildChunk,
    ChunkResult,
    ParentChunk,
    SemanticBlock,
    SourceInfo,
)

logger = logging.getLogger(__name__)


class HierarchicalChunker:
    CONTAINER_TYPES = frozenset((
        BlockType.HEADING,
        BlockType.LIST,
        BlockType.TABLE,
        BlockType.KEY_VALUE,
    ))

    def __init__(self, config: Optional[ChunkConfig] = None) -> None:
        self.config = config or ChunkConfig()

    def chunk_from_dict(self, document: dict) -> ChunkResult:
        source = self._extract_source_from_dict(document)
        pages = document.get("pages", [])
        if not isinstance(pages, list):
            return ChunkResult(source_info=source, config=self.config)

        parents: list[ParentChunk] = []
        children: list[ChildChunk] = []
        chunk_index = 0

        for page in pages:
            if not isinstance(page, dict):
                continue
            page_number = page.get("page_number", 1)
            raw_text = page.get("raw_text", "")
            if not isinstance(raw_text, str) or not raw_text.strip():
                continue

            blocks = build_hierarchy(raw_text, source, page_number, self.config)
            page_parents, page_children = self._process_blocks(
                blocks, source, page_number, chunk_index,
            )
            parents.extend(page_parents)
            children.extend(page_children)
            chunk_index += len(page_children)

        return ChunkResult(
            parents=parents,
            children=children,
            source_info=source,
            config=self.config,
        )

    def chunk_from_object(self, document: object) -> ChunkResult:
        data = self._extract_from_object(document)
        if isinstance(data, dict):
            return self.chunk_from_dict(data)
        return ChunkResult(source_info=None, config=self.config)

    def _process_blocks(
        self,
        blocks: list[SemanticBlock],
        source: SourceInfo,
        page_number: int,
        start_index: int,
    ) -> tuple[list[ParentChunk], list[ChildChunk]]:
        parents: list[ParentChunk] = []
        children: list[ChildChunk] = []
        index = start_index
        block_to_parent: dict[str, str] = {}
        used_ids: set[str] = set()

        def _unique_id(chunk_id: str) -> str:
            if chunk_id not in used_ids:
                return chunk_id
            counter = 1
            while True:
                candidate = f"{chunk_id}_{counter}"
                if candidate not in used_ids:
                    return candidate
                counter += 1

        for block in blocks:
            if block.block_type == BlockType.PAGE_BREAK:
                continue

            if block.block_type in self.CONTAINER_TYPES:
                parent = ParentChunk.from_block(block)
                parent.chunk_id = _unique_id(parent.chunk_id)
                used_ids.add(parent.chunk_id)
                block_to_parent[block.block_id] = parent.chunk_id
                children_of_parent = self._grow_children_for_container(
                    block, parent.chunk_id, source,
                )
                parent.children = [c.chunk_id for c in children_of_parent]
                parents.append(parent)
                for child in children_of_parent:
                    child.chunk_id = _unique_id(child.chunk_id)
                    used_ids.add(child.chunk_id)
                    children.append(child)
                    index += 1
            else:
                resolved_parent_id = block.parent_id
                if resolved_parent_id and resolved_parent_id in block_to_parent:
                    resolved_parent_id = block_to_parent[resolved_parent_id]
                result = self._block_to_child(block, resolved_parent_id, index)
                if result is None:
                    continue
                if isinstance(result, list):
                    for child in result:
                        child.chunk_id = _unique_id(child.chunk_id)
                        used_ids.add(child.chunk_id)
                        children.append(child)
                        index += 1
                else:
                    result.chunk_id = _unique_id(result.chunk_id)
                    used_ids.add(result.chunk_id)
                    children.append(result)
                    index += 1

        parent_map = {p.chunk_id: p for p in parents}
        for child in children:
            pid = child.parent_id
            if pid and pid in parent_map:
                if child.chunk_id not in parent_map[pid].children:
                    parent_map[pid].children.append(child.chunk_id)

        return parents, children

    def _grow_children_for_container(
        self,
        block: SemanticBlock,
        parent_id: str,
        source: SourceInfo,
    ) -> list[ChildChunk]:
        text = block.text.strip()
        if not text:
            return []

        if block.block_type == BlockType.HEADING:
            return []

        if len(text) <= self.config.effective_max:
            return [self._make_child(
                text, parent_id, block.section_path,
                block.page_start, block.page_end,
                block.block_type, source,
                self._child_id(parent_id, block.block_type.value, text[:100], 0),
                block.config,
            )]

        return self._split_container(block, parent_id, source)

    def _split_container(
        self,
        block: SemanticBlock,
        parent_id: str,
        source: SourceInfo,
    ) -> list[ChildChunk]:
        if block.block_type == BlockType.LIST:
            return self._split_list(block, parent_id, source)
        if block.block_type == BlockType.TABLE:
            return self._split_table(block, parent_id, source)
        if block.block_type == BlockType.KEY_VALUE:
            return self._split_key_value(block, parent_id, source)
        return self._split_generic(block, parent_id, source)

    def _split_list(
        self,
        block: SemanticBlock,
        parent_id: str,
        source: SourceInfo,
    ) -> list[ChildChunk]:
        lines = block.text.split("\n")
        children: list[ChildChunk] = []
        current: list[str] = []
        current_len = 0
        index = 0

        for line in lines:
            if _is_list_line(line) and current and current_len > self.config.effective_min:
                child = self._make_child(
                    self.config.separator.join(current),
                    parent_id,
                    block.section_path,
                    block.page_start,
                    block.page_end,
                    BlockType.LIST,
                    source,
                    self._child_id(parent_id, BlockType.LIST.value, current[0][:80], index),
                    block.config,
                )
                children.append(child)
                index += 1
                current = [line]
                current_len = len(line)
            else:
                if current and current_len + len(line) + 1 > self.config.effective_max:
                    child = self._make_child(
                        self.config.separator.join(current),
                        parent_id,
                        block.section_path,
                        block.page_start,
                        block.page_end,
                        BlockType.LIST,
                        source,
                        self._child_id(parent_id, BlockType.LIST.value, current[0][:80], index),
                        block.config,
                    )
                    children.append(child)
                    index += 1
                    current = [line]
                    current_len = len(line)
                else:
                    if current:
                        current_len += len(line) + 1
                    else:
                        current_len = len(line)
                    if not current:
                        current = [line]

        if current:
            child = self._make_child(
                self.config.separator.join(current),
                parent_id,
                block.section_path,
                block.page_start,
                block.page_end,
                BlockType.LIST,
                source,
                self._child_id(parent_id, BlockType.LIST.value, current[0][:80], index),
                block.config,
            )
            children.append(child)

        return children if children else [self._make_child(
            block.text, parent_id, block.section_path,
            block.page_start, block.page_end, BlockType.LIST,
            source, self._child_id(parent_id, BlockType.LIST.value, block.text[:100], 0),
            block.config,
        )]

    def _split_table(
        self,
        block: SemanticBlock,
        parent_id: str,
        source: SourceInfo,
    ) -> list[ChildChunk]:
        lines = block.text.split("\n")
        children: list[ChildChunk] = []
        header_lines: list[str] = []
        data_lines: list[str] = []
        in_header = True

        for line in lines:
            if "|" in line:
                if in_header and (len(data_lines) >= 1 or not any("|" in l for l in data_lines)):
                    header_lines.append(line)
                else:
                    data_lines.append(line)
            else:
                in_header = False
                data_lines.append(line)

        if not header_lines and data_lines:
            header_lines = data_lines[:1]
            data_lines = data_lines[1:]

        current: list[str] = list(header_lines)
        current_len = sum(len(l) for l in current)
        index = 0

        for line in data_lines:
            if current_len + len(line) + 1 > self.config.effective_max and len(current) > len(header_lines):
                child = self._make_child(
                    self.config.separator.join(current),
                    parent_id,
                    block.section_path,
                    block.page_start,
                    block.page_end,
                    BlockType.TABLE,
                    source,
                    self._child_id(parent_id, BlockType.TABLE.value, current[0][:80], index),
                    block.config,
                )
                children.append(child)
                index += 1
                current = list(header_lines) + [line]
                current_len = sum(len(l) for l in current)
            else:
                current.append(line)
                current_len += len(line) + 1

        if current and any("|" in l for l in current):
            child = self._make_child(
                self.config.separator.join(current),
                parent_id,
                block.section_path,
                block.page_start,
                block.page_end,
                BlockType.TABLE,
                source,
                self._child_id(parent_id, BlockType.TABLE.value, current[0][:80], index),
                block.config,
            )
            children.append(child)

        return children if children else [self._make_child(
            block.text, parent_id, block.section_path,
            block.page_start, block.page_end, BlockType.TABLE,
            source, self._child_id(parent_id, BlockType.TABLE.value, block.text[:100], 0),
            block.config,
        )]

    def _split_key_value(
        self,
        block: SemanticBlock,
        parent_id: str,
        source: SourceInfo,
    ) -> list[ChildChunk]:
        lines = block.text.split("\n")
        children: list[ChildChunk] = []
        current: list[str] = []
        current_key: Optional[str] = None
        current_len = 0
        index = 0

        for line in lines:
            key = self._extract_kv_key(line)
            if key:
                if current_key is not None and current and current_len > self.config.effective_min:
                    child = self._make_child(
                        self.config.separator.join(current),
                        parent_id,
                        block.section_path,
                        block.page_start,
                        block.page_end,
                        BlockType.KEY_VALUE,
                        source,
                        self._child_id(parent_id, BlockType.KEY_VALUE.value, current[0][:80], index),
                        block.config,
                    )
                    children.append(child)
                    index += 1
                current = [line]
                current_key = key
                current_len = len(line)
            else:
                if current_key is not None and current_len + len(line) + 1 > self.config.effective_max:
                    child = self._make_child(
                        self.config.separator.join(current),
                        parent_id,
                        block.section_path,
                        block.page_start,
                        block.page_end,
                        BlockType.KEY_VALUE,
                        source,
                        self._child_id(parent_id, BlockType.KEY_VALUE.value, current[0][:80], index),
                        block.config,
                    )
                    children.append(child)
                    index += 1
                    current = [line]
                    current_key = self._extract_kv_key(line) or current_key
                    current_len = len(line)
                else:
                    current.append(line)
                    if current_key is None:
                        current_key = self._extract_kv_key(line)
                    current_len += len(line) + 1

        if current:
            child = self._make_child(
                self.config.separator.join(current),
                parent_id,
                block.section_path,
                block.page_start,
                block.page_end,
                BlockType.KEY_VALUE,
                source,
                self._child_id(parent_id, BlockType.KEY_VALUE.value, current[0][:80], index),
                block.config,
            )
            children.append(child)

        return children if children else [self._make_child(
            block.text, parent_id, block.section_path,
            block.page_start, block.page_end, BlockType.KEY_VALUE,
            source, self._child_id(parent_id, BlockType.KEY_VALUE.value, block.text[:100], 0),
            block.config,
        )]

    def _split_generic(
        self,
        block: SemanticBlock,
        parent_id: str,
        source: SourceInfo,
    ) -> list[ChildChunk]:
        parts = self._safe_split_text(block.text, parent_id, source, block.section_path)
        return parts

    def _block_to_child(
        self,
        block: SemanticBlock,
        parent_id: Optional[str],
        index: int,
    ) -> Optional[ChildChunk | list[ChildChunk]]:
        text = block.text.strip()
        if not text:
            return None

        if len(text) <= self.config.effective_max:
            return self._make_child(
                text, parent_id, block.section_path,
                block.page_start, block.page_end,
                block.block_type, block.source,
                block.block_id, block.config,
            )

        return self._safe_split_text(
            text, parent_id or block.parent_id or "", block.source, block.section_path,
        )

    def _make_child(
        self,
        text: str,
        parent_id: str,
        section_path: list[str],
        page_start: Optional[int],
        page_end: Optional[int],
        block_type: BlockType,
        source: SourceInfo,
        chunk_id: str,
        config: ChunkConfig,
    ) -> ChildChunk:
        return ChildChunk(
            chunk_id=chunk_id,
            chunk_type=block_type,
            text=text,
            source=source,
            section_path=section_path,
            page_start=page_start,
            page_end=page_end,
            parent_id=parent_id,
            block_type=block_type,
            metadata={},
            config=config,
            created_at=datetime.utcnow(),
        )

    def _safe_split_text(
        self,
        text: str,
        parent_id: str,
        source: SourceInfo,
        section_path: list[str],
    ) -> list[ChildChunk]:
        if len(text) <= self.config.effective_max:
            return [self._make_child(
                text, parent_id, section_path, None, None,
                BlockType.RAW_TEXT, source,
                self._child_id(parent_id, BlockType.RAW_TEXT.value, text[:100], 0),
                self.config,
            )]

        by_paragraphs = self._split_by_paragraphs(text)
        if len(by_paragraphs) > 1:
            result = self._greedy_group(by_paragraphs, self.config.effective_max, parent_id, section_path, BlockType.RAW_TEXT, source, self.config)
            if len(result) > 1:
                return result

        by_sentences = self._split_by_sentences(text)
        if len(by_sentences) > 1:
            result = self._greedy_group(by_sentences, self.config.effective_max, parent_id, section_path, BlockType.RAW_TEXT, source, self.config)
            if len(result) > 1:
                return result

        by_words = text.split()
        if len(by_words) > 1:
            result = self._greedy_group(by_words, self.config.effective_max, parent_id, section_path, BlockType.RAW_TEXT, source, self.config)
            if len(result) > 1:
                return result

        chunks = self._greedy_group([text[i:i + self.config.effective_max] for i in range(0, len(text), self.config.effective_max)],
            self.config.effective_max, parent_id, section_path, BlockType.RAW_TEXT, source, self.config)
        if len(chunks) > 1:
            return chunks

        return [self._make_child(
            text[: self.config.effective_max],
            parent_id, section_path, None, None,
            BlockType.RAW_TEXT, source,
            self._child_id(parent_id, BlockType.RAW_TEXT.value, text[:100], 0),
            self.config,
        )]

    def _greedy_group(
        self,
        items: list[str],
        max_size: int,
        parent_id: str,
        section_path: list[str],
        block_type: BlockType,
        source: SourceInfo,
        config: ChunkConfig,
    ) -> list[ChildChunk]:
        result: list[ChildChunk] = []
        current: list[str] = []
        current_len = 0
        index = 0

        for item in items:
            item_len = len(item)
            if item_len > max_size:
                if current:
                    chunk = self._make_child(
                        config.separator.join(current),
                        parent_id, section_path, None, None,
                        block_type, source,
                        self._child_id(parent_id, block_type.value, current[0][:80], index - 1),
                        config,
                    )
                    result.append(chunk)
                    current = []
                    current_len = 0
                chunks = self._greedy_group([item[i:i + max_size] for i in range(0, len(item), max_size)],
                    max_size, parent_id, section_path, block_type, source, config)
                result.extend(chunks)
                continue

            if current_len + item_len + (2 if current else 0) <= max_size:
                current.append(item)
                current_len += item_len + (2 if current else 0)
            else:
                if current:
                    chunk = self._make_child(
                        config.separator.join(current),
                        parent_id, section_path, None, None,
                        block_type, source,
                        self._child_id(parent_id, block_type.value, current[0][:80], index - 1),
                        config,
                    )
                    result.append(chunk)
                current = [item]
                current_len = item_len
                index += 1

        if current:
            chunk = self._make_child(
                config.separator.join(current),
                parent_id, section_path, None, None,
                block_type, source,
                self._child_id(parent_id, block_type.value, current[0][:80], index),
                config,
            )
            result.append(chunk)

        return result

    def _child_id(self, parent_id: str, block_type: str, text_prefix: str, index: int) -> str:
        return _deterministic_child_id(parent_id, block_type, text_prefix, index)

    def _extract_kv_key(self, line: str) -> Optional[str]:
        stripped = line.strip()
        for sep in self.config.kv_separators:
            if sep in stripped:
                parts = stripped.split(sep, 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""
                if 1 <= len(key) <= 60 and len(value) > 0:
                    return key
        return None

    def _split_by_paragraphs(self, text: str) -> list[str]:
        parts = re.split(r"\n\n+", text)
        return [p.strip() for p in parts if p.strip()]

    def _split_by_sentences(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_from_object(self, document: object) -> Optional[dict]:
        if isinstance(document, dict):
            return document
        for attr in ("extraction", "data", "content"):
            val = getattr(document, attr, None)
            if isinstance(val, dict):
                return val
        raw = getattr(document, "raw_text", None) or getattr(document, "text", None)
        if isinstance(raw, str):
            return {"pages": [{"raw_text": raw, "page_number": 1}]}
        return None

    def _extract_source_from_dict(self, document: dict) -> SourceInfo:
        return SourceInfo(
            source_path=document.get("source_path"),
            document_id=document.get("document_id"),
            file_name=document.get("file_name"),
            file_hash=document.get("file_hash"),
        )


def _deterministic_child_id(
    parent_id: str,
    block_type: str,
    text_prefix: str,
    index: int,
) -> str:
    raw = f"{parent_id}:{block_type}:{text_prefix}:{index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def chunk_document(
    document: dict | object,
    config: Optional[ChunkConfig] = None,
) -> ChunkResult:
    chunker = HierarchicalChunker(config=config)
    return chunker.chunk_from_object(document)


def _is_list_line(line: str) -> bool:
    stripped = line.strip()
    if _LIST_BULLET.match(line):
        return True
    if _LIST_NUMBER.match(line):
        return True
    return False


_LIST_BULLET = re.compile(r"^[\s]*[•\-*▪◻◈○]\s+")
_LIST_NUMBER = re.compile(r"^[\s]*(?:\d{1,2}|[ivxlcdm]+|[a-h])\.?\s+")
