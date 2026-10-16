from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.course_repository import CourseRepository
from app.repositories.product_instructor_repository import ProductInstructorRepository
from app.repositories.product_repository import ProductRepository
from app.services.instructor_product_service import InstructorProductService


def get_instructor_product_service(
    db: Session = Depends(get_db),
) -> InstructorProductService:
    product_repository = ProductRepository(db)
    product_instructor_repository = ProductInstructorRepository(db)
    course_repository = CourseRepository(db)
    return InstructorProductService(product_repository, product_instructor_repository, course_repository)
