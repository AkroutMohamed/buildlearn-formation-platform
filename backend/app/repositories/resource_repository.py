from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.resource import Resource


class ResourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, resource: Resource) -> Resource:
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def get_by_id(self, resource_id: UUID) -> Optional[Resource]:
        return self.db.query(Resource).filter(Resource.id == resource_id).first()

    def get_by_lesson(self, lesson_id: UUID):
        return (
            self.db.query(Resource)
            .filter(Resource.lesson_id == lesson_id)
            .order_by(Resource.title.asc())
            .all()
        )

    def delete(self, resource: Resource):
        self.db.delete(resource)
        self.db.commit()
