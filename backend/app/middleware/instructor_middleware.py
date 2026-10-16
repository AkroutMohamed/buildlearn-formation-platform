from fastapi import HTTPException

from app.models.course_instructor import CourseInstructor
from app.models.user import InstructorStatus


def require_active_instructor(current_user):
    if current_user.role.value != "instructor":
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.instructor_status != InstructorStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Instructor account is not active")
    return current_user


def require_assigned_instructor(current_user, course_id, db):
    if current_user.role.value != "instructor":
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.instructor_status != InstructorStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Instructor account is not active")

    assignment = db.query(CourseInstructor).filter(
        CourseInstructor.course_id == course_id,
        CourseInstructor.instructor_id == current_user.id,
    ).first()
    if assignment is None:
        raise HTTPException(status_code=403, detail="You are not assigned to this course")
    return current_user
