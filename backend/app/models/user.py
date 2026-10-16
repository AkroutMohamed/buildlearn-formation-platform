import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class InstructorStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        nullable=False,
    )

    hashed_password = Column(String, nullable=False)

    role = Column(
        Enum(UserRole),
        default=UserRole.STUDENT,
        nullable=False,
    )

    is_active = Column(Boolean, default=True, nullable=False)

    instructor_status = Column(
        Enum(InstructorStatus),
        default=InstructorStatus.ACTIVE,
        nullable=False,
    )

    courses = relationship(
        "Course",
        back_populates="instructor",
        cascade="all, delete-orphan",
    )

    assigned_courses = relationship(
        "CourseInstructor",
        back_populates="instructor",
        cascade="all, delete-orphan",
    )

    assigned_products = relationship(
        "ProductInstructor",
        back_populates="instructor",
        cascade="all, delete-orphan",
    )

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")