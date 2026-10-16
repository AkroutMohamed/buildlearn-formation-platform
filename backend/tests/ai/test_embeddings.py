import math
import os
import time
from unittest.mock import MagicMock, patch

import pytest

from app.ai.chunking.models import ChildChunk, SourceInfo, BlockType
from app.ai.config import ai_settings
from app.ai.embeddings.base import BaseEmbeddingProvider
from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.ai.embeddings.provider import EmbeddingProvider
from app.ai.embeddings.service import EmbeddingService, EmbeddingResult, EmbeddingServiceConfig


class ConcreteProvider(BaseEmbeddingProvider):
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 2.0], [3.0, 4.0]]

    @property
    def dimension(self) -> int:
        return 2


def test_base_embedding_provider_is_abstract():
    with pytest.raises(TypeError):
        BaseEmbeddingProvider()


def test_embed_single_uses_embed():
    provider = ConcreteProvider()
    assert provider.embed_single("hello") == [1.0, 2.0]


def test_normalize_vectors_unit_magnitude():
    vectors = [[3.0, 4.0]]
    normalized = BaseEmbeddingProvider._normalize_vectors(vectors)
    magnitude = math.sqrt(sum(x * x for x in normalized[0]))
    assert abs(magnitude - 1.0) < 1e-6
    assert normalized[0] == [0.6, 0.8]


def test_normalize_vectors_zero_vector():
    vectors = [[0.0, 0.0]]
    normalized = BaseEmbeddingProvider._normalize_vectors(vectors)
    assert normalized[0] == [0.0, 0.0]


def test_ollama_embedding_provider_embed():
    mock_client = MagicMock()
    mock_client.embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

    with patch("ollama.Client", return_value=mock_client):
        provider = OllamaEmbeddingProvider(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
            normalize=False,
        )
        vectors = provider.embed(["hello world"])
        assert vectors == [[0.1, 0.2, 0.3]]
        mock_client.embeddings.assert_called_with(
            model="nomic-embed-text", prompt="hello world"
        )


def test_ollama_embedding_provider_normalize():
    mock_client = MagicMock()
    mock_client.embeddings.return_value = {"embedding": [3.0, 4.0]}

    with patch("ollama.Client", return_value=mock_client):
        provider = OllamaEmbeddingProvider(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
            normalize=True,
        )
        vectors = provider.embed(["hello"])
        assert len(vectors[0]) == 2
        magnitude = math.sqrt(sum(x * x for x in vectors[0]))
        assert abs(magnitude - 1.0) < 1e-6


def test_ollama_embedding_provider_dimension():
    mock_client = MagicMock()
    mock_client.embeddings.return_value = {"embedding": [0.1] * 768}

    with patch("ollama.Client", return_value=mock_client):
        provider = OllamaEmbeddingProvider(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
        )
        assert provider.dimension == 768
        mock_client.embeddings.assert_called_with(model="nomic-embed-text", prompt=" ")


def test_ollama_embedding_provider_empty_input():
    mock_client = MagicMock()

    with patch("ollama.Client", return_value=mock_client):
        provider = OllamaEmbeddingProvider(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
        )
        assert provider.embed([]) == []
        mock_client.embeddings.assert_not_called()


def test_ollama_embedding_provider_unavailable_model():
    mock_client = MagicMock()
    mock_client.embeddings.side_effect = Exception("model not found")

    with patch("ollama.Client", return_value=mock_client):
        provider = OllamaEmbeddingProvider(
            base_url="http://localhost:11434",
            model="missing-model",
        )
        with pytest.raises(RuntimeError, match="Failed to generate embedding"):
            provider.embed(["hello"])


def test_embedding_provider_requires_config(monkeypatch):
    monkeypatch.setattr(ai_settings, "embedding_provider", "")
    with pytest.raises(RuntimeError, match="Embedding provider is not configured"):
        EmbeddingProvider()


def test_embedding_provider_unsupported_provider(monkeypatch):
    monkeypatch.setattr(ai_settings, "embedding_provider", "unknown")
    with pytest.raises(RuntimeError, match="Unsupported embedding provider"):
        EmbeddingProvider()


def test_embedding_provider_ollama_dispatch(monkeypatch):
    monkeypatch.setattr(ai_settings, "embedding_provider", "ollama")
    monkeypatch.setattr(ai_settings, "embedding_model", "test-model")
    monkeypatch.setattr(ai_settings, "embedding_normalize", False)
    monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")

    with patch("app.ai.embeddings.provider.OllamaEmbeddingProvider") as MockOllama:
        instance = MockOllama.return_value
        instance.embed.return_value = [[0.1, 0.2]]
        provider = EmbeddingProvider()
        assert provider.embed(["test"]) == [[0.1, 0.2]]
        MockOllama.assert_called_once_with(
            base_url="http://localhost:11434",
            model="test-model",
            normalize=False,
        )


def test_embedding_provider_output_type():
    mock_client = MagicMock()
    mock_client.embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

    with patch("ollama.Client", return_value=mock_client):
        provider = OllamaEmbeddingProvider(
            base_url="http://localhost:11434",
            model="test-model",
            normalize=False,
        )
        result = provider.embed(["text"])
        assert isinstance(result, list)
        assert all(isinstance(v, list) for v in result)
        assert all(isinstance(x, float) for v in result for x in v)


class MockProvider(BaseEmbeddingProvider):
    def __init__(self, vectors: list[list[float]], fail_count: int = 0, dimension: int | None = None):
        self._all_vectors = vectors
        self._fail_count = fail_count
        self._call_count = 0
        self._dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._call_count += 1
        if self._fail_count > 0 and self._call_count <= self._fail_count:
            raise RuntimeError("Simulated failure")
        n = len(texts)
        return self._all_vectors[:n]

    @property
    def dimension(self) -> int:
        if self._dimension is not None:
            return self._dimension
        return len(self._all_vectors[0]) if self._all_vectors else 2


