from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.certificate import Certificate
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.live_session import LiveSession
from app.models.module import Module
from app.models.progress import Progress
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.models.recorded_video import RecordedVideo
from app.models.user import User, UserRole


class StudentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, student_id: UUID) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.id == student_id, User.role == UserRole.STUDENT)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email, User.role == UserRole.STUDENT)
            .first()
        )

    def get_all(self):
        return self.db.query(User).filter(User.role == UserRole.STUDENT).all()

    def get_by_course(self, course_id: UUID):
        return (
            self.db.query(User)
            .join(Enrollment, Enrollment.user_id == User.id)
            .filter(Enrollment.course_id == course_id, User.role == UserRole.STUDENT)
            .all()
        )

    def get_course_enrollments(self, course_id: UUID):
        return (
            self.db.query(Enrollment, User)
            .join(User, Enrollment.user_id == User.id)
            .filter(Enrollment.course_id == course_id, User.role == UserRole.STUDENT)
            .order_by(Enrollment.enrolled_at.desc())
            .all()
        )

    def get_course_enrollment(self, course_id: UUID, student_id: UUID):
        return (
            self.db.query(Enrollment)
            .join(User, Enrollment.user_id == User.id)
            .filter(
                Enrollment.course_id == course_id,
                Enrollment.user_id == student_id,
                User.role == UserRole.STUDENT,
            )
            .first()
        )

    def get_progress_for_enrollment(self, enrollment_id: UUID):
        return self.db.query(Progress).filter(Progress.enrollment_id == enrollment_id).all()

    def get_course_by_id(self, course_id: UUID):
        return self.db.query(Course).filter(Course.id == course_id).first()

    def get_available_courses_page(self, page: int, limit: int, search=None, category=None, level=None, language=None):
        query = (
            self.db.query(Course)
            .options(joinedload(Course.instructor))
            .filter(Course.status == CourseStatus.PUBLISHED)
            .order_by(Course.created_at.desc())
        )
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(Course.title.ilike(pattern) | Course.description.ilike(pattern))
        if category:
            query = query.filter(Course.category == category)
        if level:
            query = query.filter(Course.level == level)
        if language:
            query = query.filter(Course.language.ilike(language.strip()))
        total = query.count()
        courses = query.offset((page - 1) * limit).limit(limit).all()
        return courses, total

    def create_enrollment(self, student_id: UUID, course_id: UUID):
        enrollment = Enrollment(user_id=student_id, course_id=course_id)
        self.db.add(enrollment)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return None
        self.db.refresh(enrollment)
        return enrollment

    def get_student_enrollments(self, student_id: UUID):
        return (
            self.db.query(Enrollment)
            .options(joinedload(Enrollment.course).joinedload(Course.instructor))
            .filter(Enrollment.user_id == student_id)
            .order_by(Enrollment.enrolled_at.desc())
            .all()
        )

    def get_course_content(self, course_id: UUID):
        return (
            self.db.query(Course)
            .options(
                joinedload(Course.instructor),
                selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.resources),
                selectinload(Course.quizzes).selectinload(Quiz.questions).selectinload(Question.answers),
            )
            .filter(Course.id == course_id)
            .first()
        )

    def get_lesson_with_content(self, lesson_id: UUID):
        return (
            self.db.query(Lesson)
            .options(joinedload(Lesson.module).joinedload(Module.course), selectinload(Lesson.resources))
            .filter(Lesson.id == lesson_id)
            .first()
        )

    def get_quiz_with_content(self, quiz_id: UUID):
        return (
            self.db.query(Quiz)
            .options(
                joinedload(Quiz.course),
                selectinload(Quiz.questions).selectinload(Question.answers),
            )
            .filter(Quiz.id == quiz_id)
            .first()
        )

    def get_lesson_progress(self, enrollment_id: UUID, lesson_id: UUID):
        return (
            self.db.query(Progress)
            .filter(Progress.enrollment_id == enrollment_id, Progress.lesson_id == lesson_id)
            .first()
        )

    def complete_lesson(self, enrollment_id: UUID, lesson_id: UUID):
        from datetime import datetime

        progress = self.get_lesson_progress(enrollment_id, lesson_id)
        if progress is None:
            progress = Progress(enrollment_id=enrollment_id, lesson_id=lesson_id)
            self.db.add(progress)
        progress.completion_percent = 100
        progress.is_completed = True
        progress.completed_at = progress.completed_at or datetime.utcnow()
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            progress = self.get_lesson_progress(enrollment_id, lesson_id)
            if progress is None:
                raise
            progress.completion_percent = 100
            progress.is_completed = True
            progress.completed_at = progress.completed_at or datetime.utcnow()
            self.db.commit()
        self.db.refresh(progress)
        return progress

    def count_course_lessons(self, course_id: UUID):
        return (
            self.db.query(Lesson)
            .join(Module, Lesson.module_id == Module.id)
            .filter(Module.course_id == course_id)
            .count()
        )

    def count_certificates(self, student_id: UUID):
        return self.db.query(Certificate).filter(Certificate.user_id == student_id).count()

    def get_certificate_for_student(self, certificate_id: UUID, student_id: UUID):
        return (
            self.db.query(Certificate)
            .options(joinedload(Certificate.course))
            .filter(Certificate.id == certificate_id, Certificate.user_id == student_id)
            .first()
        )

    def get_student_certificates(self, student_id: UUID):
        return (
            self.db.query(Certificate)
            .options(joinedload(Certificate.course))
            .filter(Certificate.user_id == student_id)
            .order_by(Certificate.issued_at.desc())
            .all()
        )

    def get_course_certificates(self, course_id: UUID):
        return (
            self.db.query(Certificate)
            .options(joinedload(Certificate.course))
            .filter(Certificate.course_id == course_id)
            .order_by(Certificate.issued_at.desc())
            .all()
        )

    def get_certificate_for_course_student(self, course_id: UUID, student_id: UUID):
        return (
            self.db.query(Certificate)
            .filter(Certificate.course_id == course_id, Certificate.user_id == student_id)
            .first()
        )

    def create_certificate(self, student_id: UUID, course_id: UUID):
        certificate = Certificate(user_id=student_id, course_id=course_id)
        self.db.add(certificate)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return None
        self.db.refresh(certificate)
        return certificate

    def create_quiz_result(self, student_id: UUID, course_id: UUID, quiz_id: UUID, correct: int, total: int):
        result = QuizResult(
            student_id=student_id,
            course_id=course_id,
            quiz_id=quiz_id,
            score=(correct / total * 100) if total else 0,
            correct_answers=correct,
            total_questions=total,
        )
        self.db.add(result)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return None
        self.db.refresh(result)
        return result

    def get_quiz_result(self, student_id: UUID, quiz_id: UUID):
        return (
            self.db.query(QuizResult)
            .filter(QuizResult.student_id == student_id, QuizResult.quiz_id == quiz_id)
            .first()
        )

    def get_quiz_results(self, course_id: UUID, student_id: UUID):
        return (
            self.db.query(QuizResult, Quiz.title)
            .join(Quiz, Quiz.id == QuizResult.quiz_id)
            .filter(
                QuizResult.course_id == course_id,
                QuizResult.student_id == student_id,
            )
            .order_by(QuizResult.completed_at.desc())
            .all()
        )

    def get_lesson_video(self, lesson_id: UUID):
        return (
            self.db.query(RecordedVideo)
            .filter(RecordedVideo.lesson_id == lesson_id)
            .first()
        )

    def get_lesson_live_sessions(self, lesson_id: UUID):
        return (
            self.db.query(LiveSession)
            .filter(LiveSession.lesson_id == lesson_id)
            .order_by(LiveSession.scheduled_start.asc())
            .all()
        )
