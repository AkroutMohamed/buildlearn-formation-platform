from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnswerBase(BaseModel):
    text: str = Field(..., min_length=1)
    is_correct: bool = False


class AnswerCreate(AnswerBase):
    pass


class AnswerUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)
    is_correct: Optional[bool] = None


class AnswerResponse(AnswerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question_id: UUID
