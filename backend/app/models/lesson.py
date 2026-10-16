import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text)
    duration_minutes = Column(Integer)
    order_index = Column(Integer, nullable=False, default=0)
    is_published = Column(Boolean, default=False, nullable=False)

    module = relationship("Module", back_populates="lessons")
    resources = relationship("Resource", back_populates="lesson", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="lesson", cascade="all, delete-orphan")
    recorded_video = relationship("RecordedVideo", back_populates="lesson", uselist=False, cascade="all, delete-orphan")
    live_sessions = relationship("LiveSession", back_populates="lesson", cascade="all, delete-orphan")