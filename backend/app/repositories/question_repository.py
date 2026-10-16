from uuid import UUID

from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.quiz import Quiz
from app.models.course import Course


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, question: Question) -> Question:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_by_quiz(self, quiz_id: UUID):
        return (
            self.db.query(Question)
            .filter(Question.quiz_id == quiz_id)
            .order_by(Question.id.asc())
            .all()
        )

    def get_course_for_owner(self, course_id: UUID, instructor_id: UUID):
        return (
            self.db.query(Course)
            .filter(Course.id == course_id, Course.instructor_id == instructor_id)
            .first()
        )

    def get_quiz_in_course(self, quiz_id: UUID, course_id: UUID):
        return self.db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.course_id == course_id).first()

    def get_by_id_in_quiz(self, question_id: UUID, quiz_id: UUID):
        return self.db.query(Question).filter(Question.id == question_id, Question.quiz_id == quiz_id).first()

    def update(self, question: Question, values: dict):
        for field, value in values.items():
            setattr(question, field, value)
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question: Question):
        self.db.delete(question)
        self.db.commit()
