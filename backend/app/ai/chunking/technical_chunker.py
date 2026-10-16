from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

from app.ai.schemas.chunk import ChunkCreate

logger = logging.getLogger(__name__)

_HEADING_PATTERN = re.compile(r"^(?P<heading>[A-Z][A-Z\s\-\(\)\/']+(?:\s+[A-Z][A-Z\s\-\(\)\/']*)*)$", re.MULTILINE)
_MAX_CHUNK_SIZE = 1500
_MIN_CHUNK_SIZE = 200


class TechnicalDocumentChunker:
    def __init__(self, max_chunk_size: int = _MAX_CHUNK_SIZE, min_chunk_size: int = _MIN_CHUNK_SIZE) -> None:
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk(self, document: Any, product: Any = None) -> list[ChunkCreate]:
        content = getattr(document, "content", None) or document.get("content") if isinstance(document, dict) else None
        if not content:
            return []

        document_id = getattr(document, "document_id", None) or document.get("document_id")
        product_id = getattr(document, "product_id", None) or document.get("product_id")
        product_name = getattr(document, "product_name", None) or document.get("product_name")
        supplier = getattr(document, "metadata", {}).get("supplier") if hasattr(document, "metadata") else (document.get("metadata", {}).get("supplier") if isinstance(document, dict) else None)
        source = getattr(document, "source", None) or document.get("source")
        source_url = getattr(document, "source_url", None) or document.get("source_url")
        document_url = getattr(document, "document_url", None) or document.get("document_url")
        document_type = getattr(document, "document_type", None) or document.get("document_type")
        language = getattr(document, "language", None) or document.get("language")
        content_hash = getattr(document, "content_hash", None) or document.get("content_hash")
        metadata = getattr(document, "metadata", {}) if hasattr(document, "metadata") else (document.get("metadata", {}) if isinstance(document, dict) else {})
        source_type = metadata.get("source_type")
        discovery_provider = metadata.get("discovery_provider")
        domain = metadata.get("domain")
        confidence = metadata.get("confidence")
        evidence = metadata.get("association_evidence")

        page_count = getattr(document, "metadata", {}).get("page_count") if hasattr(document, "metadata") else (document.get("metadata", {}).get("page_count") if isinstance(document, dict) else None)
        if page_count is None:
            page_count = 1

        pages_text = content.split("\n\n")

        chunks: list[ChunkCreate] = []
        chunk_index = 0

        for page_number, page_text in enumerate(pages_text, start=1):
            sections = self._split_into_sections(page_text)
            current_section_title = None
            current_section_parts: list[str] = []

            for section in sections:
                section_title, section_body = self._extract_section_title(section)
                if section_title:
                    if current_section_parts:
                        chunk_text = "\n\n".join(current_section_parts)
                        if chunk_text.strip():
                            chunks.append(self._create_chunk(
                                document_id=document_id,
                                product_id=product_id,
                                product_name=product_name,
                                supplier=supplier,
                                source=source,
                                source_url=source_url,
                                document_url=document_url,
                                document_type=document_type,
                                page_number=page_number,
                                section_title=current_section_title,
                                chunk_index=chunk_index,
                                text=chunk_text,
                                language=language,
                                content_hash=content_hash,
                                source_type=source_type,
                                discovery_provider=discovery_provider,
                                domain=domain,
                                confidence=confidence,
                                evidence=evidence,
                            ))
                            chunk_index += 1
                            current_section_parts = []
                    current_section_title = section_title

                current_section_parts.append(section_body)
                combined = "\n\n".join(current_section_parts)
                if len(combined) >= self.max_chunk_size:
                    split_parts = self._split_oversized_text(combined, self.max_chunk_size)
                    for part in split_parts[:-1]:
                        chunks.append(self._create_chunk(
                            document_id=document_id,
                            product_id=product_id,
                            product_name=product_name,
                            supplier=supplier,
                            source=source,
                            source_url=source_url,
                            document_url=document_url,
                            document_type=document_type,
                            page_number=page_number,
                            section_title=current_section_title,
                            chunk_index=chunk_index,
                            text=part,
                            language=language,
                            content_hash=content_hash,
                            source_type=source_type,
                            discovery_provider=discovery_provider,
                            domain=domain,
                            confidence=confidence,
                            evidence=evidence,
                        ))
                        chunk_index += 1
                    current_section_parts = [split_parts[-1]] if split_parts else []

            if current_section_parts:
                chunk_text = "\n\n".join(current_section_parts)
                if chunk_text.strip():
                    chunks.append(self._create_chunk(
                        document_id=document_id,
                        product_id=product_id,
                        product_name=product_name,
                        supplier=supplier,
                        source=source,
                        source_url=source_url,
                        document_url=document_url,
                        document_type=document_type,
                        page_number=page_number,
                        section_title=current_section_title,
                        chunk_index=chunk_index,
                        text=chunk_text,
                        language=language,
                        content_hash=content_hash,
                        source_type=source_type,
                        discovery_provider=discovery_provider,
                        domain=domain,
                        confidence=confidence,
                        evidence=evidence,
                    ))
                    chunk_index += 1

        return chunks

    def _split_into_sections(self, text: str) -> list[str]:
        lines = text.splitlines()
        sections: list[str] = []
        current_section: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped and self._is_heading(stripped):
                if current_section:
                    sections.append("\n".join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        if current_section:
            sections.append("\n".join(current_section))
        return sections

    def _is_heading(self, text: str) -> bool:
        if len(text) > 80:
            return False
        if not _HEADING_PATTERN.match(text):
            return False
        words = text.split()
        if len(words) == 1 and len(text) > 10:
            return False
        return True

    def _extract_section_title(self, section: str) -> tuple[str | None, str]:
        lines = section.splitlines()
        if not lines:
            return None, section
        first_line = lines[0].strip()
        if self._is_heading(first_line):
            return first_line, "\n".join(lines[1:]).strip()
        return None, section

    def _create_chunk(
        self,
        document_id: str | None,
        product_id: str | None,
        product_name: str | None,
        supplier: str | None,
        source: str | None,
        source_url: str | None,
        document_url: str | None,
        document_type: str | None,
        page_number: int | None,
        section_title: str | None,
        chunk_index: int | None,
        text: str,
        language: str | None,
        content_hash: str | None,
        source_type: str | None,
        discovery_provider: str | None,
        domain: str | None,
        confidence: str | None,
        evidence: str | None,
    ) -> ChunkCreate:
        chunk_text = text.strip()
        chunk_id_source = f"{document_id}:{page_number}:{section_title}:{chunk_index}:{chunk_text[:100]}"
        chunk_id = hashlib.sha256(chunk_id_source.encode("utf-8")).hexdigest()[:16]

        return ChunkCreate(
            chunk_id=chunk_id,
            document_id=document_id,
            product_id=product_id,
            product_name=product_name,
            supplier=supplier,
            source=source,
            source_url=source_url,
            document_url=document_url,
            document_type=document_type,
            page_number=page_number,
            section_title=section_title,
            chunk_index=chunk_index,
            text=chunk_text,
            language=language,
            content_hash=content_hash,
            metadata={
                "char_count": len(chunk_text),
                "word_count": len(chunk_text.split()),
            },
            source_type=source_type,
            discovery_provider=discovery_provider,
            domain=domain,
            confidence=confidence,
            evidence=evidence,
        )

    def _split_oversized_text(self, text: str, max_size: int) -> list[str]:
        return [text[i:i + max_size] for i in range(0, len(text), max_size)]
