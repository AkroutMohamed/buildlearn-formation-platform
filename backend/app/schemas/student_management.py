from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EnrolledStudentResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    enrollment_id: UUID
    status: str
    enrolled_at: datetime


class StudentProgressResponse(BaseModel):
    student_id: UUID
    course_id: UUID
    completed_lessons: int
    total_lessons: int
    completion_percent: float
    last_updated_at: datetime | None


class QuizResultResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    quiz_title: str
    score: float
    correct_answers: int
    total_questions: int
    completed_at: datetime
