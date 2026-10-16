from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LiveSessionStatus(str, Enum):
    UPCOMING = "UPCOMING"
    LIVE = "LIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class LiveSessionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_start: datetime
    scheduled_end: datetime
    meeting_url: str = Field(..., min_length=1)
    status: LiveSessionStatus = LiveSessionStatus.UPCOMING
    recording_url: Optional[str] = None

    @field_validator("scheduled_end")
    @classmethod
    def end_after_start(cls, value, info):
        start = info.data.get("scheduled_start")
        if start and value <= start:
            raise ValueError("scheduled_end must be after scheduled_start")
        return value


class LiveSessionCreate(LiveSessionBase):
    pass


class LiveSessionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    meeting_url: Optional[str] = Field(None, min_length=1)
    status: Optional[LiveSessionStatus] = None
    recording_url: Optional[str] = None

    @field_validator("scheduled_end")
    @classmethod
    def end_after_start(cls, value, info):
        start = info.data.get("scheduled_start")
        if start and value and value <= start:
            raise ValueError("scheduled_end must be after scheduled_start")
        return value


class LiveSessionResponse(LiveSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lesson_id: UUID
    created_at: datetime
    updated_at: datetime
