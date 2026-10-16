from fastapi import HTTPException

from app.models.course import CourseStatus
from app.models.course_instructor import CourseInstructor
from app.repositories.student_repository import StudentRepository
from app.repositories.notification_repository import NotificationRepository


class StudentService:
    def __init__(self, repository: StudentRepository, notification_repository: NotificationRepository | None = None):
        self.repository = repository
        self.notification_repository = notification_repository

    def _notify(self, user_id, title, message):
        if self.notification_repository:
            self.notification_repository.create(user_id, title, message)
            self.repository.db.commit()

    def get_student_or_404(self, student_id):
        student = self.repository.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student

    def find_student_by_email(self, email):
        return self.repository.get_by_email(email)

    def list_students(self):
        return self.repository.get_all()

    def list_course_students(self, course_id):
        return self.repository.get_by_course(course_id)

    def _get_owned_course(self, instructor_id, course_id):
        course = self.repository.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == instructor_id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not assigned to this course")
        return course

    def list_enrolled_students(self, instructor_id, course_id):
        self._get_owned_course(instructor_id, course_id)
        return self.repository.get_course_enrollments(course_id)

    def get_student_progress(self, instructor_id, course_id, student_id):
        self._get_owned_course(instructor_id, course_id)
        enrollment = self.repository.get_course_enrollment(course_id, student_id)
        if not enrollment:
            raise HTTPException(status_code=404, detail="Student is not enrolled in this course")

        progress_records = self.repository.get_progress_for_enrollment(enrollment.id)
        total_lessons = self.repository.count_course_lessons(course_id)
        completed_lessons = sum(1 for progress in progress_records if progress.is_completed)
        completion_percent = round((completed_lessons / total_lessons) * 100, 2) if total_lessons else 0.0
        updated_times = [progress.updated_at for progress in progress_records if progress.updated_at]

        return {
            "student_id": student_id,
            "course_id": course_id,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "completion_percent": completion_percent,
            "last_updated_at": max(updated_times) if updated_times else None,
        }

    def get_student_quiz_results(self, instructor_id, course_id, student_id):
        self._get_owned_course(instructor_id, course_id)
        if not self.repository.get_course_enrollment(course_id, student_id):
            raise HTTPException(status_code=404, detail="Student is not enrolled in this course")
        return self.repository.get_quiz_results(course_id, student_id)

    def _get_enrollment_or_403(self, student_id, course_id):
        enrollment = self.repository.get_course_enrollment(course_id, student_id)
        if not enrollment:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")
        return enrollment

    def _progress_summary(self, enrollment):
        total = self.repository.count_course_lessons(enrollment.course_id)
        completed = sum(item.is_completed for item in self.repository.get_progress_for_enrollment(enrollment.id))
        percentage = round((completed / total) * 100, 2) if total else 0.0
        return total, completed, percentage

    @staticmethod
    def _instructor_name(course):
        return f"{course.instructor.first_name} {course.instructor.last_name}"

    def dashboard(self, student_id):
        enrollments = self.repository.get_student_enrollments(student_id)
        course_summaries = [self._progress_summary(enrollment) for enrollment in enrollments]
        return {
            "enrolled_courses": len(enrollments),
            "completed_courses": sum(percentage == 100 for _, _, percentage in course_summaries),
            "certificates_count": self.repository.count_certificates(student_id),
            "overall_progress": round(sum(item[2] for item in course_summaries) / len(course_summaries), 2) if course_summaries else 0.0,
        }

    def enroll(self, student_id, course_id):
        course = self.repository.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        if course.status != CourseStatus.PUBLISHED:
            raise HTTPException(status_code=422, detail="Cannot enroll in an unpublished course")
        if self.repository.get_course_enrollment(course_id, student_id):
            raise HTTPException(status_code=409, detail="Already enrolled in this course")
        enrollment = self.repository.create_enrollment(student_id, course_id)
        if enrollment is None:
            raise HTTPException(status_code=409, detail="Already enrolled in this course")
        self._notify(student_id, "Course enrollment", f"You enrolled in {course.title}.")
        return enrollment

    def my_courses(self, student_id):
        result = []
        for enrollment in self.repository.get_student_enrollments(student_id):
            total, completed, percentage = self._progress_summary(enrollment)
            result.append({
                "id": enrollment.course.id,
                "title": enrollment.course.title,
                "instructor": self._instructor_name(enrollment.course),
                "thumbnail": enrollment.course.thumbnail,
                "progress": percentage,
                "completed_lessons": completed,
                "total_lessons": total,
                "status": "completed" if percentage == 100 else enrollment.status,
            })
        return result

    def available_courses(self, page: int, limit: int, search=None, category=None, level=None, language=None):
        courses, total = self.repository.get_available_courses_page(page, limit, search, category, level, language)
        return {
            "items": [
                {
                    "id": course.id,
                    "title": course.title,
                    "description": course.description,
                    "thumbnail": course.thumbnail,
                    "language": course.language,
                    "duration": course.duration,
                    "category": course.category,
                    "level": course.level,
                    "instructor": self._instructor_name(course),
                }
                for course in courses
            ],
            "page": page,
            "limit": limit,
            "total": total,
            "has_next": page * limit < total,
        }

    def course_details(self, student_id, course_id):
        course = self.repository.get_course_content(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        enrollment = self.repository.get_course_enrollment(course_id, student_id)
        if not enrollment:
            if course.status != CourseStatus.PUBLISHED:
                raise HTTPException(status_code=404, detail="Course not found")
            total, completed, percentage = (0, 0, 0)
            completed_lesson_ids = set()
        else:
            total, completed, percentage = self._progress_summary(enrollment)
            completed_lesson_ids = {progress.lesson_id for progress in self.repository.get_progress_for_enrollment(enrollment.id) if progress.is_completed}
        return {"id": course.id, "title": course.title, "description": course.description,
                "thumbnail": course.thumbnail, "instructor": self._instructor_name(course),
                "category": course.category, "level": course.level, "language": course.language,
                "duration": course.duration, "objectives": course.objectives, "is_enrolled": bool(enrollment),
                "completion_percentage": percentage, "completed_lessons": completed, "total_lessons": total,
                "modules": [{"id": module.id, "title": module.title, "description": module.description,
                             "order_index": module.order_index,
                             "lessons": [{"id": lesson.id, "title": lesson.title, "content": lesson.content if enrollment else "",
                                          "duration_minutes": lesson.duration_minutes, "order_index": lesson.order_index,
                                          "is_completed": lesson.id in completed_lesson_ids,
                                          "resources": [{"id": resource.id, "title": resource.title, "url": resource.url,
                                                         "resource_type": resource.resource_type, "description": resource.description}
                                                        for resource in lesson.resources] if enrollment else []}
                                         for lesson in sorted(module.lessons, key=lambda item: item.order_index)]}
                            for module in sorted(course.modules, key=lambda item: item.order_index)],
                "quizzes": [{"id": quiz.id, "title": quiz.title, "description": quiz.description} for quiz in course.quizzes]}

    def lesson_details(self, student_id, lesson_id):
        lesson = self.repository.get_lesson_with_content(lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        enrollment = self._get_enrollment_or_403(student_id, lesson.module.course_id)
        progress = self.repository.get_lesson_progress(enrollment.id, lesson_id)
        video = self.repository.get_lesson_video(lesson_id)
        live_sessions = self.repository.get_lesson_live_sessions(lesson_id)
        return {"id": lesson.id, "course_id": lesson.module.course_id, "title": lesson.title, "content": lesson.content,
                "duration_minutes": lesson.duration_minutes, "completion_percent": progress.completion_percent if progress else 0,
                "is_completed": progress.is_completed if progress else False,
                "resources": [{"id": resource.id, "title": resource.title, "url": resource.url,
                               "resource_type": resource.resource_type, "description": resource.description}
                              for resource in lesson.resources],
                "video": {"id": video.id, "title": video.title, "description": video.description,
                          "video_url": video.video_url, "duration_seconds": video.duration_seconds,
                          "thumbnail_url": video.thumbnail_url, "created_at": video.created_at, "updated_at": video.updated_at} if video else None,
                "live_sessions": [{"id": s.id, "title": s.title, "description": s.description,
                                   "scheduled_start": s.scheduled_start, "scheduled_end": s.scheduled_end,
                                   "meeting_url": s.meeting_url, "status": s.status, "recording_url": s.recording_url,
                                   "created_at": s.created_at, "updated_at": s.updated_at}
                                  for s in live_sessions]}

    def complete_lesson(self, student_id, lesson_id):
        lesson = self.repository.get_lesson_with_content(lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        enrollment = self._get_enrollment_or_403(student_id, lesson.module.course_id)
        existing_progress = self.repository.get_lesson_progress(enrollment.id, lesson_id)
        was_completed = bool(existing_progress and existing_progress.is_completed)
        progress = self.repository.complete_lesson(enrollment.id, lesson_id)
        _, completed, percentage = self._progress_summary(enrollment)
        if not was_completed:
            self._notify(student_id, "Lesson completed", f"You completed {lesson.title}.")
        certificate_issued = self.issue_certificate_if_eligible(student_id, enrollment.course_id)
        return {"lesson_id": lesson_id, "is_completed": progress.is_completed,
                "course_completed_lessons": completed, "course_completion_percentage": percentage,
                "certificate_issued": certificate_issued}

    def issue_certificate_if_eligible(self, student_id, course_id):
        """Require completed lessons and a final score strictly above 80 on each quiz."""
        from app.models.quiz import Quiz
        from app.models.quiz_result import QuizResult
        enrollment = self.repository.get_course_enrollment(course_id, student_id)
        if not enrollment:
            return False
        total, completed, _ = self._progress_summary(enrollment)
        if not total or completed != total:
            return False
        quiz_ids = {qid for (qid,) in self.repository.db.query(Quiz.id).filter(Quiz.course_id == course_id)}
        if not quiz_ids:
            return False
        results = {result.quiz_id: result.score for result in self.repository.db.query(QuizResult).filter(
            QuizResult.student_id == student_id, QuizResult.course_id == course_id,
            QuizResult.quiz_id.in_(quiz_ids))}
        if set(results) != quiz_ids or not all(80 < score <= 100 for score in results.values()):
            return False
        if self.repository.get_certificate_for_course_student(course_id, student_id):
            return False
        certificate = self.repository.create_certificate(student_id, course_id)
        if certificate:
            self._notify(student_id, "Certificate issued", "You completed all lessons and scored above 80% on every course quiz.")
            return True
        return False

    def quiz_details(self, student_id, quiz_id):
        quiz = self.repository.get_quiz_with_content(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        self._get_enrollment_or_403(student_id, quiz.course_id)
        from app.services.quiz_attempt_service import QuizAttemptService
        attempts = QuizAttemptService(self.repository.db)
        attempt = attempts.find(student_id, quiz_id)
        legacy = self.repository.get_quiz_result(student_id, quiz_id)
        result = attempts.response(attempt) if attempt else ({"status": "graded", "quiz_result_id": legacy.id, "score": legacy.score, "percentage": legacy.score, "passed": legacy.score >= 50, "correct_answers": [], "wrong_answers": [], "responses": [], "pending_questions": 0} if legacy else None)
        return {"id": quiz.id, "title": quiz.title, "description": quiz.description, "result": result,
                "questions": [{"id": question.id, "text": question.text, "order_index": question.order_index, "question_type": question.question_type, "points": question.points,
                               "answers": [{"id": answer.id, "text": answer.text} for answer in question.answers]}
                              for question in sorted(quiz.questions, key=lambda item: item.order_index)]}

    def submit_quiz(self, student_id, quiz_id, selections):
        quiz = self.repository.get_quiz_with_content(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        self._get_enrollment_or_403(student_id, quiz.course_id)
        from app.services.quiz_attempt_service import QuizAttemptService
        result = QuizAttemptService(self.repository.db).submit(student_id, quiz, selections)
        self.issue_certificate_if_eligible(student_id, quiz.course_id)
        self._notify(student_id, "Quiz submitted", "Your written answers await teacher review." if result["status"] == "pending_review" else f"You completed {quiz.title} with a score of {result['score']}%.")
        return result

    def progress(self, student_id):
        result = []
        for enrollment in self.repository.get_student_enrollments(student_id):
            total, completed, percentage = self._progress_summary(enrollment)
            result.append({"course_id": enrollment.course_id, "title": enrollment.course.title,
                           "percentage": percentage, "completed_lessons": completed, "remaining_lessons": total - completed})
        return result

    @staticmethod
    def _certificate_response(certificate):
        return {"id": certificate.id, "course_id": certificate.course_id,
                "course_title": certificate.course.title, "issued_at": certificate.issued_at,
                "certificate_url": certificate.certificate_url}

    def list_certificates(self, student_id):
        return [self._certificate_response(certificate) for certificate in self.repository.get_student_certificates(student_id)]

    def get_certificate(self, student_id, certificate_id):
        certificate = self.repository.get_certificate_for_student(certificate_id, student_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        return self._certificate_response(certificate)

    def list_course_certificates(self, instructor_id, course_id):
        self._get_owned_course(instructor_id, course_id)
        return [self._certificate_response(certificate) for certificate in self.repository.get_course_certificates(course_id)]
