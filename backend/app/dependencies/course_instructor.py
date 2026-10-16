from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.course_instructor_repository import CourseInstructorRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import UserRepository
from app.services.course_instructor_service import CourseInstructorService


def get_course_instructor_service(
    db: Session = Depends(get_db),
) -> CourseInstructorService:
    course_repository = CourseRepository(db)
    user_repository = UserRepository(db)
    repository = CourseInstructorRepository(db)
    return CourseInstructorService(repository, course_repository, user_repository)
