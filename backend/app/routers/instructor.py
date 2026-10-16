from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.answer import get_answer_service
from app.dependencies.analytics import get_analytics_service
from app.dependencies.course import get_course_service
from app.dependencies.instructor_product import get_instructor_product_service
from app.dependencies.lesson import get_lesson_service
from app.dependencies.live_session import get_live_session_service
from app.dependencies.question import get_question_service
from app.dependencies.quiz import get_quiz_service
from app.dependencies.recorded_video import get_recorded_video_service
from app.dependencies.resource import get_resource_service
from app.dependencies.student import get_student_service
from app.middleware.auth_middleware import get_current_user
from app.middleware.instructor_middleware import require_active_instructor, require_assigned_instructor

from app.models.user import User
from app.schemas.common import InstructorDashboardResponse, MessageResponse
from app.schemas.course import CourseCreate, CourseDetailResponse, CourseResponse, CourseUpdate
from app.schemas.lesson import LessonCreate, LessonResponse, LessonUpdate
from app.schemas.answer import AnswerCreate, AnswerResponse, AnswerUpdate
from app.schemas.analytics import CourseAnalyticsResponse
from app.schemas.certificate import CertificateResponse
from app.schemas.module import ModuleCreate, ModuleResponse, ModuleUpdate
from app.schemas.product import ProductResponse
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate
from app.schemas.quiz import QuizCreate, QuizResponse, QuizUpdate
from app.schemas.student import QuizReview
from app.schemas.resource import ResourceCreate, ResourceResponse
from app.schemas.recorded_video import RecordedVideoCreate, RecordedVideoResponse, RecordedVideoUpdate
from app.schemas.live_session import LiveSessionCreate, LiveSessionResponse, LiveSessionUpdate
from app.schemas.student_management import EnrolledStudentResponse, QuizResultResponse, StudentProgressResponse
from app.services.answer_service import AnswerService
from app.services.analytics_service import AnalyticsService
from app.services.course_service import CourseService
from app.services.instructor_product_service import InstructorProductService
from app.services.live_session_service import LiveSessionService
from app.services.lesson_service import LessonService
from app.services.question_service import QuestionService
from app.services.quiz_service import QuizService
from app.services.recorded_video_service import RecordedVideoService
from app.services.resource_service import ResourceService
from app.services.student_service import StudentService

router = APIRouter(
    prefix="/instructor",
    tags=["Instructor"],
)


@router.get("/products", response_model=list[ProductResponse])
def list_my_products(
    current_user: User = Depends(get_current_user),
    service: InstructorProductService = Depends(get_instructor_product_service),
):
    require_active_instructor(current_user)
    return service.get_assigned_products(current_user)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product_details(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    service: InstructorProductService = Depends(get_instructor_product_service),
):
    require_active_instructor(current_user)
    return service.get_product(current_user, product_id)


@router.get("/products/{product_id}/courses", response_model=list[CourseResponse])
def list_product_courses(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InstructorProductService = Depends(get_instructor_product_service),
):
    require_active_instructor(current_user)
    service.get_product(current_user, product_id)
    return service.course_repository.get_by_product(product_id)


@router.post("/products/{product_id}/courses", response_model=CourseResponse)
def create_course_in_product(
    product_id: UUID,
    course: CourseCreate,
    current_user: User = Depends(get_current_user),
    service: InstructorProductService = Depends(get_instructor_product_service),
):
    require_active_instructor(current_user)
    return service.create_course_in_product(current_user, product_id, course)


