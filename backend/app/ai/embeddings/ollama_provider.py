import logging
from typing import Any

from app.ai.config import ai_settings
from app.ai.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(
        self,
        base_url: str,
        model: str,
        normalize: bool = True,
    ) -> None:
        import ollama

        self._client = ollama.Client(host=base_url)
        self._model = model
        self._normalize = normalize
        self._dimension: int | None = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float]] = []
        for text in texts:
            try:
                response = self._client.embeddings(model=self._model, prompt=text)
            except Exception as exc:
                logger.error("Ollama embedding failed for model %s: %s", self._model, exc)
                raise RuntimeError(
                    f"Failed to generate embedding with Ollama model '{self._model}': {exc}"
                ) from exc
            embedding = response.get("embedding")
            if embedding is None:
                raise RuntimeError(
                    f"Ollama model '{self._model}' returned no embedding"
                )
            vectors.append(embedding)
        if self._normalize:
            vectors = self._normalize_vectors(vectors)
        return vectors

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            try:
                response = self._client.embeddings(model=self._model, prompt=" ")
            except Exception as exc:
                logger.error("Failed to detect dimension for model %s: %s", self._model, exc)
                raise RuntimeError(
                    f"Failed to detect embedding dimension for model '{self._model}': {exc}"
                ) from exc
            embedding = response.get("embedding")
            if embedding is None:
                raise RuntimeError(
                    f"Ollama model '{self._model}' returned no embedding"
                )
            self._dimension = len(embedding)
        return self._dimension

    @staticmethod
    def _normalize_vectors(vectors: list[list[float]]) -> list[list[float]]:
        return BaseEmbeddingProvider._normalize_vectors(vectors)
