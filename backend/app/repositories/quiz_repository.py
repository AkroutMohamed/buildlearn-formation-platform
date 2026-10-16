from uuid import UUID

from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.course import Course


class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, quiz: Quiz) -> Quiz:
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def get_by_course(self, course_id: UUID):
        return self.db.query(Quiz).filter(Quiz.course_id == course_id).all()

    def get_course_for_owner(self, course_id: UUID, instructor_id: UUID):
        return (
            self.db.query(Course)
            .filter(Course.id == course_id, Course.instructor_id == instructor_id)
            .first()
        )

    def get_by_id_and_course(self, quiz_id: UUID, course_id: UUID):
        return self.db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.course_id == course_id).first()

    def update(self, quiz: Quiz, values: dict):
        for field, value in values.items():
            setattr(quiz, field, value)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete(self, quiz: Quiz):
        self.db.delete(quiz)
        self.db.commit()
