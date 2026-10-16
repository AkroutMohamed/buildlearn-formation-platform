from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.course_instructor import CourseInstructor
from app.models.user import InstructorStatus, UserRole


class CourseInstructorRepository:
    def __init__(self, db: Session):
        self.db = db

    def assign_instructor(self, course_id: UUID, instructor_id: UUID) -> CourseInstructor:
        assignment = CourseInstructor(course_id=course_id, instructor_id=instructor_id)
        self.db.add(assignment)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(assignment)
        return assignment

    def remove_instructor(self, course_id: UUID, instructor_id: UUID) -> bool:
        assignment = (
            self.db.query(CourseInstructor)
            .filter(
                CourseInstructor.course_id == course_id,
                CourseInstructor.instructor_id == instructor_id,
            )
            .first()
        )
        if assignment is None:
            return False
        self.db.delete(assignment)
        self.db.commit()
        return True

    def get_course_instructors(self, course_id: UUID) -> List[CourseInstructor]:
        return (
            self.db.query(CourseInstructor)
            .filter(CourseInstructor.course_id == course_id)
            .order_by(CourseInstructor.assigned_at.desc())
            .all()
        )

    def get_instructor_courses(self, instructor_id: UUID) -> List[CourseInstructor]:
        return (
            self.db.query(CourseInstructor)
            .filter(CourseInstructor.instructor_id == instructor_id)
            .order_by(CourseInstructor.assigned_at.desc())
            .all()
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
