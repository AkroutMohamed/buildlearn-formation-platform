from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.lesson import Lesson
from app.models.module import Module


class LessonRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, lesson: Lesson) -> Lesson:
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def get_by_id(self, lesson_id: UUID) -> Optional[Lesson]:
        return self.db.query(Lesson).filter(Lesson.id == lesson_id).first()

    def get_by_id_with_course(self, lesson_id: UUID) -> Optional[Lesson]:
        return (
            self.db.query(Lesson)
            .options(joinedload(Lesson.module).joinedload(Module.course))
            .filter(Lesson.id == lesson_id)
            .first()
        )

    def get_by_module(self, module_id: UUID):
        return (
            self.db.query(Lesson)
            .filter(Lesson.module_id == module_id)
            .order_by(Lesson.order_index.asc())
            .all()
        )

    def update(self, lesson: Lesson, values: dict):
        for field, value in values.items():
            setattr(lesson, field, value)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def delete(self, lesson: Lesson):
        self.db.delete(lesson)
        self.db.commit()
