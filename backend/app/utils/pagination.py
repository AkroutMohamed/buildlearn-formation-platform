from typing import Generic, TypeVar

from pydantic import BaseModel, Field


ItemType = TypeVar("ItemType")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[ItemType]):
    items: list[ItemType]
    page: int
    page_size: int
    total: int
    pages: int


def paginate(query, page: int = 1, page_size: int = 20):
    page = max(1, page)
    page_size = min(100, max(1, page_size))
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )