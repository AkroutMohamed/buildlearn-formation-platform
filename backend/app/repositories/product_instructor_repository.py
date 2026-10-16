from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.product_instructor import ProductInstructor
from app.models.user import InstructorStatus, UserRole


class ProductInstructorRepository:
    def __init__(self, db: Session):
        self.db = db

    def assign_instructor(self, product_id: UUID, instructor_id: UUID) -> ProductInstructor:
        assignment = ProductInstructor(product_id=product_id, instructor_id=instructor_id)
        self.db.add(assignment)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(assignment)
        return assignment

    def remove_instructor(self, product_id: UUID, instructor_id: UUID) -> bool:
        assignment = (
            self.db.query(ProductInstructor)
            .filter(
                ProductInstructor.product_id == product_id,
                ProductInstructor.instructor_id == instructor_id,
            )
            .first()
        )
        if assignment is None:
            return False
        self.db.delete(assignment)
        self.db.commit()
        return True

    def get_product_instructors(self, product_id: UUID) -> List[ProductInstructor]:
        return (
            self.db.query(ProductInstructor)
            .filter(ProductInstructor.product_id == product_id)
            .order_by(ProductInstructor.assigned_at.desc())
            .all()
        )

    def get_instructor_products(self, instructor_id: UUID) -> List[ProductInstructor]:
        return (
            self.db.query(ProductInstructor)
            .filter(ProductInstructor.instructor_id == instructor_id)
            .order_by(ProductInstructor.assigned_at.desc())
            .all()
        )

    def is_instructor_assigned(self, product_id: UUID, instructor_id: UUID) -> bool:
        return (
            self.db.query(ProductInstructor)
            .filter(
                ProductInstructor.product_id == product_id,
                ProductInstructor.instructor_id == instructor_id,
            )
            .first()
        ) is not None
