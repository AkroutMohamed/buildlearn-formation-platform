from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.lesson_repository import LessonRepository
from app.repositories.live_session_repository import LiveSessionRepository
from app.services.live_session_service import LiveSessionService


def get_live_session_service(
    db: Session = Depends(get_db),
) -> LiveSessionService:
    repository = LiveSessionRepository(db)
    return LiveSessionService(repository, LessonRepository(db))
