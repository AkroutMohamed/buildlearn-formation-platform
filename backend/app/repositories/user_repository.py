from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import InstructorStatus, User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_ids(self, user_ids: List[UUID]) -> List[User]:
        return self.db.query(User).filter(User.id.in_(user_ids)).all()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_role(self, role: UserRole) -> List[User]:
        return self.db.query(User).filter(User.role == role).order_by(User.created_at.desc()).all()

    def get_instructors(self) -> List[User]:
        return self.db.query(User).filter(User.role == UserRole.INSTRUCTOR).order_by(User.id.desc()).all()

    def get_pending_instructors(self) -> List[User]:
        return (
            self.db.query(User)
            .filter(User.role == UserRole.INSTRUCTOR, User.instructor_status == InstructorStatus.PENDING)
            .order_by(User.id.desc())
            .all()
        )

    def update_instructor_status(self, user_id: UUID, instructor_status: InstructorStatus) -> Optional[User]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None
        user.instructor_status = instructor_status
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_instructor(self, first_name: str, last_name: str, email: str, hashed_password: str) -> User:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hashed_password,
            role=UserRole.INSTRUCTOR,
            instructor_status=InstructorStatus.ACTIVE,
        )
        return self.create(user)