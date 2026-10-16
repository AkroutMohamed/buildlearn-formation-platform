import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CourseInstructor(Base):
    __tablename__ = "course_instructors"

    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )

    instructor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    course = relationship("Course", back_populates="assigned_instructors")
    instructor = relationship("User", back_populates="assigned_courses")