@router.get("/courses/{course_id}/analytics", response_model=CourseAnalyticsResponse)
def get_course_analytics(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.get_course_analytics(current_user.id, course_id)


@router.get("/courses/{course_id}/certificates", response_model=list[CertificateResponse])
def list_course_certificates(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: StudentService = Depends(get_student_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.list_course_certificates(current_user.id, course_id)


@router.get("/courses/{course_id}/students", response_model=list[EnrolledStudentResponse])
def list_enrolled_students(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: StudentService = Depends(get_student_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return [
        {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "enrollment_id": enrollment.id,
            "status": enrollment.status,
            "enrolled_at": enrollment.enrolled_at,
        }
        for enrollment, student in service.list_enrolled_students(current_user.id, course_id)
    ]


@router.get("/courses/{course_id}/students/{student_id}/progress", response_model=StudentProgressResponse)
def get_student_progress(
    course_id: UUID,
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: StudentService = Depends(get_student_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.get_student_progress(current_user.id, course_id, student_id)


@router.get("/courses/{course_id}/students/{student_id}/quiz-results", response_model=list[QuizResultResponse])
def get_student_quiz_results(
    course_id: UUID,
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: StudentService = Depends(get_student_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return [
        {
            "id": result.id,
            "quiz_id": result.quiz_id,
            "quiz_title": quiz_title,
            "score": result.score,
            "correct_answers": result.correct_answers,
            "total_questions": result.total_questions,
            "completed_at": result.completed_at,
        }
        for result, quiz_title in service.get_student_quiz_results(current_user.id, course_id, student_id)
    ]


@router.get("/dashboard", response_model=InstructorDashboardResponse)
def instructor_dashboard(
    current_user: User = Depends(get_current_user),
):
    require_active_instructor(current_user)

    return {
        "message": f"Welcome {current_user.first_name}",
        "email": current_user.email,
    }


@router.get("/courses", response_model=list[CourseResponse])
def list_my_courses(
    current_user: User = Depends(get_current_user),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)

    return service.get_instructor_courses(current_user)


@router.get("/courses/{course_id}", response_model=CourseDetailResponse)
def get_course_details(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.get_course_details(current_user, course_id)


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: UUID,
    course: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.update_course(
        current_user=current_user,
        course_id=course_id,
        course_data=course,
    )


@router.delete("/courses/{course_id}", response_model=MessageResponse)
def delete_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_course(current_user=current_user, course_id=course_id)

    return {"message": "Course deleted successfully"}


@router.patch("/courses/{course_id}/publish", response_model=CourseResponse)
def publish_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.publish_course(current_user=current_user, course_id=course_id)


@router.patch("/courses/{course_id}/unpublish", response_model=CourseResponse)
def unpublish_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.unpublish_course(current_user=current_user, course_id=course_id)


@router.get("/courses/{course_id}/modules", response_model=list[ModuleResponse])
def list_course_modules(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.list_course_modules(current_user=current_user, course_id=course_id)


@router.post("/courses/{course_id}/modules", response_model=ModuleResponse)
def create_module(
    course_id: UUID,
    module: ModuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.create_module(
        current_user=current_user,
        course_id=course_id,
        module_data=module,
    )


@router.put("/courses/{course_id}/modules/{module_id}", response_model=ModuleResponse)
def update_module(
    course_id: UUID,
    module_id: UUID,
    module: ModuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.update_module(
        current_user=current_user,
        course_id=course_id,
        module_id=module_id,
        module_data=module,
    )


@router.delete("/courses/{course_id}/modules/{module_id}", response_model=MessageResponse)
def delete_module(
    course_id: UUID,
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CourseService = Depends(get_course_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_module(
        current_user=current_user,
        course_id=course_id,
        module_id=module_id,
    )

    return {"message": "Module deleted successfully"}


@router.get("/courses/{course_id}/modules/{module_id}/lessons", response_model=list[LessonResponse])
def list_lessons(
    course_id: UUID,
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.list_lessons(current_user=current_user, course_id=course_id, module_id=module_id)


@router.post("/courses/{course_id}/modules/{module_id}/lessons", response_model=LessonResponse)
def create_lesson(
    course_id: UUID,
    module_id: UUID,
    lesson: LessonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.create_lesson(
        current_user=current_user,
        course_id=course_id,
        module_id=module_id,
        lesson_data=lesson,
    )


@router.put("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    course_id: UUID,
    module_id: UUID,
    lesson_id: UUID,
    lesson: LessonUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.update_lesson(
        current_user=current_user,
        course_id=course_id,
        module_id=module_id,
        lesson_id=lesson_id,
        lesson_data=lesson,
    )


@router.delete("/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}", response_model=MessageResponse)
def delete_lesson(
    course_id: UUID,
    module_id: UUID,
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_lesson(
        current_user=current_user,
        course_id=course_id,
        module_id=module_id,
        lesson_id=lesson_id,
    )

    return {"message": "Lesson deleted successfully"}


@router.get("/courses/{course_id}/lessons/{lesson_id}/resources", response_model=list[ResourceResponse])
def list_resources(
    course_id: UUID,
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: ResourceService = Depends(get_resource_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.list_resources(current_user=current_user, course_id=course_id, lesson_id=lesson_id)


@router.post("/courses/{course_id}/lessons/{lesson_id}/resources", response_model=ResourceResponse)
async def create_resource(
    course_id: UUID,
    lesson_id: UUID,
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None),
    resource_type: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: ResourceService = Depends(get_resource_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    resource_data = ResourceCreate(
        title=title or file.filename or "Untitled resource",
        url=file.filename or "",
        resource_type=resource_type,
        description=description,
    )

    return await service.create_resource(
        current_user=current_user,
        course_id=course_id,
        lesson_id=lesson_id,
        file=file,
        resource_data=resource_data,
    )


@router.delete("/courses/{course_id}/lessons/{lesson_id}/resources/{resource_id}", response_model=MessageResponse)
def delete_resource(
    course_id: UUID,
    lesson_id: UUID,
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: ResourceService = Depends(get_resource_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_resource(
        current_user=current_user,
        course_id=course_id,
        lesson_id=lesson_id,
        resource_id=resource_id,
    )
    return {"message": "Resource deleted successfully"}


@router.get("/courses/{course_id}/lessons/{lesson_id}/video", response_model=RecordedVideoResponse)
def get_video(
    course_id: UUID,
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: RecordedVideoService = Depends(get_recorded_video_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    video = service.get_video(current_user=current_user, course_id=course_id, lesson_id=lesson_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Recorded video not found")
    return video


@router.post("/courses/{course_id}/lessons/{lesson_id}/video", response_model=RecordedVideoResponse)
def create_video(
    course_id: UUID,
    lesson_id: UUID,
    video: RecordedVideoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: RecordedVideoService = Depends(get_recorded_video_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.create_video(
        current_user=current_user,
        course_id=course_id,
        lesson_id=lesson_id,
        video_data=video,
    )


@router.put("/courses/{course_id}/lessons/{lesson_id}/video", response_model=RecordedVideoResponse)
def update_video(
    course_id: UUID,
    lesson_id: UUID,
    video: RecordedVideoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: RecordedVideoService = Depends(get_recorded_video_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.update_video(
        current_user=current_user,
        course_id=course_id,
        lesson_id=lesson_id,
        video_data=video,
    )


@router.post("/courses/{course_id}/lessons/{lesson_id}/video/upload", response_model=RecordedVideoResponse)
async def upload_recorded_video(
    course_id: UUID,
    lesson_id: UUID,
    file: UploadFile = File(...),
    title: str = Form(...),
    duration_seconds: int | None = Form(None, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: RecordedVideoService = Depends(get_recorded_video_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return await service.upload_video(current_user, course_id, lesson_id, file, title, duration_seconds)


@router.post("/courses/{course_id}/lessons/{lesson_id}/videos/upload", response_model=ResourceResponse)
async def append_recorded_video(
    course_id: UUID, lesson_id: UUID,
    file: UploadFile = File(...), title: str = Form(...),
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
    service: RecordedVideoService = Depends(get_recorded_video_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return await service.upload_video(current_user, course_id, lesson_id, file, title, append=True)


@router.delete("/courses/{course_id}/lessons/{lesson_id}/video", response_model=MessageResponse)
def delete_video(
    course_id: UUID,
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: RecordedVideoService = Depends(get_recorded_video_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_video(
        current_user=current_user,
        course_id=course_id,
        lesson_id=lesson_id,
    )
    return {"message": "Recorded video deleted successfully"}


@router.get("/courses/{course_id}/lessons/{lesson_id}/live-sessions", response_model=list[LiveSessionResponse])
def list_live_sessions(
    course_id: UUID,
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: LiveSessionService = Depends(get_live_session_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.list_sessions(current_user=current_user, course_id=course_id, lesson_id=lesson_id)


@router.post("/courses/{course_id}/lessons/{lesson_id}/live-sessions", response_model=LiveSessionResponse)
def create_live_session(
    course_id: UUID,
    lesson_id: UUID,
    session: LiveSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: LiveSessionService = Depends(get_live_session_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.create_session(
        current_user=current_user,
        course_id=course_id,
        lesson_id=lesson_id,
        session_data=session,
    )


@router.put("/courses/{course_id}/live-sessions/{session_id}", response_model=LiveSessionResponse)
def update_live_session(
    course_id: UUID,
    session_id: UUID,
    session: LiveSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: LiveSessionService = Depends(get_live_session_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.update_session(
        current_user=current_user,
        session_id=session_id,
        session_data=session,
    )


@router.delete("/courses/{course_id}/live-sessions/{session_id}", response_model=MessageResponse)
def delete_live_session(
    course_id: UUID,
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: LiveSessionService = Depends(get_live_session_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_session(
        current_user=current_user,
        session_id=session_id,
    )
    return {"message": "Live session deleted successfully"}



@router.get("/courses/{course_id}/quizzes", response_model=list[QuizResponse])
def list_quizzes(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: QuizService = Depends(get_quiz_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.list_quizzes(current_user=current_user, course_id=course_id)


@router.post("/courses/{course_id}/quizzes", response_model=QuizResponse)
def create_quiz(
    course_id: UUID,
    quiz: QuizCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: QuizService = Depends(get_quiz_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.create_quiz(current_user=current_user, course_id=course_id, quiz_data=quiz)


@router.put("/courses/{course_id}/quizzes/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    course_id: UUID,
    quiz_id: UUID,
    quiz: QuizUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: QuizService = Depends(get_quiz_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.update_quiz(
        current_user=current_user,
        course_id=course_id,
        quiz_id=quiz_id,
        quiz_data=quiz,
    )


@router.delete("/courses/{course_id}/quizzes/{quiz_id}", response_model=MessageResponse)
def delete_quiz(
    course_id: UUID,
    quiz_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: QuizService = Depends(get_quiz_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_quiz(current_user=current_user, course_id=course_id, quiz_id=quiz_id)

    return {"message": "Quiz deleted successfully"}


@router.get("/courses/{course_id}/quizzes/{quiz_id}/questions", response_model=list[QuestionResponse])
def list_questions(
    course_id: UUID,
    quiz_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: QuestionService = Depends(get_question_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.list_questions(current_user=current_user, course_id=course_id, quiz_id=quiz_id)


@router.post("/courses/{course_id}/quizzes/{quiz_id}/questions", response_model=QuestionResponse)
def create_question(
    course_id: UUID,
    quiz_id: UUID,
    question: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: QuestionService = Depends(get_question_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.create_question(
        current_user=current_user,
        course_id=course_id,
        quiz_id=quiz_id,
        question_data=question,
    )


@router.put("/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    course_id: UUID,
    quiz_id: UUID,
    question_id: UUID,
    question: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: QuestionService = Depends(get_question_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.update_question(
        current_user=current_user,
        course_id=course_id,
        quiz_id=quiz_id,
        question_id=question_id,
        question_data=question,
    )


@router.delete("/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}", response_model=MessageResponse)
def delete_question(
    course_id: UUID,
    quiz_id: UUID,
    question_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: QuestionService = Depends(get_question_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_question(
        current_user=current_user,
        course_id=course_id,
        quiz_id=quiz_id,
        question_id=question_id,
    )

    return {"message": "Question deleted successfully"}


@router.get("/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}/answers", response_model=list[AnswerResponse])
def list_answers(
    course_id: UUID,
    quiz_id: UUID,
    question_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AnswerService = Depends(get_answer_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.list_answers(current_user=current_user, course_id=course_id, quiz_id=quiz_id, question_id=question_id)


@router.post("/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}/answers", response_model=AnswerResponse)
def create_answer(
    course_id: UUID,
    quiz_id: UUID,
    question_id: UUID,
    answer: AnswerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AnswerService = Depends(get_answer_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.create_answer(
        current_user=current_user,
        course_id=course_id,
        quiz_id=quiz_id,
        question_id=question_id,
        answer_data=answer,
    )


@router.put("/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}/answers/{answer_id}", response_model=AnswerResponse)
def update_answer(
    course_id: UUID,
    quiz_id: UUID,
    question_id: UUID,
    answer_id: UUID,
    answer: AnswerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AnswerService = Depends(get_answer_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    return service.update_answer(
        current_user=current_user,
        course_id=course_id,
        quiz_id=quiz_id,
        question_id=question_id,
        answer_id=answer_id,
        answer_data=answer,
    )


@router.delete("/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}/answers/{answer_id}", response_model=MessageResponse)
def delete_answer(
    course_id: UUID,
    quiz_id: UUID,
    question_id: UUID,
    answer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: AnswerService = Depends(get_answer_service),
):
    require_active_instructor(current_user)
    require_assigned_instructor(current_user, course_id, db)
    service.delete_answer(
        current_user=current_user,
        course_id=course_id,
        quiz_id=quiz_id,
        question_id=question_id,
        answer_id=answer_id,
    )

    return {"message": "Answer deleted successfully"}


@router.post("/courses", response_model=CourseResponse)
def create_course(
    course: CourseCreate,
    current_user: User = Depends(get_current_user),
):
    require_active_instructor(current_user)
    raise HTTPException(status_code=403, detail="Instructors cannot create products. Products must be created by an administrator.")


@router.get("/courses/{course_id}/quiz-submissions")
def quiz_submissions(course_id: UUID, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_active_instructor(current_user)
    service._get_owned_course(current_user.id, course_id)
    from app.services.quiz_attempt_service import QuizAttemptService
    return QuizAttemptService(service.repository.db).list_for_course(course_id)


@router.post("/courses/{course_id}/quiz-submissions/{attempt_id}/review")
def review_quiz_submission(course_id: UUID, attempt_id: UUID, review: QuizReview, current_user: User = Depends(get_current_user), service: StudentService = Depends(get_student_service)):
    require_active_instructor(current_user)
    service._get_owned_course(current_user.id, course_id)
    from app.services.quiz_attempt_service import QuizAttemptService
    result = QuizAttemptService(service.repository.db).review(current_user.id, course_id, attempt_id, review.grades)
    from app.models.quiz_attempt import QuizAttempt
    attempt = service.repository.db.get(QuizAttempt, attempt_id)
    service.issue_certificate_if_eligible(attempt.student_id, course_id)
    return result
