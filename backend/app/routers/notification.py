from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies.notification import get_notification_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(current_user: User = Depends(get_current_user), service: NotificationService = Depends(get_notification_service)):
    return service.list_notifications(current_user.id)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: UUID, current_user: User = Depends(get_current_user), service: NotificationService = Depends(get_notification_service)):
    return service.mark_read(current_user.id, notification_id)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: UUID, current_user: User = Depends(get_current_user), service: NotificationService = Depends(get_notification_service)):
    service.delete(current_user.id, notification_id)
