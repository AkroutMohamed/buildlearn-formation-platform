from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from app.ai.chunking.models import ChildChunk
from app.ai.config import ai_settings
from app.ai.embeddings.base import BaseEmbeddingProvider
from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.ai.embeddings.provider import EmbeddingProvider

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    chunk_id: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingServiceConfig:
    batch_size: int = 32
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: float = 30.0


class EmbeddingService:
    def __init__(
        self,
        provider: Optional[BaseEmbeddingProvider] = None,
        config: Optional[EmbeddingServiceConfig] = None,
    ) -> None:
        self._provider = provider or self._create_default_provider()
        self._config = config or EmbeddingServiceConfig()
        self._dimension = self._provider.dimension
        logger.info(
            "EmbeddingService initialized: provider=%s, dimension=%d, batch_size=%d",
            self._provider.__class__.__name__,
            self._dimension,
            self._config.batch_size,
        )

    def _create_default_provider(self) -> BaseEmbeddingProvider:
        if ai_settings.embedding_provider == "ollama":
            return OllamaEmbeddingProvider(
                base_url=ai_settings.ollama_base_url,
                model=ai_settings.embedding_model or "nomic-embed-text",
                normalize=ai_settings.embedding_normalize,
            )
        raise RuntimeError(
            f"Unsupported embedding provider: {ai_settings.embedding_provider}. "
            "Only 'ollama' is supported."
        )

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_chunks(self, chunks: list[ChildChunk]) -> list[EmbeddingResult]:
        if not chunks:
            return []

        texts = [chunk.text for chunk in chunks]
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [self._extract_metadata(chunk) for chunk in chunks]

        vectors = self._embed_with_retry(texts)

        return [
            EmbeddingResult(chunk_id=cid, vector=vec, metadata=meta)
            for cid, vec, meta in zip(chunk_ids, vectors, metadatas)
        ]

    def _embed_with_retry(self, texts: list[str]) -> list[list[float]]:
        for attempt in range(1, self._config.max_retries + 1):
            try:
                return self._embed_batched(texts)
            except Exception as exc:
                logger.warning(
                    "Embedding attempt %d/%d failed for %d texts: %s",
                    attempt,
                    self._config.max_retries,
                    len(texts),
                    exc,
                )
                if attempt == self._config.max_retries:
                    raise RuntimeError(
                        f"Embedding failed after {self._config.max_retries} attempts: {exc}"
                    ) from exc
                time.sleep(self._config.retry_delay * attempt)

        return []

    def _embed_batched(self, texts: list[str]) -> list[list[float]]:
        all_vectors: list[list[float]] = []

        for i in range(0, len(texts), self._config.batch_size):
            batch = texts[i : i + self._config.batch_size]
            logger.debug("Embedding batch %d-%d (%d texts)", i, i + len(batch), len(batch))
            start = time.time()
            vectors = self._provider.embed(batch)
            elapsed = time.time() - start
            logger.debug("Batch embedded in %.3fs", elapsed)
            all_vectors.extend(vectors)

        self._validate_vectors(all_vectors)
        return all_vectors

    def _validate_vectors(self, vectors: list[list[float]]) -> None:
        for idx, vec in enumerate(vectors):
            if len(vec) != self._dimension:
                raise ValueError(
                    f"Vector at index {idx} has dimension {len(vec)}, expected {self._dimension}"
                )
            for val in vec:
                if not isinstance(val, (int, float)) or val != val or val == float("inf") or val == float("-inf"):
                    raise ValueError(
                        f"Vector at index {idx} contains non-finite value: {val}"
                    )

    def _extract_metadata(self, chunk: ChildChunk) -> dict[str, Any]:
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.source.document_id,
            "source_path": chunk.source.source_path,
            "file_name": chunk.source.file_name,
            "section_path": chunk.section_path,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "parent_id": chunk.parent_id,
            "block_type": chunk.block_type.value,
            "char_count": chunk.char_count,
            "word_count": chunk.word_count,
        }

    def embed_single(self, text: str) -> list[float]:
        vectors = self._embed_with_retry([text])
        return vectors[0] if vectors else []