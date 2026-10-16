from unittest.mock import MagicMock, patch

import pytest

from app.ai.rag.rag_service import RAGService
from app.ai.schemas.chat import ChatRequest, ChatResponse
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
        "text": "BA13 Hydro is a moisture resistant board.",
        "language": "en",
        "content_hash": "hash001",
        "metadata": {"char_count": 50},
        "source_type": "external_official",
        "discovery_provider": "manufacturer_targeted",
        "domain": "www.gyproc.in",
        "confidence": "high",
        "evidence": "Found via gypsobat",
        "score": 0.95,
    }
    defaults.update(kwargs)
    return ChunkResponse(**defaults)


class TestProvenanceEvaluation:
    def _build_service(self, mock_retriever, mock_llm):
        with patch("app.ai.rag.rag_service.Retriever", return_value=mock_retriever), \
             patch("app.ai.rag.rag_service.OllamaProvider", return_value=mock_llm):
            return RAGService()

    def test_all_provenance_fields_preserved_through_rag_service(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            _make_chunk(
                id="c1", chunk_id="c1", content_hash="h1",
                product_name="BA13 Hydro",
                document_url="https://www.gyproc.in/pdf/moisture.pdf",
                source_type="external_official",
                discovery_provider="manufacturer_targeted",
                domain="www.gyproc.in",
                confidence="high",
                evidence="Found via gypsobat",
                score=0.95,
            ),
        ]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="BA13 Hydro is a moisture resistant board.",
            sources=[],
            conversation_id="conv-1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is Moisture Resistant Board?")
        response = service.run(request)

        assert len(response.sources) == 1
        source = response.sources[0]
        assert source["product_name"] == "BA13 Hydro"
        assert source["supplier"] == "GYPROC"
        assert source["document_url"] == "https://www.gyproc.in/pdf/moisture.pdf"
        assert source["source_type"] == "external_official"
        assert source["discovery_provider"] == "manufacturer_targeted"
        assert source["domain"] == "www.gyproc.in"
        assert source["confidence"] == "high"
        assert source["evidence"] == "Found via gypsobat"
        assert source["score"] == 0.95
        assert source["chunk_id"] == "c1"
        assert source["document_id"] == "doc-1"

    def test_provenance_fields_with_none_values_preserved(self):
        from app.ai.rag.context_builder import ContextBuilder

        chunk = _make_chunk(
            id="c1", chunk_id="c1",
            product_name=None,
            supplier=None,
            source_url=None,
            document_url=None,
            domain=None,
            source_type=None,
            discovery_provider=None,
            confidence=None,
            evidence=None,
            score=None,
        )
        result = ContextBuilder.build([chunk])
        source = result.sources[0]
        assert source["product_name"] is None
        assert source["supplier"] is None
        assert source["document_url"] is None
        assert source["source_url"] is None
        assert source["domain"] is None
        assert source["source_type"] is None
        assert source["discovery_provider"] is None
        assert source["confidence"] is None
        assert source["evidence"] is None
        assert source["score"] is None
        assert source["chunk_id"] == "c1"
        assert source["document_id"] == "doc-1"

    def test_multiple_sources_each_preserve_independent_provenance(self):
        from app.ai.rag.context_builder import ContextBuilder

        chunk1 = _make_chunk(
            id="c1", chunk_id="c1", content_hash="hash-a",
            product_name="BA13 Hydro",
            document_url="https://www.gyproc.in/pdf/moisture.pdf",
            score=0.95, source_type="external_official",
        )
        chunk2 = _make_chunk(
            id="c2", chunk_id="c2", content_hash="hash-b",
            product_name="BA13 Feu",
            document_url="https://www.gyproc.in/pdf/fireline.pdf",
            score=0.90, source_type="external_official",
        )
        result = ContextBuilder.build([chunk1, chunk2])
        assert len(result.sources) == 2
        assert result.sources[0]["product_name"] == "BA13 Hydro"
        assert result.sources[0]["document_url"] == "https://www.gyproc.in/pdf/moisture.pdf"
        assert result.sources[0]["score"] == 0.95
        assert result.sources[1]["product_name"] == "BA13 Feu"
        assert result.sources[1]["document_url"] == "https://www.gyproc.in/pdf/fireline.pdf"
        assert result.sources[1]["score"] == 0.90

    def test_retriever_preserves_provenance_from_payload(self):
        with patch("app.ai.rag.retriever.EmbeddingProvider") as mock_embedding_cls, \
             patch("app.ai.rag.retriever.VectorStore") as mock_vector_store_cls:
            mock_embedding = MagicMock()
            mock_embedding.embed_single.return_value = [0.1] * 768
            mock_embedding_cls.return_value = mock_embedding

            payload = {
                "chunk_id": "prov-1",
                "document_id": "doc-prov",
                "product_id": "prod-prov",
                "product_name": "BA13 Hydro",
                "supplier": "GYPROC",
                "source": "gypsobat",
                "source_url": "https://x.com/p1/",
                "document_url": "https://www.gyproc.in/pdf/moisture.pdf",
                "document_type": "technical_sheet",
                "page_number": 1,
                "section_title": "MOISTURE RESISTANCE",
                "chunk_index": 0,
                "text": "Moisture resistant board.",
                "language": "en",
                "content_hash": "hash-prov",
                "metadata": {"char_count": 30},
                "source_type": "external_official",
                "discovery_provider": "manufacturer_targeted",
                "domain": "www.gyproc.in",
                "confidence": "high",
                "evidence": "Found via gypsobat",
            }
            mock_store = MagicMock()
            mock_store.search.return_value = [{"id": 999, "score": 0.98, "payload": payload}]
            mock_vector_store_cls.return_value = mock_store

            from app.ai.rag.retriever import Retriever
            retriever = Retriever()
            results = retriever.retrieve("test query", top_k=5)

        assert len(results) == 1
        r = results[0]
        assert r.product_name == "BA13 Hydro"
        assert r.supplier == "GYPROC"
        assert r.source_type == "external_official"
        assert r.discovery_provider == "manufacturer_targeted"
        assert r.domain == "www.gyproc.in"
        assert r.confidence == "high"
        assert r.evidence == "Found via gypsobat"
        assert r.source_url == "https://x.com/p1/"
        assert r.document_url == "https://www.gyproc.in/pdf/moisture.pdf"
        assert r.score == 0.98
        assert r.chunk_id == "prov-1"
        assert r.document_id == "doc-prov"
