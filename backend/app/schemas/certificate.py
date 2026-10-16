from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CertificateResponse(BaseModel):
    id: UUID
    course_id: UUID
    course_title: str
    issued_at: datetime
    certificate_url: str | None
