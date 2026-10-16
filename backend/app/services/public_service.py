from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.course import Course, CourseStatus
from app.models.module import Module
from app.repositories.course_repository import CourseRepository


class PublicService:
    def __init__(self, course_repository: CourseRepository):
        self.course_repository = course_repository

    def list_published_courses(
        self,
        page: int,
        limit: int,
        search: str | None = None,
        category: str | None = None,
        level: str | None = None,
        language: str | None = None,
    ):
        courses, total = self.course_repository.get_published_courses_page(
            page, limit, search, category, level, language
        )
        return {
            "items": [
                {
                    "id": course.id,
                    "title": course.title,
                    "description": course.description,
                    "thumbnail": course.thumbnail,
                    "language": course.language,
                    "duration": course.duration,
                    "category": course.category.value if course.category else "",
                    "level": course.level.value if course.level else "",
                    "instructor": f"{course.instructor.first_name} {course.instructor.last_name}"
                    if course.instructor
                    else "",
                }
                for course in courses
            ],
            "page": page,
            "limit": limit,
            "total": total,
            "has_next": page * limit < total,
        }

    def get_published_course_details(self, course_id):
        course = self.course_repository.get_published_course_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        modules = []
        for module in sorted(course.modules, key=lambda m: m.order_index):
            lessons = [
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "order_index": lesson.order_index,
                    "duration_minutes": lesson.duration_minutes,
                }
                for lesson in sorted(module.lessons, key=lambda l: l.order_index)
            ]
            modules.append(
                {
                    "id": module.id,
                    "title": module.title,
                    "description": module.description,
                    "order_index": module.order_index,
                    "lessons": lessons,
                }
            )

        quizzes = [
            {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
            }
            for quiz in course.quizzes
        ]

        return {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "thumbnail": course.thumbnail,
            "instructor": f"{course.instructor.first_name} {course.instructor.last_name}"
            if course.instructor
            else "",
            "category": course.category.value if course.category else "",
            "level": course.level.value if course.level else "",
            "language": course.language,
            "duration": course.duration,
            "objectives": course.objectives,
            "modules": modules,
            "quizzes": quizzes,
        }
