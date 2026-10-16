import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RecordedVideo(Base):
    __tablename__ = "recorded_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    video_url = Column(String, nullable=False)
    duration_seconds = Column(Integer)
    thumbnail_url = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    lesson = relationship("Lesson", back_populates="recorded_video")
