from uuid import UUID

from pydantic import BaseModel, Field


class QuizAnswerSelection(BaseModel):
    question_id: UUID
    answer_id: UUID | None = None
    text_answer: str | None = Field(default=None, max_length=10000)


class QuizSubmission(BaseModel):
    answers: list[QuizAnswerSelection] = Field(default_factory=list)


class WrittenGrade(BaseModel):
    question_id: UUID
    points_awarded: float = Field(ge=0, allow_inf_nan=False)
    feedback: str = Field(default="", max_length=5000)


class QuizReview(BaseModel):
    grades: list[WrittenGrade] = Field(min_length=1)
