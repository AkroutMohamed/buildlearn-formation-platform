from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.answer_repository import AnswerRepository
from app.services.answer_service import AnswerService


def get_answer_service(
    db: Session = Depends(get_db),
) -> AnswerService:
    repository = AnswerRepository(db)
    return AnswerService(repository)
