import logging
from typing import Any

from app.ai.config import ai_settings
from app.ai.embeddings.provider import EmbeddingProvider
from app.ai.retrieval.retriever import BaseRetriever
from app.ai.schemas.chunk import ChunkResponse
from app.ai.vectorstore.provider import VectorStore

logger = logging.getLogger(__name__)


class Retriever(BaseRetriever):
    def __init__(self) -> None:
        self._embedding_provider = EmbeddingProvider()
        self._vector_store = VectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[ChunkResponse]:
        if not query or not query.strip():
            raise ValueError("Query must not be empty or whitespace")
        if top_k < 1:
            raise ValueError("top_k must be >= 1")

        try:
            query_vector = self._embedding_provider.embed_single(query)
        except Exception as exc:
            logger.error("Failed to embed query: %s", exc)
            raise RuntimeError(f"Embedding failed: {exc}") from exc

        try:
            raw_results = self._vector_store.search(query_vector, top_k=top_k, filters=filters)
        except Exception as exc:
            logger.error("Vector store search failed: %s", exc)
            raise RuntimeError(f"Search failed: {exc}") from exc

        results: list[ChunkResponse] = []
        for item in raw_results:
            payload = item.get("payload") or {}
            score = item.get("score")
            if score is not None and score < ai_settings.retrieval_score_threshold:
                continue
            results.append(
                ChunkResponse(
                    id=str(payload.get("chunk_id", item.get("id", ""))),
                    chunk_id=payload.get("chunk_id"),
                    document_id=payload.get("document_id"),
                    product_id=payload.get("product_id"),
                    product_name=payload.get("product_name"),
                    supplier=payload.get("supplier"),
                    source=payload.get("source"),
                    source_url=payload.get("source_url"),
                    document_url=payload.get("document_url"),
                    document_type=payload.get("document_type"),
                    page_number=payload.get("page_number"),
                    section_title=payload.get("section_title"),
                    chunk_index=payload.get("chunk_index"),
                    text=payload.get("text"),
                    language=payload.get("language"),
                    content_hash=payload.get("content_hash"),
                    metadata=payload.get("metadata"),
                    source_type=payload.get("source_type"),
                    discovery_provider=payload.get("discovery_provider"),
                    domain=payload.get("domain"),
                    confidence=payload.get("confidence"),
                    evidence=payload.get("evidence"),
                    score=score,
                )
            )

        results.sort(key=lambda r: r.score if r.score is not None else float("-inf"), reverse=True)
        return results
