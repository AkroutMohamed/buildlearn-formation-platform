from unittest.mock import MagicMock, patch

import pytest

from app.ai.chunking.models import ChildChunk, SourceInfo, BlockType
from app.ai.config import ai_settings
from app.ai.vectorstore.provider import VectorStore
from app.ai.vectorstore.qdrant_provider import QdrantVectorStore
from qdrant_client.http import models as qdrant_models


def _make_chunk(**kwargs):
    defaults = {
        "chunk_id": "abc123def4567890",
        "document_id": "doc-1",
        "product_id": "prod-1",
        "product_name": "Test Product",
        "supplier": "Test Supplier",
        "source": "gypsobat",
        "source_url": "https://example.com",
        "document_url": "https://example.com/doc.pdf",
        "document_type": "technical_sheet",
        "page_number": 1,
        "section_title": "SECTION A",
        "chunk_index": 0,
        "text": "Test chunk text",
        "language": "fr",
        "content_hash": "hash123",
    }
    defaults.update(kwargs)
    return defaults


def _make_child_chunk(**kwargs):
    defaults = {
        "chunk_id": "abc123def4567890",
        "chunk_type": BlockType.RAW_TEXT,
        "text": "Test child chunk text",
        "source": SourceInfo(
            document_id="doc-1",
            source_path="/path/to/doc.pdf",
            file_name="doc.pdf",
        ),
        "section_path": ["SECTION A", "SUBSECTION B"],
        "page_start": 1,
        "page_end": 2,
        "parent_id": "parent-1",
        "block_type": BlockType.PARAGRAPH,
    }
    defaults.update(kwargs)
    return ChildChunk(**defaults)


def test_vector_store_requires_config(monkeypatch):
    monkeypatch.setattr(ai_settings, "vector_store", "")
    with pytest.raises(RuntimeError, match="Vector store is not configured"):
        VectorStore()


def test_vector_store_unsupported_provider(monkeypatch):
    monkeypatch.setattr(ai_settings, "vector_store", "pinecone")
    with pytest.raises(RuntimeError, match="Unsupported vector store"):
        VectorStore()


def test_vector_store_qdrant_dispatch(monkeypatch):
    monkeypatch.setattr(ai_settings, "vector_store", "qdrant")
    monkeypatch.setattr(ai_settings, "qdrant_url", "http://localhost:6333")
    monkeypatch.setattr(ai_settings, "qdrant_collection", "test_collection")

    with patch("app.ai.vectorstore.provider.QdrantVectorStore") as MockQdrant:
        store = VectorStore()
        assert isinstance(store._provider, MagicMock)


def test_qdrant_upsert_chunks():
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        chunks = [_make_chunk()]
        embeddings = [[0.1] * 768]

        store.upsert_chunks(chunks, embeddings)

        mock_client.upsert.assert_called_once()
        call_kwargs = mock_client.upsert.call_args.kwargs
        assert call_kwargs["collection_name"] == "test_collection"
        points = call_kwargs["points"]
        assert len(points) == 1
        assert points[0].id == int("abc123def4567890", 16)
        assert points[0].vector == [0.1] * 768
        assert points[0].payload["document_id"] == "doc-1"
        assert points[0].payload["text"] == "Test chunk text"


def test_qdrant_upsert_chunks_dict_input():
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        chunks = [_make_chunk()]
        embeddings = [[0.1] * 768]

        store.upsert_chunks(chunks, embeddings)
        points = mock_client.upsert.call_args.kwargs["points"]
        assert points[0].payload["chunk_id"] == "abc123def4567890"


def test_qdrant_upsert_mismatched_lengths():
    store = QdrantVectorStore()
    store._collection = "test_collection"

    with pytest.raises(ValueError, match="Number of chunks"):
        store.upsert_chunks([_make_chunk()], [[0.1] * 768, [0.2] * 768])


def test_qdrant_search():
    mock_client = MagicMock()
    mock_point = MagicMock()
    mock_point.id = "point1"
    mock_point.score = 0.95
    mock_point.payload = {"text": "result"}
    mock_client.query_points.return_value.points = [mock_point]

    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        query_vector = [0.1] * 768
        results = store.search(query_vector, top_k=3, filters={"source": "gypsobat"})

        assert len(results) == 1
        assert results[0]["id"] == "point1"
        assert results[0]["score"] == 0.95
        assert results[0]["payload"] == {"text": "result"}

        call_kwargs = mock_client.query_points.call_args.kwargs
        assert call_kwargs["limit"] == 3
        assert call_kwargs["query"] == query_vector
        assert call_kwargs["query_filter"] is not None


