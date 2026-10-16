from fastapi import HTTPException

from app.models.course import Course
from app.models.user import InstructorStatus, UserRole
from app.repositories.course_instructor_repository import CourseInstructorRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import UserRepository


class CourseInstructorService:
    def __init__(
        self,
        repository: CourseInstructorRepository,
        course_repository: CourseRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.course_repository = course_repository
        self.user_repository = user_repository

    def assign_instructor(self, course_id, instructor_id):
        course = self.course_repository.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        instructor = self.user_repository.get_by_id(instructor_id)
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")

        if instructor.role != UserRole.INSTRUCTOR:
            raise HTTPException(status_code=422, detail="User is not an instructor")

        if instructor.instructor_status != InstructorStatus.ACTIVE:
            raise HTTPException(status_code=422, detail="Instructor is not active")

        if self.repository.is_instructor_assigned(course_id, instructor_id):
            raise HTTPException(status_code=409, detail="Instructor is already assigned to this course")

        return self.repository.assign_instructor(course_id, instructor_id)

    def remove_instructor(self, course_id, instructor_id):
        course = self.course_repository.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        instructor = self.user_repository.get_by_id(instructor_id)
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")

        if not self.repository.is_instructor_assigned(course_id, instructor_id):
            raise HTTPException(status_code=404, detail="Instructor is not assigned to this course")

        self.repository.remove_instructor(course_id, instructor_id)
        return {"message": "Instructor removed from course"}

    def get_course_instructors(self, course_id):
        course = self.course_repository.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        return self.repository.get_course_instructors(course_id)

    def get_instructor_courses(self, instructor_id):
        instructor = self.user_repository.get_by_id(instructor_id)
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")

        return self.repository.get_instructor_courses(instructor_id)
