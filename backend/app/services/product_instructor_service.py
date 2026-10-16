from fastapi import HTTPException

from app.models.product import Product
from app.models.user import InstructorStatus, UserRole
from app.repositories.product_instructor_repository import ProductInstructorRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository


class ProductInstructorService:
    def __init__(
        self,
        repository: ProductInstructorRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    def assign_instructor(self, product_id, instructor_id):
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        instructor = self.user_repository.get_by_id(instructor_id)
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")

        if instructor.role != UserRole.INSTRUCTOR:
            raise HTTPException(status_code=422, detail="User is not an instructor")

        if instructor.instructor_status != InstructorStatus.ACTIVE:
            raise HTTPException(status_code=422, detail="Instructor is not active")

        if self.repository.is_instructor_assigned(product_id, instructor_id):
            raise HTTPException(status_code=409, detail="Instructor is already assigned to this product")

        return self.repository.assign_instructor(product_id, instructor_id)

    def remove_instructor(self, product_id, instructor_id):
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        instructor = self.user_repository.get_by_id(instructor_id)
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")

        if not self.repository.is_instructor_assigned(product_id, instructor_id):
            raise HTTPException(status_code=404, detail="Instructor is not assigned to this product")

        self.repository.remove_instructor(product_id, instructor_id)
        return {"message": "Instructor removed from product"}

    def get_product_instructors(self, product_id):
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        return self.repository.get_product_instructors(product_id)

    def get_instructor_products(self, instructor_id):
        instructor = self.user_repository.get_by_id(instructor_id)
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")

        return self.repository.get_instructor_products(instructor_id)
