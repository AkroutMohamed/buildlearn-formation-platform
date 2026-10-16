from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.models.course import Course, CourseStatus
from app.models.course_instructor import CourseInstructor
from app.models.product import Product
from app.models.product_instructor import ProductInstructor
from app.models.user import User
from app.repositories.course_instructor_repository import CourseInstructorRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.product_instructor_repository import ProductInstructorRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.course import CourseCreate, CourseResponse
from app.schemas.product import ProductResponse


class InstructorProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        product_instructor_repository: ProductInstructorRepository,
        course_repository: CourseRepository,
    ):
        self.product_repository = product_repository
        self.product_instructor_repository = product_instructor_repository
        self.course_repository = course_repository

    def _ensure_assigned(self, product_id: UUID, current_user: User):
        assignment = self.product_instructor_repository.is_instructor_assigned(product_id, current_user.id)
        if not assignment:
            raise HTTPException(status_code=403, detail="You are not assigned to this product")

    def get_assigned_products(self, current_user: User) -> List[Product]:
        return self.product_repository.get_by_instructor(current_user.id)

    def get_product(self, current_user: User, product_id: UUID) -> Product:
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        self._ensure_assigned(product_id, current_user)
        return product

    def create_course_in_product(self, current_user: User, product_id: UUID, course_data: CourseCreate) -> Course:
        product = self.get_product(current_user, product_id)

        if len(course_data.title.strip()) < 3:
            raise HTTPException(status_code=422, detail="Course title must contain at least 3 characters.")

        if len(course_data.description.strip()) < 10:
            raise HTTPException(status_code=422, detail="Course description must contain at least 10 characters.")

        if course_data.duration < 0:
            raise HTTPException(status_code=422, detail="Duration cannot be negative.")

        course = Course(
            instructor_id=current_user.id,
            product_id=product_id,
            title=course_data.title.strip(),
            description=course_data.description.strip(),
            objectives=course_data.objectives,
            thumbnail=course_data.thumbnail,
            language=course_data.language,
            duration=course_data.duration,
            category=course_data.category,
            level=course_data.level,
            status=CourseStatus.DRAFT,
        )
        created_course = self.course_repository.create(course)

        course_instructor_repo = CourseInstructorRepository(self.course_repository.db)
        course_instructor_repo.assign_instructor(created_course.id, current_user.id)

        return created_course
