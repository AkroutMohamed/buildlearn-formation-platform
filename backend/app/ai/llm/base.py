from abc import ABC, abstractmethod
from typing import Any

from app.ai.schemas.chat import ChatRequest, ChatResponse


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, request: ChatRequest, context: str, history: list[dict[str, str]] | None = None) -> ChatResponse:
        ...
