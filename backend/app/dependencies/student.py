from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.student_repository import StudentRepository
from app.repositories.notification_repository import NotificationRepository
from app.services.student_service import StudentService


def get_student_service(
    db: Session = Depends(get_db),
) -> StudentService:
    repository = StudentRepository(db)
    return StudentService(repository, NotificationRepository(db))
