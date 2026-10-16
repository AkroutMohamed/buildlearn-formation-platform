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


class TestGroundedness:
    def _build_service(self, mock_retriever, mock_llm):
        with patch("app.ai.rag.rag_service.Retriever", return_value=mock_retriever), \
             patch("app.ai.rag.rag_service.OllamaProvider", return_value=mock_llm):
            return RAGService()

    def test_llm_receives_system_prompt_when_context_provided(self):
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
        service.run(request)

        call_args = mock_llm.generate.call_args
        request_arg = call_args.args[0]
        context_arg = call_args.args[1]
        assert isinstance(request_arg, ChatRequest)
        assert request_arg.question == "What is Gyproc Moisture Resistant Board?"
        assert "Moisture resistant board specification." in context_arg
        assert "BA13 Hydro" in context_arg

    def test_context_contains_expected_product_and_supplier(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            _make_chunk(text="Fireline has 60-minute fire rating.", product_name="BA13 Feu", document_url="https://www.gyproc.in/pdf/fireline.pdf")
        ]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="BA13 Feu has a 60-minute fire rating.",
            sources=[],
            conversation_id="conv-1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is Gyproc Fireline Board?")
        service.run(request)

        call_args = mock_llm.generate.call_args
        context_arg = call_args.args[1]
        assert "BA13 Feu" in context_arg
        assert "GYPROC" in context_arg
        assert "60-minute fire rating" in context_arg

    def test_sources_preserved_in_final_response(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            _make_chunk(
                id="c1", chunk_id="c1", content_hash="h1",
                text="Duraline board details.",
                product_name="BA13 Hydro",
                document_url="https://www.gyproc.in/pdf/duraline.pdf",
                source_type="external_official",
                discovery_provider="manufacturer_targeted",
                domain="www.gyproc.in",
                confidence="high",
                score=0.95,
            ),
        ]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="BA13 Hydro Duraline board details.",
            sources=[],
            conversation_id="conv-1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is Gyproc Duraline Board?")
        response = service.run(request)

        assert len(response.sources) == 1
        source = response.sources[0]
        assert source["product_name"] == "BA13 Hydro"
        assert source["supplier"] == "GYPROC"
        assert source["document_url"] == "https://www.gyproc.in/pdf/duraline.pdf"
        assert source["source_type"] == "external_official"
        assert source["discovery_provider"] == "manufacturer_targeted"
        assert source["domain"] == "www.gyproc.in"
        assert source["confidence"] == "high"
        assert source["score"] == 0.95

    def test_empty_context_triggers_refusal_without_llm_call(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []

        mock_llm = MagicMock()

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is the meaning of life?")
        response = service.run(request)

        assert "not found" in response.answer.lower()
        assert response.sources == []
        mock_llm.generate.assert_not_called()

    def test_grounded_answer_uses_provided_context_content(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            _make_chunk(text="Moisture Resistant Board is designed for high humidity areas."),
        ]

        captured_context = {}

        def capture_generate(request, context, history=None):
            captured_context["context"] = context
            return ChatResponse(
                answer="Moisture Resistant Board is designed for high humidity areas.",
                sources=[],
                conversation_id="conv-1",
                created_at=MagicMock(),
            )

        mock_llm = MagicMock()
        mock_llm.generate.side_effect = capture_generate

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="What is Gyproc Moisture Resistant Board?")
        service.run(request)

        assert "high humidity areas" in captured_context["context"]
        assert "Moisture Resistant Board" in captured_context["context"]

    def test_multiple_chunks_aggregated_in_context(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            _make_chunk(id="c1", chunk_id="c1", content_hash="h1", text="Moisture resistant properties."),
            _make_chunk(id="c2", chunk_id="c2", content_hash="h2", text="Fire resistant properties.", product_name="BA13 Feu"),
        ]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = ChatResponse(
            answer="Aggregated answer.",
            sources=[],
            conversation_id="conv-1",
            created_at=MagicMock(),
        )

        service = self._build_service(mock_retriever, mock_llm)
        request = ChatRequest(question="Compare boards")
        service.run(request)

        call_args = mock_llm.generate.call_args
        context_arg = call_args.args[1]
        assert "Moisture resistant properties." in context_arg
        assert "Fire resistant properties." in context_arg
        assert "BA13 Feu" in context_arg
