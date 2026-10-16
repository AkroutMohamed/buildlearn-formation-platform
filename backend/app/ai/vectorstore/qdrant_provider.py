from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import NAMESPACE_URL, uuid5

from app.ai.chunking.models import ChildChunk
from app.ai.config import ai_settings
from app.ai.vectorstore.base import BaseVectorStore

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qdrant_models
except ImportError as exc:
    raise RuntimeError(
        "qdrant-client is required for QdrantVectorStore. "
        "Install it with: pip install qdrant-client"
    ) from exc


logger = logging.getLogger(__name__)


class QdrantVectorStore(BaseVectorStore):
    def __init__(
        self,
        collection_name: Optional[str] = None,
        *,
        use_hierarchical: bool = False,
    ) -> None:
        url = ai_settings.qdrant_url or "http://localhost:6333"
        self._client = QdrantClient(url=url)

        if collection_name is not None:
            self._collection = collection_name
        elif use_hierarchical:
            self._collection = ai_settings.qdrant_collection_hierarchical
        else:
            self._collection = ai_settings.qdrant_collection or "buildlearn_products"

    def create_collection(self, dimension: int) -> None:
        if self.collection_exists():
            info = self._client.get_collection(self._collection)
            vectors_config = info.config.params.vectors
            existing_size = None
            existing_distance = None
            if isinstance(vectors_config, qdrant_models.VectorParams):
                existing_size = vectors_config.size
                existing_distance = vectors_config.distance
            elif isinstance(vectors_config, dict):
                first_key = next(iter(vectors_config))
                existing_size = vectors_config[first_key].size
                existing_distance = vectors_config[first_key].distance

            if existing_size is not None and existing_size != dimension:
                raise RuntimeError(
                    f"Collection '{self._collection}' already exists with vector size {existing_size}, "
                    f"but the configured embedding model requires dimension {dimension}. "
                    f"Delete the collection or change the embedding model."
                )
            if existing_distance is not None and existing_distance != qdrant_models.Distance.COSINE:
                raise RuntimeError(
                    f"Collection '{self._collection}' uses distance metric {existing_distance}, "
                    f"but COSINE is required. Delete the collection or change the embedding model."
                )
            return

        self._client.create_collection(
            collection_name=self._collection,
            vectors_config=qdrant_models.VectorParams(
                size=dimension,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

    def collection_exists(self) -> bool:
        return self._client.collection_exists(self._collection)

    def upsert_chunks(self, chunks: list[Any], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Number of chunks ({len(chunks)}) must match "
                f"number of embeddings ({len(embeddings)})"
            )

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point_id = self._get_chunk_id(chunk)
            payload = self._build_payload(chunk)
            points.append(
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        self._client.upsert(
            collection_name=self._collection,
            points=points,
        )

    def upsert_child_chunks(self, chunks: list[ChildChunk], embeddings: list[list[float]]) -> None:
        """Upsert ChildChunks with hierarchical payload mapping."""
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Number of chunks ({len(chunks)}) must match "
                f"number of embeddings ({len(embeddings)})"
            )

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point_id = self._get_child_point_id(chunk)
            payload = self._build_child_chunk_payload(chunk)
            points.append(
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        self._client.upsert(
            collection_name=self._collection,
            points=points,
        )

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[Any]:
        query_filter = None
        if filters:
            query_filter = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key=key,
                        match=qdrant_models.MatchValue(value=value),
                    )
                    for key, value in filters.items()
                ]
            )

        response = self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            limit=top_k,
            query_filter=query_filter,
        )

        return [
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload or {},
            }
            for point in response.points
        ]

    def delete_by_document(self, document_id: str) -> None:
        self._client.delete(
            collection_name=self._collection,
            points_selector=qdrant_models.FilterSelector(
                filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="document_id",
                            match=qdrant_models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )

    def delete_by_product(self, product_id: str) -> None:
        self._client.delete(
            collection_name=self._collection,
            points_selector=qdrant_models.FilterSelector(
                filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="product_id",
                            match=qdrant_models.MatchValue(value=product_id),
                        )
                    ]
                )
            ),
        )

    def collection_info(self) -> dict[str, Any]:
        info = self._client.get_collection(self._collection)
        return {
            "name": self._collection,
            "status": str(info.status),
            "points_count": info.points_count,
            "segments_count": info.segments_count,
            "indexed_vectors_count": info.indexed_vectors_count,
        }

    def add_documents(self, chunks: list[Any]) -> None:
        raise RuntimeError(
            "add_documents requires precomputed embeddings. "
            "Use upsert_chunks(chunks, embeddings) instead."
        )

    def similarity_search(self, query: str, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[Any]:
        raise RuntimeError(
            "similarity_search requires a precomputed query vector. "
            "Use search(query_vector, top_k, filters) instead."
        )

    def delete_documents(self, product_id: str) -> None:
        self.delete_by_product(product_id)

    def health_check(self) -> bool:
        try:
            self._client.get_collections()
            return True
        except Exception:
            return False

    @staticmethod
    def _get_chunk_id(chunk: Any) -> int:
        chunk_id = getattr(chunk, "chunk_id", None)
        if chunk_id is None and isinstance(chunk, dict):
            chunk_id = chunk.get("chunk_id")
        if chunk_id is None:
            raise ValueError("Chunk must have a chunk_id")
        return int(chunk_id, 16)

    @staticmethod
    def _build_payload(chunk: Any) -> dict[str, Any]:
        fields = [
            "chunk_id",
            "document_id",
            "product_id",
            "product_name",
            "supplier",
            "source",
            "source_url",
            "document_url",
            "document_type",
            "page_number",
            "section_title",
            "chunk_index",
            "language",
            "content_hash",
            "text",
            "source_type",
            "discovery_provider",
            "domain",
            "confidence",
            "evidence",
        ]
        payload: dict[str, Any] = {}
        for field in fields:
            value = getattr(chunk, field, None)
            if value is None and isinstance(chunk, dict):
                value = chunk.get(field)
            payload[field] = value
        return payload

    @staticmethod
    def _get_child_point_id(chunk: ChildChunk) -> int | str:
        """Keep valid legacy integers; support collision-suffixed hierarchical IDs.

        Python accepts underscores in hex literals, but collision suffixes can
        push the result beyond Qdrant's uint64 range. The original chunk_id
        remains unchanged in the payload. UUID5 uses the entire original ID.
        """
        point_id = QdrantVectorStore._get_chunk_id(chunk)
        if 0 <= point_id <= (1 << 64) - 1:
            return point_id
        return str(uuid5(NAMESPACE_URL, "buildlearn:hierarchical:child:" + chunk.chunk_id))

    @staticmethod
    def _build_child_chunk_payload(chunk: ChildChunk) -> dict[str, Any]:
        """Build payload for ChildChunk with hierarchical schema (10 fields)."""
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.source.document_id,
            "source_path": chunk.source.source_path,
            "file_name": chunk.source.file_name,
            "parent_id": chunk.parent_id,
            "section_path": chunk.section_path,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "block_type": chunk.block_type.value,
            "text": chunk.text,
        }
