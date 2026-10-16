from pydantic import BaseModel, Field


class CourseAnalyticsResponse(BaseModel):
    total_students: int = Field(ge=0)
    completed_students: int = Field(ge=0)
    completion_rate: float = Field(ge=0, le=100)
    average_quiz_score: float = Field(ge=0, le=100)
    total_lessons: int = Field(ge=0)
    completed_lessons: int = Field(ge=0)
    average_progress: float = Field(ge=0, le=100)
