from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    document_id: Optional[str] = None
    product_id: Optional[str] = None
    source: str
    source_url: str
    document_url: Optional[str] = None
    document_type: str
    title: str
    language: Optional[str] = None
    mime_type: Optional[str] = None
    content: Optional[str] = None
    content_hash: Optional[str] = None
    scraped_at: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
