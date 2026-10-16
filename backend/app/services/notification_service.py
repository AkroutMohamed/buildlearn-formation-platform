from fastapi import HTTPException

from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def list_notifications(self, user_id):
        return self.repository.list_for_user(user_id)

    def mark_read(self, user_id, notification_id):
        notification = self.repository.get_for_user(notification_id, user_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return self.repository.mark_read(notification)

    def delete(self, user_id, notification_id):
        notification = self.repository.get_for_user(notification_id, user_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        self.repository.delete(notification)
