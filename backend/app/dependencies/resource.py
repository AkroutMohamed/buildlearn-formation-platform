from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.lesson_repository import LessonRepository
from app.repositories.resource_repository import ResourceRepository
from app.services.resource_service import ResourceService


def get_resource_service(
    db: Session = Depends(get_db),
) -> ResourceService:
    repository = ResourceRepository(db)
    return ResourceService(repository, LessonRepository(db))
