from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.message import Message


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, message: Message) -> Message:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_conversation_id(self, conversation_id: UUID) -> List[Message]:
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def create_many(self, messages: List[Message]) -> List[Message]:
        self.db.add_all(messages)
        self.db.commit()
        for message in messages:
            self.db.refresh(message)
        return messages
