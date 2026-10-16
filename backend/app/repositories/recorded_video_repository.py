from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.recorded_video import RecordedVideo


class RecordedVideoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, video: RecordedVideo) -> RecordedVideo:
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def get_by_lesson(self, lesson_id: UUID) -> Optional[RecordedVideo]:
        return (
            self.db.query(RecordedVideo)
            .filter(RecordedVideo.lesson_id == lesson_id)
            .first()
        )

    def get_by_id(self, video_id: UUID) -> Optional[RecordedVideo]:
        return self.db.query(RecordedVideo).filter(RecordedVideo.id == video_id).first()

    def update(self, video: RecordedVideo, values: dict) -> RecordedVideo:
        for field, value in values.items():
            setattr(video, field, value)
        self.db.commit()
        self.db.refresh(video)
        return video

    def delete(self, video: RecordedVideo) -> None:
        self.db.delete(video)
        self.db.commit()
