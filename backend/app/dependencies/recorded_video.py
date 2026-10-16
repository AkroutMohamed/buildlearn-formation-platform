from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.lesson_repository import LessonRepository
from app.repositories.recorded_video_repository import RecordedVideoRepository
from app.services.recorded_video_service import RecordedVideoService


def get_recorded_video_service(
    db: Session = Depends(get_db),
) -> RecordedVideoService:
    repository = RecordedVideoRepository(db)
    return RecordedVideoService(repository, LessonRepository(db))
