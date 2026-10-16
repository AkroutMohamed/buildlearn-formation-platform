import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductStatus(str, enum.Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"


class Product(Base):
    __tablename__ = "products"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    category = Column(
        String(100),
        nullable=True,
    )

    status = Column(
        Enum(ProductStatus, name="product_status"),
        nullable=False,
        default=ProductStatus.DRAFT,
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

    courses = relationship("Course", back_populates="product")
    assigned_instructors = relationship(
        "ProductInstructor",
        back_populates="product",
        cascade="all, delete-orphan",
    )
