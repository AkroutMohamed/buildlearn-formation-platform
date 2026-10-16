import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.ai.config import ai_settings
from app.ai.rag.rag_service import RAGService
from app.ai.schemas.chat import ChatRequest, ChatResponse
from app.dependencies.chat import get_chat_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.chat import ConversationResponse, MessageResponse
from app.ai.api.rag_v2_endpoint import student_sources

router = APIRouter(prefix="/ai", tags=["AI"])

logger = logging.getLogger(__name__)

_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


@router.get("/health")
def health() -> dict[str, Any]:
    return {"ai_enabled": ai_settings.enabled}


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service = Depends(get_chat_service),
) -> ChatResponse:
    if not ai_settings.enabled:
        raise HTTPException(status_code=503, detail="AI module not enabled")
    try:
        return chat_service.chat(current_user, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in chat endpoint for user %s", current_user.id)
        raise HTTPException(status_code=500, detail="An internal error occurred while processing your request.")


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    current_user: User = Depends(get_current_user),
    chat_service = Depends(get_chat_service),
):
    conversations = chat_service.get_user_conversations(current_user.id)
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    chat_service = Depends(get_chat_service),
):
    return chat_service.get_conversation(current_user.id, conversation_id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def get_conversation_messages(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    chat_service = Depends(get_chat_service),
):
    messages = chat_service.get_messages(current_user.id, conversation_id)
    result = []
    for message in messages:
        sources = []
        if message.sources:
            import json
            try:
                sources = student_sources(json.loads(message.sources))
            except (json.JSONDecodeError, TypeError):
                sources = []
        result.append(MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            sources=sources,
            created_at=message.created_at,
        ))
    return result


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    chat_service = Depends(get_chat_service),
):
    chat_service.delete_conversation(current_user.id, conversation_id)
    return {"message": "Conversation deleted"}
