from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductResponse


class CourseCategory(str, Enum):
    OUTILLAGE = "Outillage"
    ETANCHEITE = "Étanchéité"
    GYPSTANT = "Gypstant"


class CourseLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class CourseStatus(str, Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"


# -----------------------------
# Create Course
# -----------------------------
class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)

    description: str = Field(..., min_length=10)

    objectives: Optional[str] = None

    thumbnail: Optional[str] = None

    language: str = "French"

    duration: int = Field(default=0, ge=0)

    category: CourseCategory

    level: CourseLevel

    product_id: Optional[UUID] = None


# -----------------------------
# Update Course
# -----------------------------
class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)

    description: Optional[str] = None

    objectives: Optional[str] = None

    thumbnail: Optional[str] = None

    language: Optional[str] = None

    duration: Optional[int] = Field(None, ge=0)

    category: Optional[CourseCategory] = None

    level: Optional[CourseLevel] = None

    product_id: Optional[UUID] = None

    status: Optional[CourseStatus] = None


# -----------------------------
# Response
# -----------------------------
class CourseResponse(BaseModel):
    id: UUID

    instructor_id: UUID

    product_id: UUID | None = None

    product: Optional[ProductResponse] = None

    title: str

    description: str

    objectives: Optional[str]

    thumbnail: Optional[str]

    language: str

    duration: int

    category: CourseCategory

    level: CourseLevel

    status: CourseStatus

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseModuleLessonSummary(BaseModel):
    id: UUID
    title: str
    order_index: int
    lesson_count: int

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(BaseModel):
    id: UUID

    instructor_id: UUID

    product_id: UUID | None = None

    product: Optional[ProductResponse] = None

    title: str

    description: str

    objectives: Optional[str]
    thumbnail: Optional[str]
    language: str
    duration: int
    category: CourseCategory
    level: CourseLevel
    status: CourseStatus
    created_at: datetime
    updated_at: datetime
    modules: List[CourseModuleLessonSummary]

    model_config = ConfigDict(from_attributes=True)


class CourseCatalogItem(BaseModel):
    id: UUID
    title: str
    description: str
    thumbnail: Optional[str]
    language: str
    duration: int
    category: CourseCategory
    level: CourseLevel
    instructor: str


class CourseCatalogPage(BaseModel):
    items: List[CourseCatalogItem]
    page: int
    limit: int
    total: int
    has_next: bool
