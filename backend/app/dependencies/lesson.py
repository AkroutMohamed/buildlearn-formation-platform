from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.lesson_repository import LessonRepository
from app.repositories.module_repository import ModuleRepository
from app.services.lesson_service import LessonService


def get_lesson_service(
    db: Session = Depends(get_db),
) -> LessonService:
    repository = LessonRepository(db)
    return LessonService(repository, ModuleRepository(db))
