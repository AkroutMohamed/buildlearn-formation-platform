from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.models.course import Course
from app.models.course_instructor import CourseInstructor
from app.models.quiz import Quiz
from app.models.user import User
from app.repositories.quiz_repository import QuizRepository
from app.schemas.quiz import QuizCreate, QuizUpdate


class QuizService:
    def __init__(self, repository: QuizRepository):
        self.repository = repository

    def _ensure_course_owner(self, current_user: User, course_id: UUID):
        course = self.repository.db.query(Course).filter(Course.id == course_id).first()
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == current_user.id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not assigned to this course")
        return course

    def list_quizzes(self, current_user: User, course_id: UUID) -> List[Quiz]:
        self._ensure_course_owner(current_user, course_id)
        return self.repository.get_by_course(course_id)

    def create_quiz(self, current_user: User, course_id: UUID, quiz_data: QuizCreate) -> Quiz:
        self._ensure_course_owner(current_user, course_id)
        return self.repository.create(
            Quiz(
                course_id=course_id,
                title=quiz_data.title.strip(),
                description=quiz_data.description.strip() if quiz_data.description else None,
            )
        )

    def update_quiz(self, current_user: User, course_id: UUID, quiz_id: UUID, quiz_data: QuizUpdate) -> Quiz:
        self._ensure_course_owner(current_user, course_id)
        quiz = self.repository.get_by_id_and_course(quiz_id, course_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return self.repository.update(quiz, quiz_data.model_dump(exclude_unset=True))

    def delete_quiz(self, current_user: User, course_id: UUID, quiz_id: UUID) -> None:
        self._ensure_course_owner(current_user, course_id)
        quiz = self.repository.get_by_id_and_course(quiz_id, course_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        self.repository.delete(quiz)
