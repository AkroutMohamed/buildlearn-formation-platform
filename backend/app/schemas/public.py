from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PublicCourseSummary(BaseModel):
    id: UUID
    title: str
    description: str
    thumbnail: Optional[str]
    language: str
    duration: int
    category: str
    level: str
    instructor: str


class PublicCoursePage(BaseModel):
    items: List[PublicCourseSummary]
    page: int
    limit: int
    total: int
    has_next: bool


class PublicLessonSummary(BaseModel):
    id: UUID
    title: str
    order_index: int
    duration_minutes: Optional[int]


class PublicModuleSummary(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    order_index: int
    lessons: List[PublicLessonSummary]


class PublicQuizSummary(BaseModel):
    id: UUID
    title: str
    description: Optional[str]


class PublicCourseDetail(BaseModel):
    id: UUID
    title: str
    description: str
    thumbnail: Optional[str]
    instructor: str
    category: str
    level: str
    language: str
    duration: int
    objectives: Optional[str]
    modules: List[PublicModuleSummary]
    quizzes: List[PublicQuizSummary]
