from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class QuestionBase(BaseModel):
    text: str = Field(..., min_length=1)
    question_type: Literal["multiple_choice", "yes_no", "written"] = "multiple_choice"
    points: int = Field(default=1, ge=0)
    order_index: int = Field(default=0, ge=0)


class QuestionCreate(QuestionBase):
    correct_yes: bool = True


class QuestionUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[Literal["multiple_choice", "yes_no", "written"]] = None
    points: Optional[int] = Field(None, ge=0)
    order_index: Optional[int] = Field(None, ge=0)


class QuestionResponse(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    quiz_id: UUID
