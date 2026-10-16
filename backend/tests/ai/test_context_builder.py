from unittest.mock import MagicMock, patch

import pytest

from app.ai.rag.context_builder import BuiltContext, ContextBuilder
from app.ai.schemas.chunk import ChunkResponse


def _make_chunk(**kwargs) -> ChunkResponse:
    defaults = {
        "id": "chunk-001",
        "chunk_id": "chunk-001",
        "document_id": "doc-1",
        "product_id": "prod-1",
        "product_name": "BA13 Hydro",
        "supplier": "GYPROC",
        "source": "gypsobat",
        "source_url": "https://www.gyproc.in/p1",
        "document_url": "https://www.gyproc.in/pdf/doc1.pdf",
        "document_type": "technical_sheet",
        "page_number": 1,
        "section_title": "SECTION A",
        "chunk_index": 0,
        "text": "BA13 Hydro is a moisture resistant board made of gypsum.",
        "language": "en",
        "content_hash": "hash001",
        "metadata": {"char_count": 50, "word_count": 10},
        "source_type": "external_official",
        "discovery_provider": "manufacturer_targeted",
        "domain": "www.gyproc.in",
        "confidence": "high",
        "evidence": "Found via gypsobat",
        "score": 0.95,
    }
    defaults.update(kwargs)
    return ChunkResponse(**defaults)


class TestContextBuilder:
    def test_empty_chunks_returns_empty(self):
        result = ContextBuilder.build([])
        assert isinstance(result, BuiltContext)
        assert result.context == ""
        assert result.sources == []
        assert result.chunk_count == 0

    def test_single_chunk_becomes_valid_context(self):
        chunk = _make_chunk(text="Gyproc Moisture Resistant Board has high moisture resistance.")
        result = ContextBuilder.build([chunk])
        assert result.context != ""
        assert "Gyproc Moisture Resistant Board" in result.context
        assert result.chunk_count == 1
        assert len(result.sources) == 1

    def test_multiple_chunks_become_valid_context(self):
        chunk1 = _make_chunk(
            id="c1", chunk_id="c1", content_hash="h1", text="Moisture resistant board details.",
            product_name="BA13 Hydro",
        )
        chunk2 = _make_chunk(
            id="c2", chunk_id="c2", content_hash="h2", text="Fire resistant board details.",
            product_name="BA13 Feu", document_url="https://www.gyproc.in/pdf/doc2.pdf",
        )
        result = ContextBuilder.build([chunk1, chunk2])
        assert result.chunk_count == 2
        assert len(result.sources) == 2
        assert "Moisture resistant board" in result.context
        assert "Fire resistant board" in result.context
        assert "BA13 Hydro" in result.context
        assert "BA13 Feu" in result.context

    def test_provenance_preserved_in_sources(self):
        chunk = _make_chunk()
        result = ContextBuilder.build([chunk])
        assert len(result.sources) == 1
        source = result.sources[0]
        assert source["product_name"] == "BA13 Hydro"
        assert source["supplier"] == "GYPROC"
        assert source["document_url"] == "https://www.gyproc.in/pdf/doc1.pdf"
        assert source["source_url"] == "https://www.gyproc.in/p1"
        assert source["domain"] == "www.gyproc.in"
        assert source["source_type"] == "external_official"
        assert source["discovery_provider"] == "manufacturer_targeted"
        assert source["score"] == 0.95
        assert source["confidence"] == "high"
        assert source["evidence"] == "Found via gypsobat"

    def test_provenance_in_context_string(self):
        chunk = _make_chunk(text="Technical spec content here.")
        result = ContextBuilder.build([chunk])
        assert "Product: BA13 Hydro" in result.context
        assert "Supplier: GYPROC" in result.context
        assert "Document URL: https://www.gyproc.in/pdf/doc1.pdf" in result.context
        assert "Confidence: high" in result.context
        assert "Technical spec content here." in result.context

    def test_duplicate_documents_are_deduplicated(self):
        chunk1 = _make_chunk(
            id="c1", chunk_id="c1", content_hash="same_hash", text="Same document content.",
            product_name="BA13 Hydro",
        )
        chunk2 = _make_chunk(
            id="c2", chunk_id="c2", content_hash="same_hash", text="Same document content.",
            product_name="BA13 Hydro",
        )
        result = ContextBuilder.build([chunk1, chunk2])
        assert result.chunk_count == 1
        assert len(result.sources) == 1

    def test_different_documents_same_hash_not_deduplicated_if_different_content_hash(self):
        chunk1 = _make_chunk(
            id="c1", chunk_id="c1", content_hash="hash_a", text="Content A",
            product_name="BA13 Hydro",
        )
        chunk2 = _make_chunk(
            id="c2", chunk_id="c2", content_hash="hash_b", text="Content B",
            product_name="BA13 Feu",
        )
        result = ContextBuilder.build([chunk1, chunk2])
        assert result.chunk_count == 2

    def test_deduplication_falls_back_to_chunk_id(self):
        chunk1 = _make_chunk(
            id="c1", chunk_id="c1", content_hash=None, text="Content A",
        )
        chunk2 = _make_chunk(
            id="c2", chunk_id="c1", content_hash=None, text="Content A",
        )
        result = ContextBuilder.build([chunk1, chunk2])
        assert result.chunk_count == 1

    def test_max_chars_truncation(self):
        chunk = _make_chunk(text="A" * 20000)
        result = ContextBuilder.build([chunk], max_chars=100)
        assert len(result.context) <= 100

    def test_chunks_with_empty_text(self):
        chunk = _make_chunk(text=None)
        result = ContextBuilder.build([chunk])
        assert result.chunk_count == 1
        assert len(result.sources) == 1
        assert "Product: BA13 Hydro" in result.context

    def test_score_ordering_preserved(self):
        chunk1 = _make_chunk(
            id="c1", chunk_id="c1", content_hash="h1", text="Low score", score=0.3,
        )
        chunk2 = _make_chunk(
            id="c2", chunk_id="c2", content_hash="h2", text="High score", score=0.95,
        )
        result = ContextBuilder.build([chunk1, chunk2])
        assert result.sources[0]["score"] == 0.3
        assert result.sources[1]["score"] == 0.95

    def test_preserves_all_provenance_fields(self):
        chunk = _make_chunk()
        result = ContextBuilder.build([chunk])
        source = result.sources[0]
        expected_fields = {
            "product_name", "supplier", "document_url", "source_url", "domain",
            "source_type", "discovery_provider", "score", "confidence", "evidence",
            "chunk_id", "document_id",
        }
        for field in expected_fields:
            assert field in source, f"Missing provenance field: {field}"
