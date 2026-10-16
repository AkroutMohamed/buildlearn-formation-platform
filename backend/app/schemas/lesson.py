from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LessonBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order_index: int = Field(default=0, ge=0)
    is_published: bool = False


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order_index: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None


class LessonResponse(LessonBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    module_id: UUID