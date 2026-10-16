from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_service import AnalyticsService


def get_analytics_service(
    db: Session = Depends(get_db),
) -> AnalyticsService:
    repository = AnalyticsRepository(db)
    return AnalyticsService(repository)
