from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.product_instructor_repository import ProductInstructorRepository
from app.repositories.product_repository import ProductRepository
from app.services.product_instructor_service import ProductInstructorService
from app.services.product_service import ProductService


def get_product_service(
    db: Session = Depends(get_db),
) -> ProductService:
    repository = ProductRepository(db)
    return ProductService(repository)


def get_product_instructor_service(
    db: Session = Depends(get_db),
) -> ProductInstructorService:
    repository = ProductInstructorRepository(db)
    product_repository = ProductRepository(db)
    user_repository = __import__("app.repositories.user_repository", fromlist=["UserRepository"]).UserRepository(db)
    return ProductInstructorService(repository, product_repository, user_repository)
