from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ChatMessageHistory(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    top_k: Optional[int] = 5
    messages: list[ChatMessageHistory] = []


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]] = []
    conversation_id: str
    created_at: datetime
