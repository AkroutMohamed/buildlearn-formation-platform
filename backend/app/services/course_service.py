from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.models.course import (
    Course,
    CourseStatus,
)
from app.models.course_instructor import CourseInstructor
from app.models.module import Module
from app.models.user import User
from app.repositories.course_repository import CourseRepository
from app.repositories.module_repository import ModuleRepository
from app.schemas.course import CourseCreate, CourseDetailResponse, CourseUpdate
from app.schemas.module import ModuleCreate, ModuleUpdate


class CourseService:
    def __init__(self, repository: CourseRepository, module_repository: ModuleRepository):
        self.repository = repository
        self.module_repository = module_repository

    # ==========================================================
    # Private Validation Methods
    # ==========================================================

    def _validate_create_data(self, course_data: CourseCreate):
        """Validate data before creating a course."""

        if len(course_data.title.strip()) < 3:
            raise HTTPException(status_code=422, detail="Course title must contain at least 3 characters.")

        if len(course_data.description.strip()) < 10:
            raise HTTPException(status_code=422, detail="Course description must contain at least 10 characters.")

        if course_data.duration < 0:
            raise HTTPException(status_code=422, detail="Duration cannot be negative.")

    def _validate_publish(self, course: Course):
        """
        Business rules before publishing.
        """

        if not course.title:
            raise HTTPException(status_code=422, detail="Course title is required.")

        if not course.description:
            raise HTTPException(status_code=422, detail="Course description is required.")

        if not course.category:
            raise HTTPException(status_code=422, detail="Course category is required.")

        if not course.level:
            raise HTTPException(status_code=422, detail="Course level is required.")

    def _ensure_assigned(self, course: Course, current_user: User):
        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course.id,
            CourseInstructor.instructor_id == current_user.id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not assigned to this course")

    # ==========================================================
    # Create Course
    # ==========================================================

    def create_course(
        self,
        instructor_id: UUID,
        course_data: CourseCreate,
    ) -> Course:

        self._validate_create_data(course_data)

        course = Course(
            instructor_id=instructor_id,
            title=course_data.title.strip(),
            description=course_data.description.strip(),
            objectives=course_data.objectives,
            thumbnail=course_data.thumbnail,
            language=course_data.language,
            duration=course_data.duration,
            category=course_data.category,
            level=course_data.level,
            status=CourseStatus.DRAFT,
        )

        return self.repository.create(course)

    # ==========================================================
    # Get Course
    # ==========================================================

    def get_course(self, course_id: UUID) -> Course:

        course = self.repository.get_by_id(course_id)

        if course is None:
            raise HTTPException(status_code=404, detail="Course not found.")

        return course

    def get_course_details(
        self,
        current_user: User,
        course_id: UUID,
    ) -> CourseDetailResponse:

        course = self.repository.get_by_id_with_modules_and_lessons(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found.")

        self._ensure_assigned(course, current_user)

        modules = []
        for module in course.modules:
            modules.append(
                {
                    "id": module.id,
                    "title": module.title,
                    "order_index": module.order_index,
                    "lesson_count": len(module.lessons),
                }
            )

        return CourseDetailResponse(
            id=course.id,
            instructor_id=course.instructor_id,
            title=course.title,
            description=course.description,
            objectives=course.objectives,
            thumbnail=course.thumbnail,
            language=course.language,
            duration=course.duration,
            category=course.category,
            level=course.level,
            status=course.status,
            created_at=course.created_at,
            updated_at=course.updated_at,
            modules=modules,
        )

    # ==========================================================
    # Get Instructor Courses
    # ==========================================================

    def get_instructor_courses(
        self,
        current_user: User,
    ) -> List[Course]:

        return self.repository.get_assigned_instructor_courses(current_user.id)

    # ==========================================================
    # Update Course
    # ==========================================================

    def update_course(
        self,
        current_user: User,
        course_id: UUID,
        course_data: CourseUpdate,
    ) -> Course:

        course = self.get_course(course_id)

        self._ensure_assigned(course, current_user)

        update_data = course_data.model_dump(exclude_unset=True)

        update_data.pop("status", None)

        if "title" in update_data and len(str(update_data["title"]).strip()) < 3:
            raise HTTPException(status_code=422, detail="Course title must contain at least 3 characters.")

        if "description" in update_data and len(str(update_data["description"]).strip()) < 10:
            raise HTTPException(status_code=422, detail="Course description must contain at least 10 characters.")

        if "duration" in update_data and update_data["duration"] < 0:
            raise HTTPException(status_code=422, detail="Duration cannot be negative.")

        for field, value in update_data.items():
            setattr(course, field, value)

        return self.repository.update(course)

    # ==========================================================
    # Delete Course
    # ==========================================================

    def delete_course(
        self,
        current_user: User,
        course_id: UUID,
    ) -> None:

        course = self.get_course(course_id)

        self._ensure_assigned(course, current_user)

        self.repository.delete(course)

    # ==========================================================
    # Module Management
    # ==========================================================

    def list_course_modules(
        self,
        current_user: User,
        course_id: UUID,
    ) -> List[Module]:

        course = self.get_course(course_id)

        self._ensure_assigned(course, current_user)

        return self.module_repository.get_by_course(course_id)

    def create_module(
        self,
        current_user: User,
        course_id: UUID,
        module_data: ModuleCreate,
    ) -> Module:

        course = self.get_course(course_id)

        self._ensure_assigned(course, current_user)

        if len(str(module_data.title).strip()) < 1:
            raise HTTPException(status_code=422, detail="Module title is required.")

        module = Module(
            course_id=course.id,
            title=module_data.title.strip(),
            description=module_data.description.strip() if module_data.description else None,
            order_index=module_data.order_index,
        )

        return self.module_repository.create(module)

    def update_module(
        self,
        current_user: User,
        course_id: UUID,
        module_id: UUID,
        module_data: ModuleUpdate,
    ) -> Module:

        course = self.get_course(course_id)

        self._ensure_assigned(course, current_user)

        module = self.module_repository.get_by_id(module_id)

        if module is None or module.course_id != course_id:
            raise HTTPException(status_code=404, detail="Module not found.")

        update_data = module_data.model_dump(exclude_unset=True)

        if "title" in update_data and len(str(update_data["title"]).strip()) < 1:
            raise HTTPException(status_code=422, detail="Module title is required.")

        return self.module_repository.update(module, update_data)

    def delete_module(
        self,
        current_user: User,
        course_id: UUID,
        module_id: UUID,
    ) -> None:

        course = self.get_course(course_id)

        self._ensure_assigned(course, current_user)

        module = self.module_repository.get_by_id(module_id)

        if module is None or module.course_id != course_id:
            raise HTTPException(status_code=404, detail="Module not found.")

        self.module_repository.delete(module)

    # ==========================================================
    # Publish Course
    # ==========================================================

    def publish_course(
        self,
        current_user: User,
        course_id: UUID,
    ) -> Course:

        course = self.get_course(course_id)

        self._ensure_assigned(course, current_user)

        self._validate_publish(course)

        course.status = CourseStatus.PUBLISHED

        return self.repository.update(course)

    # ==========================================================
    # Archive Course
    # ==========================================================

    def unpublish_course(
        self,
        current_user: User,
        course_id: UUID,
    ) -> Course:

        course = self.get_course(course_id)

        self._ensure_assigned(course, current_user)

        course.status = CourseStatus.DRAFT

        return self.repository.update(course)

