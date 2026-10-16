from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProgressUpdate(BaseModel):
    completion_percent: int = Field(default=0, ge=0, le=100)
    is_completed: bool = False


class ProgressResponse(ProgressUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    enrollment_id: UUID
    lesson_id: UUID
    completed_at: datetime | None = None
    updated_at: datetime
