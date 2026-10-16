from typing import Any

from app.ai.config import ai_settings
from app.ai.vectorstore.base import BaseVectorStore
from app.ai.vectorstore.qdrant_provider import QdrantVectorStore


class VectorStore(BaseVectorStore):
    def __init__(self) -> None:
        store = (ai_settings.vector_store or "").lower().strip()
        if store == "qdrant":
            self._provider = QdrantVectorStore()
        elif not store:
            raise RuntimeError("Vector store is not configured")
        else:
            raise RuntimeError(f"Unsupported vector store: {store}")

    def add_documents(self, chunks: list[Any]) -> None:
        raise RuntimeError("add_documents requires precomputed embeddings. Use upsert_chunks(chunks, embeddings) instead.")

    def similarity_search(self, query: str, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[Any]:
        raise RuntimeError("similarity_search requires a precomputed query vector. Use search(query_vector, top_k, filters) instead.")

    def delete_documents(self, product_id: str) -> None:
        self._provider.delete_by_product(product_id)

    def health_check(self) -> bool:
        return self._provider.health_check()

    def create_collection(self, dimension: int) -> None:
        self._provider.create_collection(dimension)

    def collection_exists(self) -> bool:
        return self._provider.collection_exists()

    def upsert_chunks(self, chunks: list[Any], embeddings: list[list[float]]) -> None:
        self._provider.upsert_chunks(chunks, embeddings)

    def search(self, query_vector: list[float], top_k: int = 5, filters: dict[str, Any] | None = None) -> list[Any]:
        return self._provider.search(query_vector, top_k, filters)

    def delete_by_document(self, document_id: str) -> None:
        self._provider.delete_by_document(document_id)

    def delete_by_product(self, product_id: str) -> None:
        self._provider.delete_by_product(product_id)

    def collection_info(self) -> dict[str, Any]:
        return self._provider.collection_info()
