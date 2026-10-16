from abc import ABC, abstractmethod
from typing import Any


class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, chunks: list[Any]) -> None:
        ...

    @abstractmethod
    def similarity_search(self, query: str, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[Any]:
        ...

    @abstractmethod
    def delete_documents(self, product_id: str) -> None:
        ...

    @abstractmethod
    def health_check(self) -> bool:
        ...

    @abstractmethod
    def create_collection(self, dimension: int) -> None:
        ...

    @abstractmethod
    def collection_exists(self) -> bool:
        ...

    @abstractmethod
    def upsert_chunks(self, chunks: list[Any], embeddings: list[list[float]]) -> None:
        ...

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int = 5, filters: dict[str, Any] | None = None) -> list[Any]:
        ...

    @abstractmethod
    def delete_by_document(self, document_id: str) -> None:
        ...

    @abstractmethod
    def delete_by_product(self, product_id: str) -> None:
        ...

    @abstractmethod
    def collection_info(self) -> dict[str, Any]:
        ...
