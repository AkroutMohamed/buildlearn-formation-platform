from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ModuleBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    order_index: int = Field(default=0, ge=0)


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)


class ModuleResponse(ModuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: UUID