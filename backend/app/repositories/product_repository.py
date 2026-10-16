from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.product import Product, ProductStatus


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: UUID) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_all(self) -> List[Product]:
        return (
            self.db.query(Product)
            .order_by(Product.created_at.desc())
            .all()
        )

    def get_by_instructor(self, instructor_id: UUID) -> List[Product]:
        return (
            self.db.query(Product)
            .join(Product.assigned_instructors)
            .filter(Product.assigned_instructors.any(instructor_id=instructor_id))
            .order_by(Product.created_at.desc())
            .all()
        )

    def update(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product):
        self.db.delete(product)
        self.db.commit()
