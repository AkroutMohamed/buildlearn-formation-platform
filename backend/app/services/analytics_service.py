from fastapi import HTTPException

from app.models.course_instructor import CourseInstructor
from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    def get_course_analytics(self, instructor_id, course_id):
        course = self.repository.get_course_with_enrollments(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        assignment = self.repository.db.query(CourseInstructor).filter(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == instructor_id,
        ).first()
        if assignment is None:
            raise HTTPException(status_code=403, detail="You are not assigned to this course")

        total_lessons = self.repository.count_course_lessons(course_id)
        completed_by_student = [sum(progress.is_completed for progress in enrollment.progress) for enrollment in course.enrollments]
        percentages = [round((completed / total_lessons) * 100, 2) if total_lessons else 0.0 for completed in completed_by_student]
        total_students = len(course.enrollments)

        return {
            "total_students": total_students,
            "completed_students": sum(percentage == 100 for percentage in percentages),
            "completion_rate": round((sum(percentage == 100 for percentage in percentages) / total_students) * 100, 2) if total_students else 0.0,
            "average_quiz_score": round(float(self.repository.average_quiz_score(course_id) or 0), 2),
            "total_lessons": total_lessons,
            "completed_lessons": sum(completed_by_student),
            "average_progress": round(sum(percentages) / total_students, 2) if total_students else 0.0,
        }
