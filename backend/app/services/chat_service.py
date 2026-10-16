import logging
import re
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from app.ai.rag.rag_service import RAGService
from app.ai.schemas.chat import ChatRequest, ChatResponse
from app.ai.api.rag_v2_endpoint import stored_sources
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 2000
MAX_HISTORY_TURNS = 6


class ChatService:
    def __init__(self, db, rag_service: RAGService | None = None) -> None:
        self.db = db
        self._conversation_repo = ConversationRepository(db)
        self._message_repo = MessageRepository(db)
        self._rag_service = rag_service or RAGService()

    def chat(self, user: User, request: ChatRequest) -> ChatResponse:
        question = request.question.strip()
        if len(question) > MAX_QUESTION_LENGTH:
            raise HTTPException(status_code=400, detail="Question is too long. Please keep it under 2000 characters.")

        conversation = self._load_or_create_conversation(
            user.id, request.conversation_id, question
        )

        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=question,
        )
        self.db.add(user_message)
        self.db.commit()

        history = self._build_history(conversation.id)

        try:
            rag_request = ChatRequest(
                question=question,
                conversation_id=str(conversation.id),
                top_k=request.top_k,
                messages=request.messages,
            )
            rag_response = self._rag_service.run(rag_request, history=history)
        except Exception:
            logger.exception("RAGService failed for user %s conversation %s", user.id, conversation.id)
            raise

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=rag_response.answer,
            sources=stored_sources(rag_response),
        )
        self.db.add(assistant_message)

        conversation.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        return ChatResponse(
            answer=rag_response.answer,
            sources=rag_response.sources,
            conversation_id=str(conversation.id),
            created_at=rag_response.created_at,
        )

    def get_user_conversations(self, user_id: UUID):
        return self._conversation_repo.get_by_user(user_id)

    def get_conversation(self, user_id: UUID, conversation_id: UUID):
        conversation = self._conversation_repo.get_by_id_and_user(conversation_id, user_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation

    def get_messages(self, user_id: UUID, conversation_id: UUID):
        conversation = self._conversation_repo.get_by_id_and_user(conversation_id, user_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return self._message_repo.get_by_conversation_id(conversation_id)

    def delete_conversation(self, user_id: UUID, conversation_id: UUID):
        conversation = self._conversation_repo.get_by_id_and_user(conversation_id, user_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        self._conversation_repo.delete(conversation)

    def _load_or_create_conversation(self, user_id: UUID, conversation_id: str | None, first_question: str):
        if conversation_id:
            try:
                conv_uuid = UUID(conversation_id)
            except ValueError:
                raise HTTPException(status_code=422, detail="Invalid conversation_id")
            conversation = self._conversation_repo.get_by_id_and_user(conv_uuid, user_id)
            if conversation is None:
                raise HTTPException(status_code=404, detail="Conversation not found")
            return conversation

        title = self._generate_title(first_question)
        conversation = self._conversation_repo.create(
            Conversation(
                user_id=user_id,
                title=title,
            )
        )
        return conversation

    def _build_history(self, conversation_id: UUID) -> list[dict[str, str]]:
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(MAX_HISTORY_TURNS * 2)
            .all()
        )
        messages = list(reversed(messages))
        return [{"role": m.role, "content": m.content} for m in messages]

    @staticmethod
    def _generate_title(question: str) -> str:
        cleaned = question.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if len(cleaned) > 60:
            cleaned = cleaned[:57].rstrip() + "..."
        return cleaned or "New conversation"
