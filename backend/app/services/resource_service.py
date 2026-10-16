from pathlib import Path
from typing import List
from uuid import UUID
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.models.course_instructor import CourseInstructor
from app.models.lesson import Lesson
from app.models.resource import Resource
from app.models.user import User
from app.repositories.lesson_repository import LessonRepository
from app.repositories.resource_repository import ResourceRepository
from app.schemas.resource import ResourceCreate
from app.utils.upload import validate_upload
from app.config import settings


class ResourceService:
    def __init__(self, repository: ResourceRepository, lesson_repository: LessonRepository):
        self.repository = repository
        self.lesson_repository = lesson_repository

    def _get_lesson_for_owner(self, current_user: User, course_id: UUID, lesson_id: UUID) -> Lesson:
        lesson = self.lesson_repository.get_by_id_with_course(lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == current_user.id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not authorized to manage resources for this course")

        if lesson.module.course_id != course_id:
            raise HTTPException(status_code=404, detail="Lesson not found")

        return lesson

    def list_resources(self, current_user: User, course_id: UUID, lesson_id: UUID) -> List[Resource]:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        return self.repository.get_by_lesson(lesson.id)

    async def create_resource(self, current_user: User, course_id: UUID, lesson_id: UUID, file: UploadFile, resource_data: ResourceCreate) -> Resource:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        await validate_upload(file)

        extension = Path(file.filename or "").suffix.lower()
        stored_name = f"{uuid4().hex}{extension}"
        destination = settings.upload_path / stored_name
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                output.write(chunk)
        resource = Resource(
            lesson_id=lesson.id,
            title=resource_data.title.strip() or file.filename or "Untitled resource",
            url=f"/uploads/{stored_name}",
            resource_type=resource_data.resource_type or (file.content_type if file.content_type else "file"),
            description=resource_data.description,
        )

        try:
            return self.repository.create(resource)
        except Exception:
            destination.unlink(missing_ok=True)
            raise

    def delete_resource(self, current_user: User, course_id: UUID, lesson_id: UUID, resource_id: UUID) -> None:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        resource = self.repository.get_by_id(resource_id)
        if resource is None or resource.lesson_id != lesson.id:
            raise HTTPException(status_code=404, detail="Resource not found")
        self.repository.delete(resource)
        if resource.url.startswith("/uploads/"):
            root = settings.upload_path.resolve()
            destination = (root / resource.url.removeprefix("/uploads/")).resolve()
            if destination.is_relative_to(root):
                destination.unlink(missing_ok=True)
