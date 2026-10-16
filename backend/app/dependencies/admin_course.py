from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.course_instructor_repository import CourseInstructorRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import UserRepository
from app.services.admin_course_service import AdminCourseService


def get_admin_course_service(
    db: Session = Depends(get_db),
) -> AdminCourseService:
    course_repository = CourseRepository(db)
    course_instructor_repository = CourseInstructorRepository(db)
    user_repository = UserRepository(db)
    return AdminCourseService(course_repository, course_instructor_repository, user_repository)
