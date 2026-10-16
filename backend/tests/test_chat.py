import os
import sys
from datetime import datetime, timezone
from uuid import UUID

os.environ["AI_ENABLED"] = "true"

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock

from app.main import app
from app.ai.schemas.chat import ChatRequest, ChatResponse
from app.database import Base, get_db
from app.dependencies.chat import get_chat_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import User, UserRole
from app.services.chat_service import ChatService
from app.utils.jwt import create_access_token
from app.ai.config import ai_settings

# `ai_settings` is a module-level singleton built from env vars at first import.
# Because `tests/ai/*` modules are collected before this file, another module may
# have frozen `ai_settings.enabled` to its default (False) during collection.
# Force it here so the chat tests are independent of collection order.
ai_settings.enabled = True

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_active_session = None


def _setup_db():
    global _active_session
    Base.metadata.create_all(bind=engine)
    db = SessionLocalTest()
    try:
        db.query(User).delete()
        db.commit()
    finally:
        _active_session = db


def _teardown_db():
    global _active_session
    if _active_session:
        _active_session.close()
        _active_session = None
    Base.metadata.drop_all(bind=engine)


def _create_user(tag: str = "") -> tuple[User, str]:
    email = f"test-{tag}-{UUID(int=0)}@example.com"
    while _active_session.query(User).filter(User.email == email).first():
        email = f"test-{tag}-{UUID(int=1)}@example.com"
    user = User(
        first_name="Test",
        last_name="User",
        email=email,
        hashed_password="hashed",
        role=UserRole.STUDENT if tag == "stu" else UserRole.INSTRUCTOR,
        is_active=True,
    )
    _active_session.add(user)
    _active_session.commit()
    _active_session.refresh(user)
    return user, email


def _get_token(email: str, role: str) -> str:
    return create_access_token({"sub": email, "role": role})


def _fake_current_user(request: Request):
    email = request.headers.get("x-test-user")
    assert email, "missing x-test-user header"
    user = _active_session.query(User).filter(User.email == email).first()
    assert user is not None, f"no test user for {email}"
    return user


def _mock_rag_service(conversation_id: str | None = None):
    mock_rag = MagicMock()
    mock_rag.run.return_value = ChatResponse(
        answer="This is a mocked RAG answer.",
        sources=[{"product_name": "BA13 Hydro", "score": 0.95}],
        conversation_id=conversation_id or str(UUID(int=0)),
        created_at=datetime.now(timezone.utc),
    )
    return mock_rag


def _get_test_db():
    db = SessionLocalTest()
    try:
        yield db
    finally:
        db.close()


def _make_chat_service_with_mock(mock_rag):
    def _factory():
        db = next(_get_test_db())
        return ChatService(db, rag_service=mock_rag)
    return _factory


class TestChatAPI:
    def setup_method(self):
        _setup_db()
        app.dependency_overrides[get_db] = _get_test_db
        app.dependency_overrides[get_current_user] = _fake_current_user
        app.dependency_overrides[get_chat_service] = _make_chat_service_with_mock(_mock_rag_service())
        self.client = TestClient(app)

        self.student, student_email = _create_user("stu")
        self.instructor, instructor_email = _create_user("inst")

        self.student_token = _get_token(student_email, self.student.role.value)
        self.instructor_token = _get_token(instructor_email, self.instructor.role.value)

    def teardown_method(self):
        app.dependency_overrides.clear()
        _teardown_db()

    def test_unauthenticated_chat_rejected(self):
        app.dependency_overrides.pop(get_current_user, None)
        r = self.client.post("/ai/chat", json={"question": "What is BA13 Hydro?"})
        assert r.status_code == 401

    def test_unauthenticated_list_conversations_rejected(self):
        app.dependency_overrides.pop(get_current_user, None)
        r = self.client.get("/ai/conversations")
        assert r.status_code == 401

    def test_chat_creates_conversation(self):
        r = self.client.post("/ai/chat", json={"question": "What is BA13 Hydro?"}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 200, r.text
        data = r.json()
        assert "conversation_id" in data
        assert "answer" in data

    def test_chat_saves_user_and_assistant_messages(self):
        r = self.client.post("/ai/chat", json={"question": "What is BA13 Hydro?"}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 200
        conv_id = r.json()["conversation_id"]

        r = self.client.get(f"/ai/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 200
        messages = r.json()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "What is BA13 Hydro?"
        assert messages[1]["role"] == "assistant"
        assert len(messages[1]["content"]) > 0

    def test_chat_reuses_existing_conversation(self):
        r1 = self.client.post("/ai/chat", json={"question": "First question"}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r1.status_code == 200
        conv_id = r1.json()["conversation_id"]

        r2 = self.client.post("/ai/chat", json={"question": "Second question", "conversation_id": conv_id}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r2.status_code == 200
        assert r2.json()["conversation_id"] == conv_id

        r3 = self.client.get(f"/ai/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r3.status_code == 200
        messages = r3.json()
        assert len(messages) == 4

    def test_list_user_conversations(self):
        r1 = self.client.post("/ai/chat", json={"question": "Q1"}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        r2 = self.client.post("/ai/chat", json={"question": "Q2"}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r1.status_code == 200
        assert r2.status_code == 200

        r = self.client.get("/ai/conversations", headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2

    def test_cannot_access_others_conversation(self):
        r = self.client.post("/ai/chat", json={"question": "secret question"}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 200
        conv_id = r.json()["conversation_id"]

        r = self.client.get(f"/ai/conversations/{conv_id}", headers={"Authorization": f"Bearer {self.instructor_token}", "x-test-user": self.instructor.email})
        assert r.status_code == 404

        r = self.client.get(f"/ai/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {self.instructor_token}", "x-test-user": self.instructor.email})
        assert r.status_code == 404

        r = self.client.delete(f"/ai/conversations/{conv_id}", headers={"Authorization": f"Bearer {self.instructor_token}", "x-test-user": self.instructor.email})
        assert r.status_code == 404

    def test_delete_own_conversation(self):
        r = self.client.post("/ai/chat", json={"question": "to be deleted"}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 200
        conv_id = r.json()["conversation_id"]

        r = self.client.delete(f"/ai/conversations/{conv_id}", headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 200

        r = self.client.get(f"/ai/conversations/{conv_id}", headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 404

    def test_invalid_conversation_id_format(self):
        r = self.client.post("/ai/chat", json={"question": "Q", "conversation_id": "not-a-uuid"}, headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 422

    def test_get_nonexistent_conversation(self):
        fake_id = str(UUID(int=12345))
        r = self.client.get(f"/ai/conversations/{fake_id}", headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email})
        assert r.status_code == 404

    def test_unexpected_error_returns_generic_500(self):
        class _BoomService:
            def chat(self, user, request):
                raise Exception("secret internal db host=10.0.0.5 credentials leaked")

        app.dependency_overrides[get_chat_service] = lambda: _BoomService()
        r = self.client.post(
            "/ai/chat",
            json={"question": "What is BA13 Hydro?"},
            headers={"Authorization": f"Bearer {self.student_token}", "x-test-user": self.student.email},
        )
        assert r.status_code == 500
        assert "secret" not in r.text
        assert "10.0.0.5" not in r.text
