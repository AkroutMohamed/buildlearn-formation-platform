import uuid

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductInstructor(Base):
    __tablename__ = "product_instructors"

    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
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

    product = relationship("Product", back_populates="assigned_instructors")
    instructor = relationship("User", back_populates="assigned_products")
