import enum
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CourseCategory(str, enum.Enum):
    OUTILLAGE = "Outillage"
    ETANCHEITE = "Étanchéité"
    GYPSTANT = "Gypstant"


class CourseLevel(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class CourseStatus(str, enum.Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"


class Course(Base):
    __tablename__ = "courses"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    instructor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    objectives = Column(
        Text,
        nullable=True,
    )

    thumbnail = Column(
        String(500),
        nullable=True,
    )

    language = Column(
        String(50),
        nullable=False,
        default="French",
    )

    duration = Column(
        Integer,
        nullable=False,
        default=0,
    )

    category = Column(
        Enum(CourseCategory, name="course_category"),
        nullable=False,
    )

    level = Column(
        Enum(CourseLevel, name="course_level"),
        nullable=False,
    )

    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )

    status = Column(
        Enum(CourseStatus, name="course_status"),
        nullable=False,
        default=CourseStatus.DRAFT,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    instructor = relationship(
        "User",
        back_populates="courses",
    )
    assigned_instructors = relationship(
        "CourseInstructor",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    product = relationship("Product", back_populates="courses")
    certificates = relationship("Certificate", back_populates="course", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")