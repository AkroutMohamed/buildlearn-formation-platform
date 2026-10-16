from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from app.dependencies.student import get_student_service
from app.dependencies.live_session import get_live_session_service
from app.dependencies.recorded_video import get_recorded_video_service
from app.middleware.auth_middleware import get_current_user
from app.middleware.role_middleware import require_role
from app.models.user import User
from app.schemas.student import QuizSubmission
from app.schemas.certificate import CertificateResponse
from app.schemas.common import StudentDashboardResponse
from app.schemas.course import CourseCatalogPage, CourseCategory, CourseLevel
from app.schemas.live_session import LiveSessionResponse
from app.schemas.recorded_video import RecordedVideoResponse
from app.services.student_service import StudentService

router = APIRouter(prefix="/student", tags=["Student"])


@router.get("/dashboard", response_model=StudentDashboardResponse)
def student_dashboard(
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
):
    require_role(["student"])(current_user)
    return service.dashboard(current_user.id)


@router.post("/courses/{course_id}/enroll", status_code=201)
def enroll(course_id: UUID, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.enroll(current_user.id, course_id)


@router.get("/courses", response_model=CourseCatalogPage)
def available_courses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=100),
    search: str | None = Query(default=None, max_length=200),
    category: CourseCategory | None = None,
    level: CourseLevel | None = None,
    language: str | None = Query(default=None, max_length=50),
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
):
    require_role(["student"])(current_user)
    return service.available_courses(page, limit, search, category, level, language)


@router.get("/my-courses")
def my_courses(
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
):
    require_role(["student"])(current_user)
    return service.my_courses(current_user.id)


@router.get("/courses/{course_id}")
def course_details(course_id: UUID, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.course_details(current_user.id, course_id)


@router.get("/lessons/{lesson_id}")
def lesson_details(lesson_id: UUID, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.lesson_details(current_user.id, lesson_id)


@router.get("/lessons/{lesson_id}/video", response_model=RecordedVideoResponse)
def get_lesson_video(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    service: RecordedVideoService = Depends(get_recorded_video_service),
):
    require_role(["student"])(current_user)
    video = service.get_video_for_student(current_user.id, lesson_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Recorded video not found")
    return video


@router.get("/lessons/{lesson_id}/live-sessions", response_model=list[LiveSessionResponse])
def get_lesson_live_sessions(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    service: LiveSessionService = Depends(get_live_session_service),
):
    require_role(["student"])(current_user)
    return service.list_sessions_for_student(current_user.id, lesson_id)


@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(lesson_id: UUID, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.complete_lesson(current_user.id, lesson_id)


@router.get("/quizzes/{quiz_id}")
def quiz_details(quiz_id: UUID, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.quiz_details(current_user.id, quiz_id)


@router.post("/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: UUID, submission: QuizSubmission, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.submit_quiz(current_user.id, quiz_id, submission.answers)


@router.get("/progress")
def student_progress(current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.progress(current_user.id)


@router.get("/certificates", response_model=list[CertificateResponse])
def list_certificates(current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.list_certificates(current_user.id)


@router.get("/certificates/{certificate_id}", response_model=CertificateResponse)
def get_certificate(certificate_id: UUID, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_role(["student"])(current_user)
    return service.get_certificate(current_user.id, certificate_id)
