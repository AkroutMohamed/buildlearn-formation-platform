from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.course_repository import CourseRepository
from app.repositories.module_repository import ModuleRepository
from app.services.course_service import CourseService


def get_course_service(
    db: Session = Depends(get_db),
) -> CourseService:
    """
    Dependency that provides a CourseService instance.
    """

    repository = CourseRepository(db)

    return CourseService(repository, ModuleRepository(db))
