from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class QuizBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None


class QuizCreate(QuizBase):
    pass


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None


class QuizResponse(QuizBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: UUID