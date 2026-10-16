from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.question_repository import QuestionRepository
from app.services.question_service import QuestionService


def get_question_service(
    db: Session = Depends(get_db),
) -> QuestionService:
    repository = QuestionRepository(db)
    return QuestionService(repository)
