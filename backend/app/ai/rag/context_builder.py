from dataclasses import dataclass, field
from typing import Any

from app.ai.schemas.chunk import ChunkResponse


@dataclass
class BuiltContext:
    context: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    chunk_count: int = 0


class ContextBuilder:
    DEFAULT_MAX_CHARS: int = 8000

    @staticmethod
    def build(
        chunks: list[ChunkResponse],
        max_chars: int | None = None,
    ) -> BuiltContext:
        if max_chars is None:
            max_chars = ContextBuilder.DEFAULT_MAX_CHARS

        if not chunks:
            return BuiltContext(context="", sources=[], chunk_count=0)

        unique_chunks: list[ChunkResponse] = ContextBuilder._deduplicate(chunks)

        parts: list[str] = []
        sources: list[dict[str, Any]] = []
        total = 0

        for i, chunk in enumerate(unique_chunks, start=1):
            sources.append(ContextBuilder._chunk_to_source(chunk))

            text = chunk.text or ""
            header = ContextBuilder._format_header(chunk, i, len(unique_chunks))
            block = f"{header}\n{text}" if text else header

            remaining = max_chars - total
            if remaining <= 0:
                break

            if len(block) <= remaining:
                parts.append(block)
                total += len(block)
            else:
                parts.append(block[:remaining])
                total = max_chars
                break

        context = "\n\n".join(parts) if parts else ""
        return BuiltContext(
            context=context,
            sources=sources,
            chunk_count=len(unique_chunks),
        )

    @staticmethod
    def _deduplicate(chunks: list[ChunkResponse]) -> list[ChunkResponse]:
        seen: set[str] = set()
        unique: list[ChunkResponse] = []
        for chunk in chunks:
            key = chunk.content_hash or chunk.chunk_id or chunk.id
            if key is None:
                unique.append(chunk)
                continue
            if key in seen:
                continue
            seen.add(str(key))
            unique.append(chunk)
        return unique

    @staticmethod
    def _chunk_to_source(chunk: ChunkResponse) -> dict[str, Any]:
        return {
            "product_name": chunk.product_name,
            "supplier": chunk.supplier,
            "document_url": chunk.document_url,
            "source_url": chunk.source_url,
            "domain": chunk.domain,
            "source_type": chunk.source_type,
            "discovery_provider": chunk.discovery_provider,
            "score": chunk.score,
            "confidence": chunk.confidence,
            "evidence": chunk.evidence,
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
        }

    @staticmethod
    def _format_header(chunk: ChunkResponse, index: int, total: int) -> str:
        lines = [f"[DOCUMENT {index}/{total}]"]
        if chunk.product_name:
            lines.append(f"Product: {chunk.product_name}")
        if chunk.supplier:
            lines.append(f"Supplier: {chunk.supplier}")
        if chunk.document_url:
            lines.append(f"Document URL: {chunk.document_url}")
        if chunk.source_type:
            lines.append(f"Source type: {chunk.source_type}")
        if chunk.confidence:
            lines.append(f"Confidence: {chunk.confidence}")
        if chunk.discovery_provider:
            lines.append(f"Discovery provider: {chunk.discovery_provider}")
        if chunk.score is not None:
            lines.append(f"Relevance score: {chunk.score:.4f}")
        return "\n".join(lines)
