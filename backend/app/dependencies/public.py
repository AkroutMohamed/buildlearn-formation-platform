from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.course_repository import CourseRepository
from app.services.public_service import PublicService


def get_public_service(
    db: Session = Depends(get_db),
) -> PublicService:
    repository = CourseRepository(db)
    return PublicService(repository)
