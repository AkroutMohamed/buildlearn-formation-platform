from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.admin_service import AdminService


def get_admin_service(
    db: Session = Depends(get_db),
) -> AdminService:
    repository = UserRepository(db)
    return AdminService(repository)
