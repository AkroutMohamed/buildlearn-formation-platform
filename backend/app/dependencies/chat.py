from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.chat_service import ChatService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.ai.api.rag_v2_endpoint import rag_v2_enabled, get_rag_v2_service


def get_chat_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatService:
    if rag_v2_enabled() and getattr(current_user.role, "value", current_user.role) == "student":
        return ChatService(db, rag_service=get_rag_v2_service())
    from app.ai.api.routes import get_rag_service
    return ChatService(db, rag_service=get_rag_service())
