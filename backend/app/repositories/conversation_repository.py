from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def get_by_id_and_user(self, conversation_id: UUID, user_id: UUID) -> Optional[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )

    def get_by_user(self, user_id: UUID) -> List[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    def delete(self, conversation: Conversation):
        self.db.delete(conversation)
        self.db.commit()
