import os
from datetime import datetime, timezone
from uuid import UUID

os.environ["AI_ENABLED"] = "true"
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "test"
os.environ["VECTOR_STORE"] = "qdrant"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock

from app.ai.schemas.chat import ChatRequest, ChatResponse
from app.database import Base
from app.models.user import User, UserRole
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.chat_service import ChatService

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _get_test_db():
    db = SessionLocalTest()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _make_user(tag: str = "") -> User:
    db = SessionLocalTest()
    try:
        email = f"test-{tag}-{UUID(int=0)}@example.com"
        user = User(
            first_name="Test",
            last_name="User",
            email=email,
            hashed_password="hashed",
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


class TestChatService:
    def test_chat_creates_conversation_with_title(self):
        db = next(_get_test_db())
        mock_rag = MagicMock()
        mock_rag.run.return_value = ChatResponse(
            answer="Answer",
            sources=[],
            conversation_id=str(UUID(int=0)),
            created_at=datetime.now(timezone.utc),
        )

        service = ChatService(db, rag_service=mock_rag)
        user = _make_user("title")
        request = ChatRequest(question="What is Gyproc Fireline?")

        response = service.chat(user, request)

        assert response.conversation_id is not None
        conv = ConversationRepository(db).get_by_id(UUID(response.conversation_id))
        assert conv is not None
        assert "Gyproc Fireline" in conv.title

    def test_long_question_is_rejected(self):
        db = next(_get_test_db())
        mock_rag = MagicMock()
        service = ChatService(db, rag_service=mock_rag)
        user = _make_user("long")
        request = ChatRequest(question="a" * 2001)

        from fastapi import HTTPException
        with pytest.raises(HTTPException, match="too long"):
            service.chat(user, request)

    def test_history_is_built_from_messages(self):
        db = next(_get_test_db())
        mock_rag = MagicMock()
        mock_rag.run.return_value = ChatResponse(
            answer="Answer",
            sources=[],
            conversation_id=str(UUID(int=0)),
            created_at=datetime.now(timezone.utc),
        )

        service = ChatService(db, rag_service=mock_rag)
        user = _make_user("hist")
        conv = ConversationRepository(db).create(
            __import__("app.models.conversation", fromlist=["Conversation"]).Conversation(
                user_id=user.id, title="Test"
            )
        )

        msg_repo = MessageRepository(db)
        msg_repo.create(__import__("app.models.message", fromlist=["Message"]).Message(
            conversation_id=conv.id, role="user", content="First question"
        ))
        msg_repo.create(__import__("app.models.message", fromlist=["Message"]).Message(
            conversation_id=conv.id, role="assistant", content="First answer"
        ))
        db.commit()

        request = ChatRequest(question="Follow up", conversation_id=str(conv.id))
        service.chat(user, request)

        call_args = mock_rag.run.call_args
        history = call_args.kwargs.get("history")
        assert history is not None
        assert len(history) == 3
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Follow up"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "First answer"
        assert history[2]["role"] == "user"
        assert history[2]["content"] == "First question"

    def test_title_generation_short_question(self):
        db = next(_get_test_db())
        service = ChatService(db, rag_service=MagicMock())
        title = service._generate_title("BA13 Hydro")
        assert title == "BA13 Hydro"

    def test_title_generation_long_question(self):
        db = next(_get_test_db())
        service = ChatService(db, rag_service=MagicMock())
        title = service._generate_title("Explain the detailed difference between BA13 Hydro moisture resistant board and BA13 Feu fire resistant board")
        assert title.endswith("...")
        assert len(title) <= 60

    def test_title_generation_empty_question(self):
        db = next(_get_test_db())
        service = ChatService(db, rag_service=MagicMock())
        title = service._generate_title("   ")
        assert title == "New conversation"

    def test_title_generation_very_long_question(self):
        db = next(_get_test_db())
        service = ChatService(db, rag_service=MagicMock())
        title = service._generate_title("a" * 100)
        assert len(title) <= 60
        assert title.endswith("...")
