from typing import Optional
from uuid import UUID
from uuid import uuid4
from pathlib import Path
import re
import logging

from fastapi import HTTPException, UploadFile
from app.config import settings

from app.models.course_instructor import CourseInstructor
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.recorded_video import RecordedVideo
from app.models.resource import Resource
from app.repositories.resource_repository import ResourceRepository
from app.models.user import User
from app.repositories.lesson_repository import LessonRepository
from app.repositories.recorded_video_repository import RecordedVideoRepository
from app.schemas.recorded_video import RecordedVideoCreate, RecordedVideoUpdate


class RecordedVideoService:
    MAX_VIDEO_BYTES = 250 * 1024 * 1024

    def __init__(self, repository: RecordedVideoRepository, lesson_repository: LessonRepository):
        self.repository = repository
        self.lesson_repository = lesson_repository

    def _remove_uploaded_file(self, url: str) -> None:
        if re.fullmatch(r"/uploads/videos/[a-f0-9]{32}\.(mp4|webm|ogv)", url):
            try:
                (settings.upload_path / "videos" / Path(url).name).unlink(missing_ok=True)
            except OSError:
                logging.getLogger(__name__).warning("Could not remove obsolete uploaded video", exc_info=True)

    async def upload_video(self, current_user: User, course_id: UUID, lesson_id: UUID,
                           file: UploadFile, title: str, duration_seconds: int | None = None, append: bool = False) -> RecordedVideo | Resource:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        title = title.strip()
        if not title or len(title) > 200:
            raise HTTPException(status_code=400, detail="Enter a video title of 1–200 characters")
        if duration_seconds is not None and duration_seconds < 0:
            raise HTTPException(status_code=400, detail="Duration cannot be negative")
        extension = Path(file.filename or "").suffix.lower()
        allowed = {".mp4": "video/mp4", ".webm": "video/webm", ".ogv": "video/ogg"}
        if extension not in allowed or file.content_type not in {allowed[extension], "application/octet-stream"}:
            raise HTTPException(status_code=400, detail="Choose an MP4, WebM, or OGV video")
        existing = None if append else self.repository.get_by_lesson(lesson.id)
        old_url = existing.video_url if existing else None
        directory = settings.upload_path / "videos"
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"{uuid4().hex}{extension}"
        try:
            total = 0
            with destination.open("xb") as output:
                while chunk := await file.read(1024 * 1024):
                    if total == 0:
                        valid = (extension == ".mp4" and chunk[4:8] == b"ftyp"
                                 or extension == ".webm" and chunk.startswith(b"\x1a\x45\xdf\xa3")
                                 or extension == ".ogv" and chunk.startswith(b"OggS"))
                        if not valid:
                            raise HTTPException(status_code=400, detail="File content does not match the selected video format")
                    total += len(chunk)
                    if total > self.MAX_VIDEO_BYTES:
                        raise HTTPException(status_code=413, detail="Video must be 250 MB or smaller")
                    output.write(chunk)
            if not total:
                raise HTTPException(status_code=400, detail="Uploaded video is empty")
            values = {"title": title, "video_url": f"/uploads/videos/{destination.name}", "duration_seconds": duration_seconds}
            if append:
                result = ResourceRepository(self.repository.db).create(Resource(
                    lesson_id=lesson.id, title=title, url=values["video_url"], resource_type=allowed[extension],
                ))
            else:
                result = self.repository.update(existing, values) if existing else self.repository.create(RecordedVideo(lesson_id=lesson.id, **values))
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        if old_url:
            self._remove_uploaded_file(old_url)
        return result

    def _get_lesson_for_owner(self, current_user: User, course_id: UUID, lesson_id: UUID) -> Lesson:
        lesson = self.lesson_repository.get_by_id_with_course(lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == current_user.id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not authorized to manage videos for this course")

        if lesson.module.course_id != course_id:
            raise HTTPException(status_code=404, detail="Lesson not found")

        return lesson

    def get_video(self, current_user: User, course_id: UUID, lesson_id: UUID) -> Optional[RecordedVideo]:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        return self.repository.get_by_lesson(lesson.id)

    def create_video(self, current_user: User, course_id: UUID, lesson_id: UUID, video_data: RecordedVideoCreate) -> RecordedVideo:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        existing = self.repository.get_by_lesson(lesson.id)
        if existing:
            raise HTTPException(status_code=409, detail="A recorded video already exists for this lesson")

        video = RecordedVideo(
            lesson_id=lesson.id,
            title=video_data.title.strip(),
            description=video_data.description.strip() if video_data.description else None,
            video_url=video_data.video_url.strip(),
            duration_seconds=video_data.duration_seconds,
            thumbnail_url=video_data.thumbnail_url.strip() if video_data.thumbnail_url else None,
        )
        return self.repository.create(video)

    def update_video(self, current_user: User, course_id: UUID, lesson_id: UUID, video_data: RecordedVideoUpdate) -> RecordedVideo:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        video = self.repository.get_by_lesson(lesson.id)
        if video is None:
            raise HTTPException(status_code=404, detail="Recorded video not found")

        update_data = video_data.model_dump(exclude_unset=True)
        if "title" in update_data:
            update_data["title"] = update_data["title"].strip()
        if "video_url" in update_data:
            update_data["video_url"] = update_data["video_url"].strip()
        if "thumbnail_url" in update_data and update_data["thumbnail_url"] is not None:
            update_data["thumbnail_url"] = update_data["thumbnail_url"].strip()

        old_url = video.video_url
        result = self.repository.update(video, update_data)
        if "video_url" in update_data and old_url != result.video_url:
            self._remove_uploaded_file(old_url)
        return result

    def delete_video(self, current_user: User, course_id: UUID, lesson_id: UUID) -> None:
        lesson = self._get_lesson_for_owner(current_user, course_id, lesson_id)
        video = self.repository.get_by_lesson(lesson.id)
        if video is None:
            raise HTTPException(status_code=404, detail="Recorded video not found")
        old_url = video.video_url
        self.repository.delete(video)
        self._remove_uploaded_file(old_url)

    def get_video_for_student(self, student_id: UUID, lesson_id: UUID) -> Optional[RecordedVideo]:
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
