from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecordedVideoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    video_url: str = Field(..., min_length=1)
    duration_seconds: Optional[int] = Field(None, ge=0)
    thumbnail_url: Optional[str] = None


class RecordedVideoCreate(RecordedVideoBase):
    pass


class RecordedVideoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    video_url: Optional[str] = Field(None, min_length=1)
    duration_seconds: Optional[int] = Field(None, ge=0)
    thumbnail_url: Optional[str] = None


class RecordedVideoResponse(RecordedVideoBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lesson_id: UUID
    created_at: datetime
    updated_at: datetime
