from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ChunkBase(BaseModel):
    chunk_id: Optional[str] = None
    document_id: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    supplier: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    document_url: Optional[str] = None
    document_type: Optional[str] = None
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_index: Optional[int] = None
    text: Optional[str] = None
    language: Optional[str] = None
    content_hash: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    source_type: Optional[str] = None
    discovery_provider: Optional[str] = None
    domain: Optional[str] = None
    confidence: Optional[str] = None
    evidence: Optional[str] = None


class ChunkCreate(ChunkBase):
    pass


class ChunkResponse(ChunkBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    score: float | None = None