def _make_chunk(text: str, chunk_id: str = "test") -> ChildChunk:
    return ChildChunk(
        chunk_id=chunk_id,
        chunk_type=BlockType.RAW_TEXT,
        text=text,
        source=SourceInfo(document_id="doc-1"),
        block_type=BlockType.RAW_TEXT,
    )


def test_embedding_service_basic():
    provider = MockProvider(vectors=[[0.1, 0.2], [0.3, 0.4]])
    service = EmbeddingService(provider=provider, config=EmbeddingServiceConfig(batch_size=10))
    chunks = [_make_chunk("hello", "c1"), _make_chunk("world", "c2")]

    results = service.embed_chunks(chunks)

    assert len(results) == 2
    assert results[0].chunk_id == "c1"
    assert results[0].vector == [0.1, 0.2]
    assert results[1].chunk_id == "c2"
    assert results[1].vector == [0.3, 0.4]


def test_embedding_service_batching():
    provider = MockProvider(
        vectors=[[float(i), float(i+1)] for i in range(10)],
        dimension=2,
    )
    # Use batch_size >= total chunks so embed is called once
    service = EmbeddingService(provider=provider, config=EmbeddingServiceConfig(batch_size=100))
    chunks = [_make_chunk(f"text {i}", f"c{i}") for i in range(10)]

    results = service.embed_chunks(chunks)

    assert len(results) == 10
    for i, r in enumerate(results):
        assert r.chunk_id == f"c{i}"
        assert r.vector == [float(i), float(i+1)]


def test_embedding_service_retry_on_failure():
    provider = MockProvider(vectors=[[0.1, 0.2]], fail_count=2)
    service = EmbeddingService(provider=provider, config=EmbeddingServiceConfig(max_retries=3, retry_delay=0.01))
    chunks = [_make_chunk("hello", "c1")]

    results = service.embed_chunks(chunks)

    assert len(results) == 1
    assert results[0].vector == [0.1, 0.2]
    assert provider._call_count == 3


def test_embedding_service_fails_after_max_retries():
    provider = MockProvider(vectors=[[0.1, 0.2]], fail_count=5)
    service = EmbeddingService(provider=provider, config=EmbeddingServiceConfig(max_retries=3, retry_delay=0.01))
    chunks = [_make_chunk("hello", "c1")]

    with pytest.raises(RuntimeError, match="Embedding failed after 3 attempts"):
        service.embed_chunks(chunks)
    assert provider._call_count == 3


def test_embedding_service_validates_dimension():
    provider = MockProvider(vectors=[[0.1, 0.2, 0.3]], dimension=2)
    service = EmbeddingService(provider=provider)
    chunks = [_make_chunk("hello", "c1")]

    with pytest.raises(RuntimeError, match="dimension 3, expected 2"):
        service.embed_chunks(chunks)


def test_embedding_service_validates_finite_values():
    provider = MockProvider(vectors=[[0.1, float("inf")]])
    service = EmbeddingService(provider=provider, config=EmbeddingServiceConfig(max_retries=1, retry_delay=0.01))
    chunks = [_make_chunk("hello", "c1")]

    with pytest.raises(RuntimeError, match="non-finite value"):
        service.embed_chunks(chunks)


def test_embedding_service_validates_nan():
    provider = MockProvider(vectors=[[0.1, float("nan")]])
    service = EmbeddingService(provider=provider, config=EmbeddingServiceConfig(max_retries=1, retry_delay=0.01))
    chunks = [_make_chunk("hello", "c1")]

    with pytest.raises(RuntimeError, match="non-finite value"):
        service.embed_chunks(chunks)


def test_embedding_service_empty_input():
    provider = MockProvider(vectors=[])
    service = EmbeddingService(provider=provider)
    assert service.embed_chunks([]) == []


def test_embedding_service_metadata_extraction():
    provider = MockProvider(vectors=[[0.1, 0.2]])
    service = EmbeddingService(provider=provider)
    chunk = ChildChunk(
        chunk_id="test-chunk",
        chunk_type=BlockType.RAW_TEXT,
        text="test text",
        source=SourceInfo(document_id="doc-1", source_path="/path", file_name="test.pdf"),
        section_path=["section1", "subsection2"],
        page_start=1,
        page_end=2,
        parent_id="parent-1",
        block_type=BlockType.RAW_TEXT,
    )

    results = service.embed_chunks([chunk])

    assert results[0].metadata["chunk_id"] == "test-chunk"
    assert results[0].metadata["document_id"] == "doc-1"
    assert results[0].metadata["section_path"] == ["section1", "subsection2"]
    assert results[0].metadata["page_start"] == 1
    assert results[0].metadata["page_end"] == 2
    assert results[0].metadata["parent_id"] == "parent-1"


def test_embedding_service_deterministic_ids():
    provider = MockProvider(vectors=[[0.1, 0.2]])
    service = EmbeddingService(provider=provider)
    chunk = _make_chunk("hello", "fixed-id")

    r1 = service.embed_chunks([chunk])
    r2 = service.embed_chunks([chunk])

    assert r1[0].chunk_id == r2[0].chunk_id == "fixed-id"


def test_embedding_service_single():
    provider = MockProvider(vectors=[[0.5, 0.5]])
    service = EmbeddingService(provider=provider)
    vec = service.embed_single("single text")
    assert vec == [0.5, 0.5]