def test_qdrant_search_without_filters():
    mock_client = MagicMock()
    mock_client.query_points.return_value.points = []

    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        store.search([0.1] * 768)

        call_kwargs = mock_client.query_points.call_args.kwargs
        assert call_kwargs["query_filter"] is None


def test_qdrant_delete_by_document():
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        store.delete_by_document("doc-1")

        mock_client.delete.assert_called_once()
        selector = mock_client.delete.call_args.kwargs["points_selector"]
        assert selector.filter.must[0].key == "document_id"
        assert selector.filter.must[0].match.value == "doc-1"


def test_qdrant_delete_by_product():
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        store.delete_by_product("prod-1")

        mock_client.delete.assert_called_once()
        selector = mock_client.delete.call_args.kwargs["points_selector"]
        assert selector.filter.must[0].key == "product_id"
        assert selector.filter.must[0].match.value == "prod-1"


def test_qdrant_collection_exists_true():
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        assert store.collection_exists() is True
        mock_client.collection_exists.assert_called_once_with("test_collection")


def test_qdrant_collection_exists_false():
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        assert store.collection_exists() is False


def test_qdrant_health_check():
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()

        assert store.health_check() is True
        mock_client.get_collections.assert_called_once()


def test_qdrant_health_check_failure():
    mock_client = MagicMock()
    mock_client.get_collections.side_effect = Exception("connection error")
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()

        assert store.health_check() is False


def test_qdrant_collection_info():
    mock_client = MagicMock()
    mock_info = MagicMock()
    mock_info.status = "green"
    mock_info.points_count = 42
    mock_info.segments_count = 3
    mock_info.indexed_vectors_count = 42
    mock_client.get_collection.return_value = mock_info

    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        info = store.collection_info()

        assert info["name"] == "test_collection"
        assert info["status"] == "green"
        assert info["points_count"] == 42
        assert info["segments_count"] == 3


def test_qdrant_add_documents_raises():
    store = QdrantVectorStore()
    store._collection = "test_collection"

    with pytest.raises(RuntimeError, match="add_documents requires precomputed embeddings"):
        store.add_documents([_make_chunk()])


def test_qdrant_similarity_search_raises():
    store = QdrantVectorStore()
    store._collection = "test_collection"

    with pytest.raises(RuntimeError, match="similarity_search requires a precomputed query vector"):
        store.similarity_search("hello world")


def test_qdrant_delete_documents_delegates():
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        store.delete_documents("prod-1")

        mock_client.delete.assert_called_once()
        selector = mock_client.delete.call_args.kwargs["points_selector"]
        assert selector.filter.must[0].key == "product_id"


def test_qdrant_create_collection_detects_dimension_mismatch():
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    mock_info = MagicMock()
    mock_params = MagicMock()
    mock_vectors = qdrant_models.VectorParams(size=512, distance=qdrant_models.Distance.COSINE)
    mock_params.vectors = mock_vectors
    mock_info.config.params = mock_params
    mock_client.get_collection.return_value = mock_info

    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        with pytest.raises(RuntimeError, match="vector size 512"):
            store.create_collection(768)

        mock_client.create_collection.assert_not_called()


def test_qdrant_create_collection_detects_distance_mismatch():
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    mock_info = MagicMock()
    mock_params = MagicMock()
    mock_vectors = qdrant_models.VectorParams(size=768, distance=qdrant_models.Distance.EUCLID)
    mock_params.vectors = mock_vectors
    mock_info.config.params = mock_params
    mock_client.get_collection.return_value = mock_info

    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        with pytest.raises(RuntimeError, match="COSINE is required"):
            store.create_collection(768)

        mock_client.create_collection.assert_not_called()


def test_qdrant_create_collection_creates_when_missing():
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False

    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        store.create_collection(768)

        mock_client.create_collection.assert_called_once()
        call_kwargs = mock_client.create_collection.call_args.kwargs
        assert call_kwargs["collection_name"] == "test_collection"
        assert call_kwargs["vectors_config"].size == 768
        assert call_kwargs["vectors_config"].distance == qdrant_models.Distance.COSINE


