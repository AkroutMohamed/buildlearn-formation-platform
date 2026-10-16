from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    product_id: Optional[str] = None
    name: str
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    applications: Optional[list[str]] = None
    technical_specifications: Optional[dict[str, Any]] = None
    usage_instructions: Optional[str] = None
    limitations: Optional[str] = None
    standards: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    packaging: Optional[str] = None
    storage: Optional[str] = None
    shelf_life: Optional[str] = None
    source_url: Optional[str] = None
    technical_document_url: Optional[str] = None
    document_urls: Optional[list[str]] = None
    language: Optional[str] = None
    scraped_at: Optional[datetime] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
