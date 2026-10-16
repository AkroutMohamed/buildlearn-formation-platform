from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException

from app.models.course_instructor import CourseInstructor
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.live_session import LiveSession, LiveSessionStatus
from app.models.user import User
from app.repositories.lesson_repository import LessonRepository
from app.repositories.live_session_repository import LiveSessionRepository
from app.schemas.live_session import LiveSessionCreate, LiveSessionUpdate


class LiveSessionService:
    def __init__(self, repository: LiveSessionRepository, lesson_repository: LessonRepository):
        self.repository = repository
        self.lesson_repository = lesson_repository

    def _get_lesson_for_owner(self, current_user: User, course_id: UUID, lesson_id: UUID) -> Lesson:
        lesson = self.lesson_repository.get_by_id_with_course(lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == current_user.id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not authorized to manage live sessions for this course")

        if lesson.module.course_id != course_id:
            raise HTTPException(status_code=404, detail="Lesson not found")

        return lesson

    def _validate_status_transition(self, current_status: LiveSessionStatus, new_status: LiveSessionStatus) -> None:
        if current_status == new_status:
            return

        valid_transitions = {
            LiveSessionStatus.UPCOMING: {LiveSessionStatus.LIVE, LiveSessionStatus.CANCELLED},
            LiveSessionStatus.LIVE: {LiveSessionStatus.COMPLETED, LiveSessionStatus.CANCELLED},
            LiveSessionStatus.COMPLETED: set(),
            LiveSessionStatus.CANCELLED: set(),
        }

        allowed = valid_transitions.get(current_status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=422,
                detail=f"Cannot transition from {current_status.value} to {new_status.value}",
            )

    def list_sessions(self, current_user: User, course_id: UUID, lesson_id: UUID) -> List[LiveSession]:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        return self.repository.get_by_lesson(lesson.id)

    def create_session(self, current_user: User, course_id: UUID, lesson_id: UUID, session_data: LiveSessionCreate) -> LiveSession:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        session = LiveSession(
            lesson_id=lesson.id,
            title=session_data.title.strip(),
            description=session_data.description.strip() if session_data.description else None,
            scheduled_start=session_data.scheduled_start,
            scheduled_end=session_data.scheduled_end,
            meeting_url=session_data.meeting_url.strip(),
            status=session_data.status,
            recording_url=session_data.recording_url.strip() if session_data.recording_url else None,
        )
        return self.repository.create(session)

    def update_session(self, current_user: User, session_id: UUID, session_data: LiveSessionUpdate) -> LiveSession:
        session = self.repository.get_by_id(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Live session not found")

        lesson = self.lesson_repository.get_by_id_with_course(session.lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Live session not found")

        course_id = lesson.module.course_id

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == current_user.id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not authorized to manage live sessions for this course")

        update_data = session_data.model_dump(exclude_unset=True)

        if "status" in update_data:
            new_status = update_data["status"]
            self._validate_status_transition(session.status, new_status)

        if "title" in update_data:
            update_data["title"] = update_data["title"].strip()
        if "meeting_url" in update_data:
            update_data["meeting_url"] = update_data["meeting_url"].strip()
        if "recording_url" in update_data and update_data["recording_url"] is not None:
            update_data["recording_url"] = update_data["recording_url"].strip()
        if "description" in update_data and update_data["description"] is not None:
            update_data["description"] = update_data["description"].strip()

        return self.repository.update(session, update_data)

    def delete_session(self, current_user: User, session_id: UUID) -> None:
        session = self.repository.get_by_id(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Live session not found")

        lesson = self.lesson_repository.get_by_id_with_course(session.lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Live session not found")

        course_id = lesson.module.course_id

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == current_user.id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not authorized to manage live sessions for this course")

        self.repository.delete(session)

    def list_sessions_for_student(self, student_id: UUID, lesson_id: UUID) -> List[LiveSession]:
        lesson = self.lesson_repository.get_by_id_with_course(lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")

        enrollment = self.repository.db.query(Enrollment).filter(
            Enrollment.course_id == lesson.module.course_id,
            Enrollment.user_id == student_id,
        ).first()
        if enrollment is None:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")

        return self.repository.get_by_lesson(lesson.id)