def test_qdrant_constructor_collection_name_override():
    """Explicit collection_name override works."""
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore(collection_name="custom_collection")
        assert store._collection == "custom_collection"


def test_qdrant_constructor_use_hierarchical():
    """use_hierarchical=True picks the hierarchical collection from settings."""
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        with patch.object(ai_settings, "qdrant_collection_hierarchical", "buildlearn_products_hierarchical_v1"):
            store = QdrantVectorStore(use_hierarchical=True)
            assert store._collection == "buildlearn_products_hierarchical_v1"


def test_qdrant_constructor_explicit_overrides_hierarchical():
    """Explicit collection_name takes precedence over use_hierarchical."""
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        with patch.object(ai_settings, "qdrant_collection_hierarchical", "hierarchical_from_settings"):
            store = QdrantVectorStore(collection_name="explicit", use_hierarchical=True)
            assert store._collection == "explicit"


def test_qdrant_build_child_chunk_payload_exact_fields():
    """_build_child_chunk_payload produces exactly 10 expected fields from ChildChunk."""
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        chunk = _make_child_chunk()

        payload = store._build_child_chunk_payload(chunk)

        expected_keys = {
            "chunk_id", "document_id", "source_path", "file_name",
            "parent_id", "section_path", "page_start", "page_end",
            "block_type", "text",
        }
        assert set(payload.keys()) == expected_keys
        assert payload["chunk_id"] == "abc123def4567890"
        assert payload["document_id"] == "doc-1"
        assert payload["source_path"] == "/path/to/doc.pdf"
        assert payload["file_name"] == "doc.pdf"
        assert payload["parent_id"] == "parent-1"
        assert payload["section_path"] == ["SECTION A", "SUBSECTION B"]
        assert payload["page_start"] == 1
        assert payload["page_end"] == 2
        assert payload["block_type"] == "paragraph"
        assert payload["text"] == "Test child chunk text"


def test_qdrant_upsert_child_chunks():
    """upsert_child_chunks uses hierarchical payload and correct point IDs."""
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        chunks = [_make_child_chunk(chunk_id="c1"), _make_child_chunk(chunk_id="c2")]
        embeddings = [[0.1] * 768, [0.2] * 768]

        store.upsert_child_chunks(chunks, embeddings)

        mock_client.upsert.assert_called_once()
        call_kwargs = mock_client.upsert.call_args.kwargs
        assert call_kwargs["collection_name"] == "test_collection"
        points = call_kwargs["points"]
        assert len(points) == 2
        # Point IDs from hex chunk_ids
        assert points[0].id == int("c1", 16)
        assert points[1].id == int("c2", 16)
        # Vectors preserved
        assert points[0].vector == [0.1] * 768
        # Payload has hierarchical schema
        expected_keys = {
            "chunk_id", "document_id", "source_path", "file_name",
            "parent_id", "section_path", "page_start", "page_end",
            "block_type", "text",
        }
        assert set(points[0].payload.keys()) == expected_keys
        assert points[0].payload["chunk_id"] == "c1"
        assert points[0].payload["document_id"] == "doc-1"


def test_qdrant_upsert_child_chunks_mismatched_lengths():
    """upsert_child_chunks validates lengths match."""
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        chunks = [_make_child_chunk()]
        embeddings = [[0.1] * 768, [0.2] * 768]

        with pytest.raises(ValueError, match="Number of chunks"):
            store.upsert_child_chunks(chunks, embeddings)


def test_qdrant_legacy_upsert_chunks_unchanged():
    """Legacy upsert_chunks still uses old payload builder."""
    mock_client = MagicMock()
    with patch("app.ai.vectorstore.qdrant_provider.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore()
        store._collection = "test_collection"

        chunks = [_make_chunk()]
        embeddings = [[0.1] * 768]

        store.upsert_chunks(chunks, embeddings)

        points = mock_client.upsert.call_args.kwargs["points"]
        # Legacy payload has more fields
        assert "product_id" in points[0].payload
        assert "supplier" in points[0].payload
        assert "document_type" in points[0].payload
        # But not hierarchical fields
        assert "source_path" not in points[0].payload
        assert "section_path" not in points[0].payload
