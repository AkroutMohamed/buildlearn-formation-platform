from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    repository = UserRepository(db)
    return AuthService(repository)
