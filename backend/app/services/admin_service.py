from fastapi import HTTPException

from app.models.user import InstructorStatus, UserRole
from app.repositories.user_repository import UserRepository


class AdminService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def list_pending_instructors(self):
        return self.repository.get_pending_instructors()

    def list_instructors(self):
        return self.repository.get_instructors()

    def approve_instructor(self, user_id):
        user = self.repository.update_instructor_status(user_id, InstructorStatus.ACTIVE)
        if user is None:
            raise HTTPException(status_code=404, detail="Instructor not found")
        return user

    def reject_instructor(self, user_id):
        user = self.repository.update_instructor_status(user_id, InstructorStatus.REJECTED)
        if user is None:
            raise HTTPException(status_code=404, detail="Instructor not found")
        return user

    def create_instructor(self, first_name, last_name, email, password):
        existing = self.repository.get_by_email(email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already exists")
        from app.utils.hash import hash_password
        return self.repository.create_instructor(first_name, last_name, email, hash_password(password))
