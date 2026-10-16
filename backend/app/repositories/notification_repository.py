from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID, title: str, message: str):
        notification = Notification(user_id=user_id, title=title, message=message)
        self.db.add(notification)
        return notification

    def get_for_user(self, notification_id: UUID, user_id: UUID):
        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: UUID):
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    def mark_read(self, notification: Notification):
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def delete(self, notification: Notification):
        self.db.delete(notification)
        self.db.commit()
