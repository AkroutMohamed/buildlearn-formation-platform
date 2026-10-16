from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.ai.config import ai_settings
from app.ai.llm.ollama import OllamaProvider
from app.ai.schemas.chat import ChatRequest, ChatResponse


def _mock_ollama_chat_response(content: str = "This is a grounded answer."):
    return {"message": {"role": "assistant", "content": content}}


class TestOllamaProvider:
    def test_successful_generation(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = _mock_ollama_chat_response("Grounded answer about Gyproc boards.")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="What is Gyproc Moisture Resistant Board?")
            context = "[DOCUMENT 1/1]\nProduct: BA13 Hydro\nSupplier: GYPROC\nMoisture resistant board."

            response = provider.generate(request, context)

            assert isinstance(response, ChatResponse)
            assert "Grounded answer" in response.answer
            assert response.sources == []
            assert response.conversation_id is not None

    def test_generation_respects_configuration(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://custom-host:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "my-custom-llm")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = _mock_ollama_chat_response("Answer")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="test?")
            provider.generate(request, "context")

            mock_client_cls.assert_called_with(host="http://custom-host:11434")
            call_args = mock_client.chat.call_args
            assert call_args.kwargs["model"] == "my-custom-llm"
            assert len(call_args.kwargs["messages"]) == 2
            assert call_args.kwargs["messages"][0]["role"] == "system"
            assert call_args.kwargs["messages"][1]["role"] == "user"

    def test_raises_when_config_incomplete(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "")
        monkeypatch.setattr(ai_settings, "ollama_model", "")

        provider = OllamaProvider()
        request = ChatRequest(question="test?")
        with pytest.raises(RuntimeError, match="configuration is incomplete"):
            provider.generate(request, "context")

    def test_raises_when_base_url_missing(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        provider = OllamaProvider()
        request = ChatRequest(question="test?")
        with pytest.raises(RuntimeError, match="configuration is incomplete"):
            provider.generate(request, "context")

    def test_raises_when_model_missing(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "")

        provider = OllamaProvider()
        request = ChatRequest(question="test?")
        with pytest.raises(RuntimeError, match="configuration is incomplete"):
            provider.generate(request, "context")

    def test_handles_ollama_connection_error(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.side_effect = ConnectionError("Ollama server not reachable")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="test?")
            with pytest.raises(RuntimeError, match="LLM generation failed"):
                provider.generate(request, "context")

    def test_handles_unexpected_response_format(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = {"unexpected": "format"}
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="test?")
            with pytest.raises(RuntimeError, match="unexpected response format"):
                provider.generate(request, "context")

    def test_handles_empty_response_content(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = {"message": {"role": "assistant", "content": ""}}
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="test?")
            with pytest.raises(RuntimeError, match="empty response"):
                provider.generate(request, "context")

    def test_prompt_includes_system_and_user_messages(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = _mock_ollama_chat_response("Answer")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="What is fireline board?")
            context = "Document content about fireline."
            provider.generate(request, context)

            messages = mock_client.chat.call_args.kwargs["messages"]
            assert messages[0]["role"] == "system"
            assert "construction products" in messages[0]["content"]
            assert messages[1]["role"] == "user"
            assert "What is fireline board?" in messages[1]["content"]
            assert "Document content about fireline." in messages[1]["content"]

    def test_generation_includes_conversation_history(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = _mock_ollama_chat_response("It has a 60-minute fire rating.")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="What is its fire classification?")
            context = "Fireline has a 60-minute fire rating."
            history = [
                {"role": "user", "content": "What is Gyproc Fireline?"},
                {"role": "assistant", "content": "Gyproc Fireline is a fire-resistant plasterboard."},
            ]
            provider.generate(request, context, history=history)

            messages = mock_client.chat.call_args.kwargs["messages"]
            user_prompt = messages[1]["content"]
            assert "Previous conversation:" in user_prompt
            assert "What is Gyproc Fireline?" in user_prompt
            assert "What is its fire classification?" in user_prompt

    def test_history_is_trimmed_to_max_turns(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = _mock_ollama_chat_response("Answer")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="latest")
            history = [{"role": "user", "content": f"turn {i}"} for i in range(20)]
            provider.generate(request, "context", history=history)

            user_prompt = mock_client.chat.call_args.kwargs["messages"][1]["content"]
            assert "turn 0" not in user_prompt
            assert "turn 19" in user_prompt

    def test_conversation_id_preserved(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = _mock_ollama_chat_response("Answer")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="test?", conversation_id="conv-123")
            response = provider.generate(request, "context")
            assert response.conversation_id == "conv-123"

    def test_strips_whitespace_from_answer(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = _mock_ollama_chat_response("  Answer with spaces  \n\n")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="test?")
            response = provider.generate(request, "context")
            assert response.answer == "Answer with spaces"

    def test_created_at_is_set(self, monkeypatch):
        monkeypatch.setattr(ai_settings, "ollama_base_url", "http://localhost:11434")
        monkeypatch.setattr(ai_settings, "ollama_model", "qwen2.5")

        with patch("ollama.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.return_value = _mock_ollama_chat_response("Answer")
            mock_client_cls.return_value = mock_client

            provider = OllamaProvider()
            request = ChatRequest(question="test?")
            response = provider.generate(request, "context")
            assert isinstance(response.created_at, datetime)
