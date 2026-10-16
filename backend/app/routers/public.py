from fastapi import APIRouter, Depends, Query
from uuid import UUID

from app.dependencies.public import get_public_service
from app.schemas.course import CourseCategory, CourseLevel
from app.schemas.public import PublicCourseDetail, PublicCoursePage
from app.services.public_service import PublicService

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/courses", response_model=PublicCoursePage)
def list_public_courses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=100),
    search: str | None = Query(default=None, max_length=200),
    category: CourseCategory | None = None,
    level: CourseLevel | None = None,
    language: str | None = Query(default=None, max_length=50),
    service: PublicService = Depends(get_public_service),
):
    return service.list_published_courses(page, limit, search, category, level, language)


@router.get("/courses/{course_id}", response_model=PublicCourseDetail)
def get_public_course_details(
    course_id: UUID,
    service: PublicService = Depends(get_public_service),
):
    return service.get_published_course_details(course_id)
