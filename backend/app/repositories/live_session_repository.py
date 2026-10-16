from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.live_session import LiveSession, LiveSessionStatus


class LiveSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session: LiveSession) -> LiveSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_lesson(self, lesson_id: UUID) -> List[LiveSession]:
        return (
            self.db.query(LiveSession)
            .filter(LiveSession.lesson_id == lesson_id)
            .order_by(LiveSession.scheduled_start.asc())
            .all()
        )

    def get_by_id(self, session_id: UUID) -> Optional[LiveSession]:
        return self.db.query(LiveSession).filter(LiveSession.id == session_id).first()

    def update(self, session: LiveSession, values: dict) -> LiveSession:
        for field, value in values.items():
            setattr(session, field, value)
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, session: LiveSession) -> None:
        self.db.delete(session)
        self.db.commit()
