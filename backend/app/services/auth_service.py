from fastapi import HTTPException

from app.models.user import User, InstructorStatus
from app.repositories.user_repository import UserRepository
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_access_token


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def login_user(self, login_data):
        user = self.repository.get_by_email(login_data["email"])

        if not user or not verify_password(login_data["password"], user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({
            "sub": user.email,
            "role": user.role.value,
        })

        return {
            "access_token": token,
            "token_type": "bearer",
        }

    def register_user(self, user):
        existing_user = self.repository.get_by_email(user.email)

        if existing_user:
            raise HTTPException(status_code=409, detail="Email already exists")

        hashed_password_value = hash_password(user.password)

        role = user.role
        instructor_status = InstructorStatus.ACTIVE if role != "instructor" else InstructorStatus.PENDING

        new_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=hashed_password_value,
            role=role,
            instructor_status=instructor_status,
        )

        return self.repository.create(new_user)
