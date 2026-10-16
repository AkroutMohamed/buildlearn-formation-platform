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


class TestRAGService:
    def _build_service(self, mock_retriever, mock_llm):
        with patch("app.ai.rag.rag_service.Retriever", return_value=mock_retriever), \
             patch("app.ai.rag.rag_service.OllamaProvider", return_value=mock_llm):
            return RAGService()

    def test_full_pipeline_question_to_answer(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [_make_chunk(text="Moisture resistant board specification.")]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="BA13 Hydro is a moisture resistant board.",
            sources=[],
            conversation_id="conv-1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is Gyproc Moisture Resistant Board?")
        response = service.run(request)

        assert isinstance(response, ChatResponse)
        assert response.answer == "BA13 Hydro is a moisture resistant board."
        assert len(response.sources) == 1
        assert response.sources[0]["product_name"] == "BA13 Hydro"
        assert response.sources[0]["supplier"] == "GYPROC"
        assert response.sources[0]["score"] == 0.95

    def test_empty_retrieval_returns_not_found_answer(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []

        mock_llm = MagicMock()

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is the meaning of life?")
        response = service.run(request)

        assert "not found" in response.answer.lower()
        assert response.sources == []
        mock_llm.generate.assert_not_called()

    def test_llm_failure_raises_runtime_error(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [_make_chunk()]

        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("Ollama is down")

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is the board made of?")
        with pytest.raises(RuntimeError, match="LLM generation failed"):
            service.run(request)

    def test_retriever_failure_raises_runtime_error(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.side_effect = RuntimeError("Qdrant connection refused")

        mock_llm = MagicMock()

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="test")
        with pytest.raises(RuntimeError, match="Retrieval failed"):
            service.run(request)
        mock_llm.generate.assert_not_called()

    def test_retriever_failure_does_not_fabricate_answer(self):
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
        with pytest.raises(RuntimeError):
            response = service.run(request)
        mock_llm.generate.assert_not_called()

    def test_provenance_returned_in_sources(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            _make_chunk(
                id="c1", chunk_id="c1", content_hash="h1",
                text="Moisture resistant board.",
                product_name="BA13 Hydro",
                document_url="https://www.gyproc.in/pdf/moisture.pdf",
                source_type="external_official",
                discovery_provider="manufacturer_targeted",
                domain="www.gyproc.in",
                confidence="high",
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
        assert source["score"] == 0.95

    def test_empty_question_raises_value_error(self):
        mock_retriever = MagicMock()
        mock_llm = MagicMock()
        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="")
        with pytest.raises(ValueError, match="empty"):
            service.run(request)
        mock_retriever.retrieve.assert_not_called()

    def test_whitespace_question_raises_value_error(self):
        mock_retriever = MagicMock()
        mock_llm = MagicMock()
        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="   ")
        with pytest.raises(ValueError, match="empty"):
            service.run(request)
        mock_retriever.retrieve.assert_not_called()

    def test_top_k_defaults_to_5(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [_make_chunk()]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="Answer",
            sources=[],
            conversation_id="c1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="test")
        service.run(request)

        mock_retriever.retrieve.assert_called_once()
        call_args = mock_retriever.retrieve.call_args
        assert call_args.kwargs["top_k"] == 5

    def test_top_k_from_request_respected(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [_make_chunk()]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="Answer",
            sources=[],
            conversation_id="c1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="test", top_k=10)
        service.run(request)

        call_args = mock_retriever.retrieve.call_args
        assert call_args.kwargs["top_k"] == 10

    def test_conversation_id_preserved(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [_make_chunk()]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="Answer",
            sources=[],
            conversation_id="conv-from-llm",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="test", conversation_id="req-conv-id")
        response = service.run(request)

        assert response.conversation_id == "req-conv-id"

    def test_passes_context_to_llm(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [_make_chunk(
            id="c1", chunk_id="c1", content_hash="h1",
            text="Board specification content.",
        )]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="Answer",
            sources=[],
            conversation_id="c1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What are specs?")
        service.run(request)

        call_args = mock_llm.generate.call_args
        context = call_args.args[1]
        assert "Board specification content." in context
        assert "Product: BA13 Hydro" in context
        assert "Supplier: GYPROC" in context

    def test_history_passed_to_llm(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [_make_chunk()]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="Answer",
            sources=[],
            conversation_id="c1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is its fire classification?")
        history = [
            {"role": "user", "content": "What is Gyproc Fireline?"},
            {"role": "assistant", "content": "It is a fire-resistant board."},
        ]
        service.run(request, history=history)

        call_args = mock_llm.generate.call_args
        assert call_args.kwargs["history"] == history
