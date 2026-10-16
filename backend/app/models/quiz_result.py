import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class QuizResult(Base):
    """A student's completed attempt for a quiz."""

    __tablename__ = "quiz_results"
    __table_args__ = (UniqueConstraint("student_id", "quiz_id", name="uq_quiz_result_student_quiz"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    correct_answers = Column(Integer, nullable=False, default=0)
    total_questions = Column(Integer, nullable=False, default=0)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
