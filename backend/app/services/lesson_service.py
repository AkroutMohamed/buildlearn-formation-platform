from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.models.course_instructor import CourseInstructor
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.user import User
from app.repositories.lesson_repository import LessonRepository
from app.repositories.module_repository import ModuleRepository
from app.schemas.lesson import LessonCreate, LessonUpdate


class LessonService:
    def __init__(self, repository: LessonRepository, module_repository: ModuleRepository):
        self.repository = repository
        self.module_repository = module_repository

    def get_lesson_or_404(self, lesson_id: UUID):
        lesson = self.repository.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return lesson

    def _get_module_for_owner(self, current_user: User, course_id: UUID, module_id: UUID) -> Module:
        module = self.module_repository.get_by_id_with_course(module_id)
        if module is None or module.course_id != course_id:
            raise HTTPException(status_code=404, detail="Module not found")

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == current_user.id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not authorized to manage lessons for this course")

        return module

    def list_lessons(self, current_user: User, course_id: UUID, module_id: UUID) -> List[Lesson]:
        module = self._get_module_for_owner(current_user, course_id, module_id)
        return self.repository.get_by_module(module.id)

    def create_lesson(self, current_user: User, course_id: UUID, module_id: UUID, lesson_data: LessonCreate) -> Lesson:
        module = self._get_module_for_owner(current_user, course_id, module_id)
        lesson = Lesson(
            module_id=module.id,
            title=lesson_data.title.strip(),
            content=lesson_data.content.strip() if lesson_data.content else None,
            duration_minutes=lesson_data.duration_minutes,
            order_index=lesson_data.order_index,
            is_published=lesson_data.is_published,
        )
        return self.repository.create(lesson)

    def update_lesson(self, current_user: User, course_id: UUID, module_id: UUID, lesson_id: UUID, lesson_data: LessonUpdate) -> Lesson:
        module = self._get_module_for_owner(current_user, course_id, module_id)
        lesson = self.get_lesson_or_404(lesson_id)
        if lesson.module_id != module.id:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return self.repository.update(lesson, lesson_data.model_dump(exclude_unset=True))

    def delete_lesson(self, current_user: User, course_id: UUID, module_id: UUID, lesson_id: UUID) -> None:
        module = self._get_module_for_owner(current_user, course_id, module_id)
        lesson = self.get_lesson_or_404(lesson_id)
        if lesson.module_id != module.id:
            raise HTTPException(status_code=404, detail="Lesson not found")
        self.repository.delete(lesson)
