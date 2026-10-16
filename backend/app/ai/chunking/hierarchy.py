from __future__ import annotations

import re
from typing import Optional

from app.ai.chunking.config import ChunkConfig
from app.ai.chunking.models import (
    BlockType,
    ChildChunk,
    ParentChunk,
    SemanticBlock,
    SourceInfo,
)
from app.ai.chunking.parser import parse_text_blocks

_LIST_BULLET_RE = re.compile(r"^[\s]*[•\-*▪◻◈○]\s+")
_LIST_NUMBER_RE = re.compile(r"^[\s]*(?:\d{1,2}|[ivxlcdm]+|[a-h])\.?\s+")


class HierarchyBuilder:
    def __init__(self, config: Optional[ChunkConfig] = None) -> None:
        self.config = config or ChunkConfig()

    def build_hierarchy(
        self,
        raw_text: str,
        source: SourceInfo,
        page_number: int = 1,
    ) -> list[SemanticBlock]:
        blocks = parse_text_blocks(raw_text, source, page_number, self.config)
        return self._assign_hierarchy(blocks)

    def _assign_hierarchy(
        self,
        blocks: list[SemanticBlock],
    ) -> list[SemanticBlock]:
        if not blocks:
            return []

        sections: list[SemanticBlock] = []
        subsections: list[SemanticBlock] = []
        body_blocks: list[SemanticBlock] = []

        current_section: Optional[SemanticBlock] = None
        current_subsection: Optional[SemanticBlock] = None

        for block in blocks:
            if block.block_type == BlockType.PAGE_BREAK:
                body_blocks.append(block)
                continue

            if block.block_type == BlockType.HEADING:
                if current_subsection is not None and current_subsection.text != block.text:
                    subsections.append(current_subsection)
                    current_subsection = None

                if current_section is not None and self._is_higher_level(block, current_section):
                    sections.append(current_section)
                    current_section = block
                    current_subsection = None
                elif current_section is not None and block.text != current_section.text:
                    sections.append(current_section)
                    current_section = block
                    current_subsection = None
                else:
                    current_section = block
                continue

            if current_section is None:
                body_blocks.append(block)
                continue

            block.section_path = (current_section.section_path or []) + [current_section.text]
            block.parent_id = current_section.block_id

            if current_subsection is not None and self._is_higher_level(block, current_subsection):
                subsections.append(current_subsection)
                current_subsection = None
                block.section_path = (current_section.section_path or []) + [current_section.text]
                block.parent_id = current_section.block_id

            if block.block_type in (BlockType.LIST, BlockType.TABLE, BlockType.KEY_VALUE):
                if current_subsection is not None and self._is_same_context(block, current_subsection):
                    current_subsection.text += self.config.separator + block.text
                    continue
                current_subsection = block
            else:
                if current_subsection is not None:
                    subsections.append(current_subsection)
                    current_subsection = None
                block.section_path = (current_section.section_path or []) + [current_section.text]
                block.parent_id = current_section.block_id
                body_blocks.append(block)

        if current_subsection is not None:
            subsections.append(current_subsection)
        if current_section is not None:
            sections.append(current_section)

        result: list[SemanticBlock] = []
        result.extend(sections)
        result.extend(subsections)
        result.extend(body_blocks)
        return result

    @staticmethod
    def _is_higher_level(block: SemanticBlock, candidate: SemanticBlock) -> bool:
        block_words = len(block.text.split())
        cand_words = len(candidate.text.split())
        if cand_words > 5 and block_words < 5:
            return True
        if block.text.isupper() and not candidate.text.isupper():
            return True
        if len(block.text) < len(candidate.text) * 0.5 and block_words <= 3:
            return True
        return False

    @staticmethod
    def _is_same_context(block: SemanticBlock, candidate: SemanticBlock) -> bool:
        return block.block_type in (
            BlockType.LIST, BlockType.TABLE, BlockType.KEY_VALUE, BlockType.LIST_ITEM,
        ) and candidate.block_type in (
            BlockType.LIST, BlockType.TABLE, BlockType.KEY_VALUE, BlockType.LIST_ITEM,
        )


def build_hierarchy(
    raw_text: str,
    source: SourceInfo,
    page_number: int = 1,
    config: Optional[ChunkConfig] = None,
) -> list[SemanticBlock]:
    builder = HierarchyBuilder(config=config)
    return builder.build_hierarchy(raw_text, source, page_number)
