from typing import Any

from app.ai.config import ai_settings
from app.ai.embeddings.base import BaseEmbeddingProvider
from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider


class EmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self) -> None:
        provider_name = (ai_settings.embedding_provider or "").lower().strip()
        if provider_name == "ollama":
            self._provider = OllamaEmbeddingProvider(
                base_url=ai_settings.ollama_base_url,
                model=ai_settings.embedding_model or "nomic-embed-text",
                normalize=ai_settings.embedding_normalize,
            )
        elif not provider_name:
            raise RuntimeError("Embedding provider is not configured")
        else:
            raise RuntimeError(f"Unsupported embedding provider: {provider_name}")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._provider.embed(texts)

    @property
    def dimension(self) -> int:
        if not hasattr(self, "_provider"):
            raise RuntimeError("Embedding provider is not configured")
        return self._provider.dimension
