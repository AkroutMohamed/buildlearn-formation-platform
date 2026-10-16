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


class TestRefusal:
    def _build_service(self, mock_retriever, mock_llm):
        with patch("app.ai.rag.rag_service.Retriever", return_value=mock_retriever), \
             patch("app.ai.rag.rag_service.OllamaProvider", return_value=mock_llm):
            return RAGService()

    def test_out_of_context_question_returns_not_found(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []

        mock_llm = MagicMock()

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is the meaning of life?")
        response = service.run(request)

        assert "not found" in response.answer.lower() or "not found in the available documentation" in response.answer.lower()
        assert response.sources == []
        mock_llm.generate.assert_not_called()

    def test_empty_retrieval_does_not_call_llm(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []

        mock_llm = MagicMock()

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is quantum gravity?")
        response = service.run(request)

        mock_llm.generate.assert_not_called()
        assert len(response.sources) == 0

    def test_retriever_exception_does_not_call_llm(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.side_effect = RuntimeError("Qdrant connection refused")

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="I fabricated this answer.",
            sources=[],
            conversation_id="x",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is BA13 Hydro?")
        with pytest.raises(RuntimeError, match="Retrieval failed"):
            service.run(request)
        mock_llm.generate.assert_not_called()

    def test_context_builder_empty_chunks_returns_empty(self):
        from app.ai.rag.context_builder import ContextBuilder, BuiltContext

        result = ContextBuilder.build([])
        assert isinstance(result, BuiltContext)
        assert result.context == ""
        assert result.sources == []
        assert result.chunk_count == 0

    def test_unsupported_price_question_does_not_fabricate(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            _make_chunk(text="Gyproc Fireline Board is designed for fire-resistant applications."),
        ]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="The exact price is not provided in the available documentation.",
            sources=[],
            conversation_id="conv-1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is the exact price of Gyproc Fireline Board?")
        response = service.run(request)

        assert "not provided" in response.answer.lower() or "not found" in response.answer.lower() or "not available" in response.answer.lower()
        mock_llm.generate.assert_called_once()

    def test_unsupported_spec_question_does_not_fabricate(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            _make_chunk(text="Gyproc Moisture Resistant Board is used in bathrooms."),
        ]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="The specific chemical composition is not mentioned in the available documentation.",
            sources=[],
            conversation_id="conv-1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is the exact chemical composition of Gyproc Moisture Resistant Board?")
        response = service.run(request)

        assert "not mentioned" in response.answer.lower() or "not found" in response.answer.lower() or "not available" in response.answer.lower()
        mock_llm.generate.assert_called_once()

    def test_meaning_of_life_refusal_with_sources_empty(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []

        mock_llm = MagicMock()

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is the meaning of life?")
        response = service.run(request)

        assert response.sources == []
        mock_llm.generate.assert_not_called()
