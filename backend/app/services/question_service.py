from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.models.course import Course
from app.models.course_instructor import CourseInstructor
from app.models.answer import Answer
from app.models.question import Question
from app.models.user import User
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionService:
    def __init__(self, repository: QuestionRepository):
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

    def _get_quiz_or_404(self, course_id: UUID, quiz_id: UUID):
        quiz = self.repository.get_quiz_in_course(quiz_id, course_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return quiz

    def list_questions(self, current_user: User, course_id: UUID, quiz_id: UUID) -> List[Question]:
        self._ensure_course_owner(current_user, course_id)
        self._get_quiz_or_404(course_id, quiz_id)
        return self.repository.get_by_quiz(quiz_id)

    def create_question(self, current_user: User, course_id: UUID, quiz_id: UUID, question_data: QuestionCreate) -> Question:
        self._ensure_course_owner(current_user, course_id)
        self._get_quiz_or_404(course_id, quiz_id)
        question = Question(
            quiz_id=quiz_id,
            text=question_data.text.strip(),
            question_type=question_data.question_type,
            points=question_data.points,
            order_index=question_data.order_index,
        )
        if question.question_type == "yes_no":
            question.answers = [Answer(text="Yes", is_correct=question_data.correct_yes), Answer(text="No", is_correct=not question_data.correct_yes)]
        return self.repository.create(question)

    def update_question(self, current_user: User, course_id: UUID, quiz_id: UUID, question_id: UUID, question_data: QuestionUpdate) -> Question:
        self._ensure_course_owner(current_user, course_id)
        self._get_quiz_or_404(course_id, quiz_id)
        question = self.repository.get_by_id_in_quiz(question_id, quiz_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        if question_data.question_type is not None and question_data.question_type != question.question_type:
            raise HTTPException(status_code=422, detail="Create a new question to change its type")
        return self.repository.update(question, question_data.model_dump(exclude_unset=True))

    def delete_question(self, current_user: User, course_id: UUID, quiz_id: UUID, question_id: UUID) -> None:
        self._ensure_course_owner(current_user, course_id)
        self._get_quiz_or_404(course_id, quiz_id)
        question = self.repository.get_by_id_in_quiz(question_id, quiz_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        self.repository.delete(question)
