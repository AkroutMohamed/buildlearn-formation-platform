from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.course import Course, CourseStatus
from app.models.course_instructor import CourseInstructor
from app.models.lesson import Lesson
from app.models.module import Module


class CourseRepository:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Create
    # -------------------------
    def create(self, course: Course) -> Course:
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    # -------------------------
    # Get by ID
    # -------------------------
    def get_by_id(self, course_id: UUID) -> Optional[Course]:
        return (
            self.db.query(Course)
            .filter(Course.id == course_id)
            .first()
        )

    def get_by_id_with_modules_and_lessons(self, course_id: UUID) -> Optional[Course]:
        return (
            self.db.query(Course)
            .options(selectinload(Course.modules).selectinload(Module.lessons))
            .filter(Course.id == course_id)
            .first()
        )

    # -------------------------
    # Get all
    # -------------------------
    def get_all(self) -> List[Course]:
        return (
            self.db.query(Course)
            .order_by(Course.created_at.desc())
            .all()
        )

    # -------------------------
    # Get instructor courses
    # -------------------------
    def get_by_instructor(
        self,
        instructor_id: UUID
    ) -> List[Course]:

        return (
            self.db.query(Course)
            .filter(Course.instructor_id == instructor_id)
            .order_by(Course.created_at.desc())
            .all()
        )

    def get_assigned_instructor_courses(self, instructor_id: UUID) -> List[Course]:
        return (
            self.db.query(Course)
            .options(joinedload(Course.product))
            .join(CourseInstructor, Course.id == CourseInstructor.course_id)
            .filter(CourseInstructor.instructor_id == instructor_id)
            .order_by(Course.created_at.desc())
            .all()
        )

    def get_by_product(self, product_id: UUID) -> List[Course]:
        return (
            self.db.query(Course)
            .filter(Course.product_id == product_id)
            .order_by(Course.created_at.desc())
            .all()
        )

    def get_published_courses_page(self, page: int, limit: int, search=None, category=None, level=None, language=None):
        query = (
            self.db.query(Course)
            .options(joinedload(Course.instructor))
            .filter(Course.status == CourseStatus.PUBLISHED)
            .order_by(Course.created_at.desc())
        )
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(Course.title.ilike(pattern) | Course.description.ilike(pattern))
        if category:
            query = query.filter(Course.category == category)
        if level:
            query = query.filter(Course.level == level)
        if language:
            query = query.filter(Course.language.ilike(language.strip()))
        total = query.count()
        courses = query.offset((page - 1) * limit).limit(limit).all()
        return courses, total

    def get_published_course_by_id(self, course_id: UUID):
        return (
            self.db.query(Course)
            .options(
                joinedload(Course.instructor),
                selectinload(Course.modules).selectinload(Module.lessons),
                selectinload(Course.quizzes),
            )
            .filter(Course.id == course_id, Course.status == CourseStatus.PUBLISHED)
            .first()
        )

    def is_instructor_assigned(self, course_id: UUID, instructor_id: UUID) -> bool:
        return (
            self.db.query(CourseInstructor)
            .filter(
                CourseInstructor.course_id == course_id,
                CourseInstructor.instructor_id == instructor_id,
            )
            .first()
        ) is not None

    # -------------------------
    # Update
    # -------------------------
    def update(self, course: Course) -> Course:
        self.db.commit()
        self.db.refresh(course)
        return course

    # -------------------------
    # Delete
    # -------------------------
    def delete(self, course: Course):
        self.db.delete(course)
        self.db.commit()
