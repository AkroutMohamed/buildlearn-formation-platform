import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class LiveSessionStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    LIVE = "LIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class LiveSession(Base):
    __tablename__ = "live_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    meeting_url = Column(String, nullable=False)
    status = Column(Enum(LiveSessionStatus, name="live_session_status"), nullable=False, default=LiveSessionStatus.UPCOMING)
    recording_url = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    lesson = relationship("Lesson", back_populates="live_sessions")
