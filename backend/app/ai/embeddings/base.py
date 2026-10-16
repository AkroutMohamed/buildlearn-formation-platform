import math
from abc import ABC, abstractmethod
from typing import Any


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_single(self, text: str) -> list[float]:
        return self.embed([text])[0]

    @property
    @abstractmethod
    def dimension(self) -> int:
        ...

    @staticmethod
    def _normalize_vectors(vectors: list[list[float]]) -> list[list[float]]:
        normalized: list[list[float]] = []
        for vector in vectors:
            magnitude = math.sqrt(sum(x * x for x in vector))
            if magnitude == 0:
                normalized.append(vector)
            else:
                normalized.append([x / magnitude for x in vector])
        return normalized
