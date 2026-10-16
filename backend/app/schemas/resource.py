from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResourceBase(BaseModel):
    title: str
    url: str
    resource_type: str | None = None
    description: str | None = None


class ResourceCreate(ResourceBase):
    pass


class ResourceResponse(ResourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lesson_id: UUID
