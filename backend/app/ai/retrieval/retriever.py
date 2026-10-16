from abc import ABC, abstractmethod
from typing import Any

from app.ai.schemas.chunk import ChunkResponse


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[ChunkResponse]:
        ...
