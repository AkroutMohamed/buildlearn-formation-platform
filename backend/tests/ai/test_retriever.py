from unittest.mock import MagicMock, patch

import pytest

from app.ai.config import ai_settings
from app.ai.rag.retriever import Retriever
from app.ai.schemas.chunk import ChunkResponse


def _make_qdrant_result(payload: dict[str, object], score: float = 0.9, point_id: int = 12345):
    return {
        "id": point_id,
        "score": score,
        "payload": payload,
    }


def test_empty_query_raises():
    with patch("app.ai.rag.retriever.EmbeddingProvider") as mock_embedding_cls, \
         patch("app.ai.rag.retriever.VectorStore") as mock_vector_store_cls:
            mock_embedding_cls.return_value = MagicMock()
            mock_vector_store_cls.return_value = MagicMock()
            retriever = Retriever()
            with pytest.raises(ValueError, match="Query must not be empty"):
                retriever.retrieve("")


def test_whitespace_query_raises():
    with patch("app.ai.rag.retriever.EmbeddingProvider") as mock_embedding_cls, \
         patch("app.ai.rag.retriever.VectorStore") as mock_vector_store_cls:
            mock_embedding_cls.return_value = MagicMock()
            mock_vector_store_cls.return_value = MagicMock()
            retriever = Retriever()
            with pytest.raises(ValueError, match="Query must not be empty"):
                retriever.retrieve("   ")


