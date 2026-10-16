from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.module import Module


class ModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, module: Module) -> Module:
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module

    def get_by_id(self, module_id: UUID) -> Optional[Module]:
        return self.db.query(Module).filter(Module.id == module_id).first()

    def get_by_id_with_course(self, module_id: UUID) -> Optional[Module]:
        return (
            self.db.query(Module)
            .options(joinedload(Module.course))
            .filter(Module.id == module_id)
            .first()
        )

    def get_by_course(self, course_id: UUID):
        return (
            self.db.query(Module)
            .filter(Module.course_id == course_id)
            .order_by(Module.order_index.asc())
            .all()
        )

    def update(self, module: Module, values: dict):
        for field, value in values.items():
            setattr(module, field, value)
        self.db.commit()
        self.db.refresh(module)
        return module

    def delete(self, module: Module):
        self.db.delete(module)
        self.db.commit()
