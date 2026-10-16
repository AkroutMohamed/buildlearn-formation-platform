from uuid import UUID

from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.course import Course
from app.models.question import Question
from app.models.quiz import Quiz


class AnswerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, answer: Answer) -> Answer:
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def get_by_question(self, question_id: UUID):
        return (
            self.db.query(Answer)
            .filter(Answer.question_id == question_id)
            .order_by(Answer.id.asc())
            .all()
        )

    def get_course_for_owner(self, course_id: UUID, instructor_id: UUID):
        return (
            self.db.query(Course)
            .filter(Course.id == course_id, Course.instructor_id == instructor_id)
            .first()
        )

    def get_question_in_quiz(self, question_id: UUID, quiz_id: UUID, course_id: UUID):
        return (
            self.db.query(Question)
            .join(Quiz, Question.quiz_id == Quiz.id)
            .filter(Question.id == question_id, Quiz.id == quiz_id, Quiz.course_id == course_id)
            .first()
        )

    def get_by_id_in_question(self, answer_id: UUID, question_id: UUID):
        return self.db.query(Answer).filter(Answer.id == answer_id, Answer.question_id == question_id).first()

    def update(self, answer: Answer, values: dict):
        for field, value in values.items():
            setattr(answer, field, value)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def delete(self, answer: Answer):
        self.db.delete(answer)
        self.db.commit()
