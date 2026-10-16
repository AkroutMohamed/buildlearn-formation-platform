import logging
from datetime import datetime, timezone
from uuid import uuid4

from app.ai.config import ai_settings
from app.ai.llm.base import BaseLLMProvider
from app.ai.rag.prompts import SYSTEM_PROMPT, build_prompt
from app.ai.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

MAX_HISTORY_TURNS = 6
MAX_HISTORY_CHARS = 4000


class OllamaProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self._base_url = ai_settings.ollama_base_url
        self._model = ai_settings.ollama_model

    def generate(self, request: ChatRequest, context: str, history: list[dict[str, str]] | None = None) -> ChatResponse:
        if not ai_settings.ollama_base_url or not ai_settings.ollama_model:
            raise RuntimeError("Ollama configuration is incomplete: check OLLAMA_BASE_URL and OLLAMA_MODEL")

        import ollama

        client = ollama.Client(host=self._base_url)

        trimmed_history = self._trim_history(history)
        prompt = build_prompt(request.question, context, trimmed_history)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = client.chat(
                model=self._model,
                messages=messages,
            )
        except Exception as exc:
            logger.error("Ollama LLM generation failed: %s", exc)
            raise RuntimeError(f"LLM generation failed: {exc}") from exc

        message = getattr(response, "message", None)
        if message is None and isinstance(response, dict):
            message = response.get("message")
        if message is None:
            raise RuntimeError("Ollama returned an unexpected response format: no 'message' field")

        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content", "")
        if not content:
            raise RuntimeError("Ollama returned an empty response")

        conversation_id = request.conversation_id or str(uuid4())

        return ChatResponse(
            answer=content.strip(),
            sources=[],
            conversation_id=conversation_id,
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _trim_history(history: list[dict[str, str]] | None) -> list[dict[str, str]]:
        if not history:
            return []

        trimmed: list[dict[str, str]] = []
        total_chars = 0
        for turn in reversed(history):
            if len(trimmed) >= MAX_HISTORY_TURNS:
                break
            content = turn.get("content", "")
            if total_chars + len(content) > MAX_HISTORY_CHARS:
                break
            trimmed.append(turn)
            total_chars += len(content)

        return list(reversed(trimmed))
