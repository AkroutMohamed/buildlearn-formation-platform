from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EnrollmentCreate(BaseModel):
    user_id: UUID
    course_id: UUID


class EnrollmentResponse(EnrollmentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    enrolled_at: datetime
