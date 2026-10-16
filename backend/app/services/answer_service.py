from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.models.answer import Answer
from app.models.course import Course
from app.models.course_instructor import CourseInstructor
from app.models.user import User
from app.repositories.answer_repository import AnswerRepository
from app.schemas.answer import AnswerCreate, AnswerUpdate


class AnswerService:
    def __init__(self, repository: AnswerRepository):
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

    def _get_question_or_404(self, course_id: UUID, quiz_id: UUID, question_id: UUID):
        question = self.repository.get_question_in_quiz(question_id, quiz_id, course_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question

    def list_answers(self, current_user: User, course_id: UUID, quiz_id: UUID, question_id: UUID) -> List[Answer]:
        self._ensure_course_owner(current_user, course_id)
        question = self._get_question_or_404(course_id, quiz_id, question_id)
        return self.repository.get_by_question(question.id)

    def create_answer(self, current_user: User, course_id: UUID, quiz_id: UUID, question_id: UUID, answer_data: AnswerCreate) -> Answer:
        self._ensure_course_owner(current_user, course_id)
        question = self._get_question_or_404(course_id, quiz_id, question_id)
        if question.question_type != "multiple_choice":
            raise HTTPException(status_code=422, detail="Only multiple-choice questions have editable answer options")
        answer = Answer(
            question_id=question_id,
            text=answer_data.text.strip(),
            is_correct=answer_data.is_correct,
        )
        return self.repository.create(answer)

    def update_answer(self, current_user: User, course_id: UUID, quiz_id: UUID, question_id: UUID, answer_id: UUID, answer_data: AnswerUpdate) -> Answer:
        self._ensure_course_owner(current_user, course_id)
        question = self._get_question_or_404(course_id, quiz_id, question_id)
        if question.question_type != "multiple_choice":
            raise HTTPException(status_code=422, detail="Only multiple-choice questions have editable answer options")
        answer = self.repository.get_by_id_in_question(answer_id, question_id)
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found")
        return self.repository.update(answer, answer_data.model_dump(exclude_unset=True))

    def delete_answer(self, current_user: User, course_id: UUID, quiz_id: UUID, question_id: UUID, answer_id: UUID) -> None:
        self._ensure_course_owner(current_user, course_id)
        question = self._get_question_or_404(course_id, quiz_id, question_id)
        if question.question_type != "multiple_choice":
            raise HTTPException(status_code=422, detail="Only multiple-choice questions have editable answer options")
        answer = self.repository.get_by_id_in_question(answer_id, question_id)
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found")
        self.repository.delete(answer)
