from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.progress import Progress
from app.models.quiz_result import QuizResult


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_course_with_enrollments(self, course_id: UUID):
        return (
            self.db.query(Course)
            .options(selectinload(Course.enrollments).selectinload(Enrollment.progress))
            .filter(Course.id == course_id)
            .first()
        )

    def count_course_lessons(self, course_id: UUID):
        return (
            self.db.query(Lesson)
            .join(Module, Lesson.module_id == Module.id)
            .filter(Module.course_id == course_id)
            .count()
        )

    def average_quiz_score(self, course_id: UUID):
        return (
            self.db.query(func.avg(QuizResult.score))
            .filter(QuizResult.course_id == course_id)
            .scalar()
        )
