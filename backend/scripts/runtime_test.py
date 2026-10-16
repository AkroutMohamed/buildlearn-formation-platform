"""Runtime smoke test for stabilization fixes (A: auth, B: delete course, C: ownership)."""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.middleware import auth_middleware
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.notification import Notification
from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.models.user import User, UserRole

client = TestClient(app, raise_server_exceptions=False)

_active_session = None


def _fake_current_user(request: Request):
    email = request.headers.get("x-test-user")
    assert email, "missing x-test-user header"
    user = _active_session.query(User).filter(User.email == email).first()
    assert user is not None, f"no test user for {email}"
    return user


app.dependency_overrides[auth_middleware.get_current_user] = _fake_current_user

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), "-", name, detail)


def make_user(role, tag):
    email = f"{tag}-{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        first_name="T", last_name="U", email=email,
        hashed_password="dummy", role=UserRole(role),
    )
    _active_session.add(user)
    _active_session.commit()
    _active_session.refresh(user)
    return user, email


r_admin = client.post("/auth/register", json={
    "first_name": "A", "last_name": "D",
    "email": f"adm-{uuid.uuid4().hex[:8]}@x.com",
    "password": "Password123!", "role": "admin",
})
check("register role=admin -> 422", r_admin.status_code == 422)

with SessionLocal() as db:
    _active_session = db
    admin, admin_email = make_user("admin", "adm")
    instructor1, e1 = make_user("instructor", "inst")
    instructor2, e2 = make_user("instructor", "inst2")
    student1, es = make_user("student", "stu")

    me = client.get("/auth/me", headers={"x-test-user": e1})
    body = me.json()
    check("/auth/me -> 200", me.status_code == 200)
    check("/auth/me no password/hashed_password",
          "password" not in body and "hashed_password" not in body)
    check("/auth/me role == instructor", body.get("role") == "instructor")

    # Step 4B-2: instructors cannot create products
    rc = client.post("/instructor/courses", headers={"x-test-user": e1}, json={
        "title": "No Create Course",
        "description": "instructors cannot create products",
        "objectives": "x", "thumbnail": None, "language": "French",
        "duration": 30, "category": "Étanchéité", "level": "Beginner",
    })
    check("instructor create course -> 403", rc.status_code == 403)

    # Admin creates course, then assign instructor1
    rc_admin = client.post("/admin/courses", headers={"x-test-user": admin_email}, json={
        "title": "Delete Me Course",
        "description": "has children, will be deleted",
        "objectives": "x", "thumbnail": None, "language": "French",
        "duration": 30, "category": "Étanchéité", "level": "Beginner",
    })
    check("admin create course -> 200/201", rc_admin.status_code in (200, 201), f"status={rc_admin.status_code} body={rc_admin.text[:200]}")
    cid = rc_admin.json()["id"]

    from app.repositories.course_instructor_repository import CourseInstructorRepository
    from app.repositories.user_repository import UserRepository
    from app.repositories.course_repository import CourseRepository
    from app.services.course_instructor_service import CourseInstructorService

    repo = CourseInstructorRepository(db)
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    service = CourseInstructorService(repo, course_repo, user_repo)
    repo.assign_instructor(cid, instructor1.id)

    rm = client.post(f"/instructor/courses/{cid}/modules", headers={"x-test-user": e1},
                     json={"title": "Module A", "description": "d", "order_index": 0})
    check("create module -> 200/201", rm.status_code in (200, 201))

    rp = client.patch(f"/admin/courses/{cid}/publish", headers={"x-test-user": admin_email})
    check("publish course for enrollment -> 200", rp.status_code == 200, f"status={rp.status_code}")

    re_ = client.post(f"/student/courses/{cid}/enroll", headers={"x-test-user": es})
    check("student enroll -> 201", re_.status_code == 201)

    rd = client.delete(f"/instructor/courses/{cid}", headers={"x-test-user": e1})
    check("DELETE assigned course w/ children -> 200 (not 500)",
          rd.status_code == 200 and rd.json().get("message") == "Course deleted successfully")
    check("course row removed after delete",
          db.query(Course).filter(Course.id == cid).first() is None)
    check("enrollment rows removed after delete",
          db.query(Enrollment).filter(Enrollment.course_id == cid).first() is None)

    # C. ownership: another instructor cannot delete a peer's course
    rc2_admin = client.post("/admin/courses", headers={"x-test-user": admin_email}, json={
        "title": "Ownership Course", "description": "ownership test",
        "objectives": None, "thumbnail": None, "language": "French",
        "duration": 20, "category": "Outillage", "level": "Intermediate",
    })
    check("admin create 2nd course -> 200/201", rc2_admin.status_code in (200, 201))
    cid2 = rc2_admin.json()["id"]

    repo.assign_instructor(cid2, instructor1.id)

    rf = client.delete(f"/instructor/courses/{cid2}", headers={"x-test-user": e2})
    check("DELETE peer's course -> 403 (not assigned)", rf.status_code == 403)

    # QuizResult cascade tests
    quiz = Quiz(course_id=cid2, title="Quiz A", description="test quiz")
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    quiz_result = QuizResult(student_id=student1.id, course_id=cid2, quiz_id=quiz.id, score=100.0, correct_answers=1, total_questions=1)
    db.add(quiz_result)
    db.commit()
    db.refresh(quiz_result)

    check("quiz result created", db.query(QuizResult).filter(QuizResult.id == quiz_result.id).first() is not None)

    rd_quiz = client.delete(f"/instructor/courses/{cid2}/quizzes/{quiz.id}", headers={"x-test-user": e1})
    check("DELETE quiz -> 200", rd_quiz.status_code == 200)
    check("quiz row removed", db.query(Quiz).filter(Quiz.id == quiz.id).first() is None)
    check("quiz result removed after quiz delete", db.query(QuizResult).filter(QuizResult.id == quiz_result.id).first() is None)

    # Recreate quiz and result for course-delete cascade test
    quiz2 = Quiz(course_id=cid2, title="Quiz B", description="test quiz 2")
    db.add(quiz2)
    db.commit()
    db.refresh(quiz2)
    quiz_result2 = QuizResult(student_id=student1.id, course_id=cid2, quiz_id=quiz2.id, score=50.0, correct_answers=0, total_questions=1)
    db.add(quiz_result2)
    db.commit()
    quiz_result2_id = quiz_result2.id

    rd_course = client.delete(f"/instructor/courses/{cid2}", headers={"x-test-user": e1})
    check("DELETE course with quiz results -> 200", rd_course.status_code == 200)
    check("course row removed", db.query(Course).filter(Course.id == cid2).first() is None)
    check("quiz result removed after course delete", db.query(QuizResult).filter(QuizResult.id == quiz_result2_id).first() is None)

    # cleanup: remove notifications (and any quiz results) that reference these
    # users before deleting the users themselves (FK has no ON DELETE CASCADE).
    uids = [instructor1.id, instructor2.id, student1.id, admin.id]
    db.query(QuizResult).filter(QuizResult.student_id.in_(uids)).delete(synchronize_session=False)
    db.query(Notification).filter(Notification.user_id.in_(uids)).delete(synchronize_session=False)
    db.delete(instructor1)
    db.delete(instructor2)
    db.delete(student1)
    db.delete(admin)
    db.commit()
    print("cleanup done")

failed = [n for n, ok in results if not ok]
print("\n=== SUMMARY ===")
print(f"{len(results) - len(failed)}/{len(results)} passed")
if failed:
    print("FAILED:", failed)
    sys.exit(1)
print("ALL CHECKS PASSED")
