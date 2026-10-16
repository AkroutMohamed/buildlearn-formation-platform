from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.product_repository import ProductRepository
from app.services.admin_product_service import AdminProductService
from app.services.product_service import ProductService


def get_admin_product_service(
    db: Session = Depends(get_db),
) -> AdminProductService:
    repository = ProductRepository(db)
    return AdminProductService(repository)