def test_invalid_top_k_raises():
    with patch("app.ai.rag.retriever.EmbeddingProvider") as mock_embedding_cls, \
         patch("app.ai.rag.retriever.VectorStore") as mock_vector_store_cls:
            mock_embedding_cls.return_value = MagicMock()
            mock_vector_store_cls.return_value = MagicMock()
            retriever = Retriever()
            with pytest.raises(ValueError, match="top_k must be >= 1"):
                retriever.retrieve("test", top_k=0)
            with pytest.raises(ValueError, match="top_k must be >= 1"):
                retriever.retrieve("test", top_k=-1)


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_embeds_query(mock_vector_store_cls, mock_embedding_cls):
    mock_embedding = MagicMock()
    mock_embedding.embed_single.return_value = [0.1] * 768
    mock_embedding_cls.return_value = mock_embedding

    mock_store = MagicMock()
    mock_store.search.return_value = []
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    retriever.retrieve("What is the Gyproc Moisture Resistant Board?", top_k=5)

    mock_embedding.embed_single.assert_called_once_with("What is the Gyproc Moisture Resistant Board?")
    mock_store.search.assert_called_once()
    args, kwargs = mock_store.search.call_args
    assert kwargs["top_k"] == 5
    assert len(args) == 1
    assert len(args[0]) == 768


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_handles_embedding_failure(mock_vector_store_cls, mock_embedding_cls):
    mock_embedding = MagicMock()
    mock_embedding.embed_single.side_effect = RuntimeError("Ollama down")
    mock_embedding_cls.return_value = mock_embedding

    mock_store = MagicMock()
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    with pytest.raises(RuntimeError, match="Embedding failed"):
        retriever.retrieve("test query")


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_handles_qdrant_failure(mock_vector_store_cls, mock_embedding_cls):
    mock_embedding = MagicMock()
    mock_embedding.embed_single.return_value = [0.1] * 768
    mock_embedding_cls.return_value = mock_embedding

    mock_store = MagicMock()
    mock_store.search.side_effect = RuntimeError("Qdrant connection refused")
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    with pytest.raises(RuntimeError, match="Search failed"):
        retriever.retrieve("test query")


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_maps_payload_to_chunk_response(mock_vector_store_cls, mock_embedding_cls):
    mock_embedding = MagicMock()
    mock_embedding.embed_single.return_value = [0.1] * 768
    mock_embedding_cls.return_value = mock_embedding

    payload = {
        "chunk_id": "chunk001",
        "document_id": "doc-1",
        "product_id": "prod-1",
        "product_name": "BA13 Hydro",
        "supplier": "GYPROC",
        "source": "gypsobat",
        "source_url": "https://x.com/p1/",
        "document_url": "https://www.gyproc.in/pdf/Gyproc_BA13_Hydro.pdf",
        "document_type": "technical_sheet",
        "page_number": 1,
        "section_title": "SECTION A",
        "chunk_index": 0,
        "text": "Moisture Resistance high moisture resistance board.",
        "language": "fr",
        "content_hash": "hash123",
        "metadata": {"char_count": 50, "word_count": 10},
        "source_type": "external_official",
        "discovery_provider": "manufacturer_targeted",
        "domain": "www.gyproc.in",
        "confidence": "high",
        "evidence": "Found via manufacturer_targeted",
    }
    mock_store = MagicMock()
    mock_store.search.return_value = [_make_qdrant_result(payload, score=0.95, point_id=999)]
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    results = retriever.retrieve("test query", top_k=5)

    assert len(results) == 1
    result = results[0]
    assert isinstance(result, ChunkResponse)
    assert result.chunk_id == "chunk001"
    assert result.score == 0.95
    assert result.text == "Moisture Resistance high moisture resistance board."
    assert result.product_name == "BA13 Hydro"
    assert result.supplier == "GYPROC"
    assert result.source_type == "external_official"
    assert result.discovery_provider == "manufacturer_targeted"
    assert result.domain == "www.gyproc.in"
    assert result.confidence == "high"
    assert result.evidence == "Found via manufacturer_targeted"
    assert result.source_url == "https://x.com/p1/"
    assert result.document_url == "https://www.gyproc.in/pdf/Gyproc_BA13_Hydro.pdf"


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_preserves_gyproc_provenance(mock_vector_store_cls, mock_embedding_cls):
    mock_embedding = MagicMock()
    mock_embedding.embed_single.return_value = [0.1] * 768
    mock_embedding_cls.return_value = mock_embedding

    payload = {
        "chunk_id": "gyproc-chunk-1",
        "document_id": "doc-gyproc",
        "product_id": "prod-gyproc",
        "product_name": "BA13 Hydro",
        "supplier": "GYPROC",
        "source": "gypsobat",
        "source_url": "https://x.com/p1/",
        "document_url": "https://www.gyproc.in/pdf/Gyproc_BA13_Hydro.pdf",
        "document_type": "technical_sheet",
        "page_number": 1,
        "section_title": "MOISTURE RESISTANCE",
        "chunk_index": 0,
        "text": "BA13 Hydro is a moisture resistant board.",
        "language": "en",
        "content_hash": "abc123",
        "metadata": {"char_count": 40},
        "source_type": "external_official",
        "discovery_provider": "manufacturer_targeted",
        "domain": "www.gyproc.in",
        "confidence": "high",
        "evidence": "Found via manufacturer_targeted",
    }
    mock_store = MagicMock()
    mock_store.search.return_value = [_make_qdrant_result(payload, score=0.98, point_id=111)]
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    results = retriever.retrieve("What is the Gyproc Moisture Resistant Board?", top_k=5)

    assert len(results) == 1
    result = results[0]
    assert result.product_name == "BA13 Hydro"
    assert result.supplier == "GYPROC"
    assert result.source_type == "external_official"
    assert result.discovery_provider == "manufacturer_targeted"
    assert result.domain == "www.gyproc.in"
    assert result.confidence == "high"
    assert result.evidence == "Found via manufacturer_targeted"
    assert result.source_url == "https://x.com/p1/"
    assert result.document_url == "https://www.gyproc.in/pdf/Gyproc_BA13_Hydro.pdf"


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_returns_results_in_score_order(mock_vector_store_cls, mock_embedding_cls):
    mock_embedding = MagicMock()
    mock_embedding.embed_single.return_value = [0.1] * 768
    mock_embedding_cls.return_value = mock_embedding

    low_payload = {"chunk_id": "c1", "text": "low score result", "product_name": "A"}
    high_payload = {"chunk_id": "c2", "text": "high score result", "product_name": "B"}
    mid_payload = {"chunk_id": "c3", "text": "mid score result", "product_name": "C"}

    mock_store = MagicMock()
    mock_store.search.return_value = [
        _make_qdrant_result(low_payload, score=0.5, point_id=1),
        _make_qdrant_result(high_payload, score=0.95, point_id=2),
        _make_qdrant_result(mid_payload, score=0.7, point_id=3),
    ]
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    results = retriever.retrieve("test", top_k=3)

    scores = [r.score for r in results]
    assert scores == [0.95, 0.7, 0.5]
    assert results[0].product_name == "B"
    assert results[1].product_name == "C"
    assert results[2].product_name == "A"


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_handles_empty_payload(mock_vector_store_cls, mock_embedding_cls):
    mock_embedding = MagicMock()
    mock_embedding.embed_single.return_value = [0.1] * 768
    mock_embedding_cls.return_value = mock_embedding

    mock_store = MagicMock()
    mock_store.search.return_value = [{"id": 1, "score": 0.8, "payload": {}}]
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    results = retriever.retrieve("test", top_k=5)

    assert len(results) == 1
    assert results[0].score == 0.8
    assert results[0].chunk_id is None
    assert results[0].text is None


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_filters_low_score_results(mock_vector_store_cls, mock_embedding_cls, monkeypatch):
    monkeypatch.setattr(ai_settings, "retrieval_score_threshold", 0.7)

    mock_embedding = MagicMock()
    mock_embedding.embed_single.return_value = [0.1] * 768
    mock_embedding_cls.return_value = mock_embedding

    high_payload = {"chunk_id": "c1", "text": "high score", "product_name": "A"}
    low_payload = {"chunk_id": "c2", "text": "low score", "product_name": "B"}

    mock_store = MagicMock()
    mock_store.search.return_value = [
        _make_qdrant_result(high_payload, score=0.9, point_id=1),
        _make_qdrant_result(low_payload, score=0.2, point_id=2),
    ]
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    results = retriever.retrieve("test", top_k=5)

    assert len(results) == 1
    assert results[0].product_name == "A"


@patch("app.ai.rag.retriever.EmbeddingProvider")
@patch("app.ai.rag.retriever.VectorStore")
def test_retrieve_all_below_threshold_returns_empty(mock_vector_store_cls, mock_embedding_cls, monkeypatch):
    monkeypatch.setattr(ai_settings, "retrieval_score_threshold", 0.99)

    mock_embedding = MagicMock()
    mock_embedding.embed_single.return_value = [0.1] * 768
    mock_embedding_cls.return_value = mock_embedding

    payload = {"chunk_id": "c1", "text": "low score", "product_name": "A"}
    mock_store = MagicMock()
    mock_store.search.return_value = [_make_qdrant_result(payload, score=0.5, point_id=1)]
    mock_vector_store_cls.return_value = mock_store

    retriever = Retriever()
    results = retriever.retrieve("test", top_k=5)

    assert len(results) == 0
