from abc import ABC, abstractmethod
from typing import Any

from app.ai.schemas.chat import ChatRequest, ChatResponse


class BaseRAGPipeline(ABC):
    @abstractmethod
    def run(self, request: ChatRequest) -> ChatResponse:
        ...
