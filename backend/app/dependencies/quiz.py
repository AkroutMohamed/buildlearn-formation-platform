from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.quiz_repository import QuizRepository
from app.services.quiz_service import QuizService


def get_quiz_service(
    db: Session = Depends(get_db),
) -> QuizService:
    repository = QuizRepository(db)
    return QuizService(repository)
