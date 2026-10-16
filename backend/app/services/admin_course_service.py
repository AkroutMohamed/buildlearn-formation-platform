from fastapi import HTTPException

from app.models.course import Course, CourseStatus
from app.models.course_instructor import CourseInstructor
from app.models.user import InstructorStatus, UserRole
from app.repositories.course_instructor_repository import CourseInstructorRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import UserRepository
from app.schemas.course import CourseCreate, CourseUpdate


class AdminCourseService:
    def __init__(
        self,
        course_repository: CourseRepository,
        course_instructor_repository: CourseInstructorRepository,
        user_repository: UserRepository,
    ):
        self.course_repository = course_repository
        self.course_instructor_repository = course_instructor_repository
        self.user_repository = user_repository

    def list_courses(self):
        return self.course_repository.get_all()

    def get_course(self, course_id):
        course = self.course_repository.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")
        return course

    def create_course(self, course_data: CourseCreate, instructor_id: UUID):
        course = Course(
            instructor_id=instructor_id,
            title=course_data.title.strip(),
            description=course_data.description.strip(),
            objectives=course_data.objectives,
            thumbnail=course_data.thumbnail,
            language=course_data.language,
            duration=course_data.duration,
            category=course_data.category,
            level=course_data.level,
            product_id=course_data.product_id,
            status=CourseStatus.DRAFT,
        )
        return self.course_repository.create(course)

    def update_course(self, course_id, course_data: CourseUpdate):
        course = self.get_course(course_id)
        update_data = course_data.model_dump(exclude_unset=True)

        if "title" in update_data and len(str(update_data["title"]).strip()) < 3:
            raise HTTPException(status_code=422, detail="Course title must contain at least 3 characters.")

        if "description" in update_data and len(str(update_data["description"]).strip()) < 10:
            raise HTTPException(status_code=422, detail="Course description must contain at least 10 characters.")

        if "duration" in update_data and update_data["duration"] < 0:
            raise HTTPException(status_code=422, detail="Duration cannot be negative.")

        for field, value in update_data.items():
            setattr(course, field, value)

        return self.course_repository.update(course)

    def delete_course(self, course_id):
        course = self.get_course(course_id)
        self.course_repository.delete(course)

    def publish_course(self, course_id):
        course = self.get_course(course_id)
        if not course.title:
            raise HTTPException(status_code=422, detail="Course title is required.")
        if not course.description:
            raise HTTPException(status_code=422, detail="Course description is required.")
        if not course.category:
            raise HTTPException(status_code=422, detail="Course category is required.")
        if not course.level:
            raise HTTPException(status_code=422, detail="Course level is required.")

        course.status = CourseStatus.PUBLISHED
        return self.course_repository.update(course)

    def unpublish_course(self, course_id):
        course = self.get_course(course_id)
        course.status = CourseStatus.DRAFT
        return self.course_repository.update(course)

    def assign_instructor(self, course_id, instructor_id):
        course = self.get_course(course_id)
        instructor = self.user_repository.get_by_id(instructor_id)
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")
        if instructor.role != UserRole.INSTRUCTOR:
            raise HTTPException(status_code=422, detail="User is not an instructor")
        if instructor.instructor_status != InstructorStatus.ACTIVE:
            raise HTTPException(status_code=422, detail="Instructor is not active")
        if self.course_instructor_repository.is_instructor_assigned(course_id, instructor_id):
            raise HTTPException(status_code=409, detail="Instructor is already assigned to this course")
        return self.course_instructor_repository.assign_instructor(course_id, instructor_id)

    def unassign_instructor(self, course_id, instructor_id):
        course = self.get_course(course_id)
        instructor = self.user_repository.get_by_id(instructor_id)
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")
        if not self.course_instructor_repository.is_instructor_assigned(course_id, instructor_id):
            raise HTTPException(status_code=404, detail="Instructor is not assigned to this course")
        self.course_instructor_repository.remove_instructor(course_id, instructor_id)
        return {"message": "Instructor removed from course"}

    def get_course_instructors(self, course_id):
        course = self.get_course(course_id)
        assignments = self.course_instructor_repository.get_course_instructors(course_id)
        instructor_ids = [a.instructor_id for a in assignments]
        if not instructor_ids:
            return []
        return self.user_repository.get_by_ids(instructor_ids)
