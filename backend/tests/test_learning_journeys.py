"""User-facing API journeys against an isolated DB and temporary uploads."""
from pathlib import Path
from uuid import uuid4
import pytest
from fastapi import FastAPI, Header
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import app.models
from app.database import Base, get_db
from app.models.user import User, UserRole, InstructorStatus
from app.models.product import Product
from app.models.product_instructor import ProductInstructor
from app.middleware.auth_middleware import get_current_user
from app.routers.instructor import router as instructor
from app.routers.student import router as student
from app.routers.public import router as public
from app.config import settings
from app.models.quiz_result import QuizResult


@pytest.fixture
def journey(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, 'upload_dir', str(tmp_path))
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    users = {}
    for role in ('instructor', 'student', 'outsider'):
        users[role] = User(id=uuid4(), first_name='Journey', last_name=role, email=f'{role}@journey.test', hashed_password='not-used', role=UserRole.INSTRUCTOR if role == 'instructor' else UserRole.STUDENT, instructor_status=InstructorStatus.ACTIVE, is_active=True)
        db.add(users[role])
    product = Product(id=uuid4(), name='Journey product', description='Isolated test product')
    db.add(product); db.flush()
    db.add(ProductInstructor(product_id=product.id, instructor_id=users['instructor'].id)); db.commit()
    app = FastAPI()
    for router in (instructor, student, public): app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    def current(x_test_role: str = Header(default='instructor')):
        return users[x_test_role]
    app.dependency_overrides[get_current_user] = current
    client = TestClient(app)
    def ok(method, path, role='instructor', **kwargs):
        response = client.request(method, path, headers={'x-test-role': role}, **kwargs)
        assert response.status_code < 300, response.text
        return response.json()
    course = ok('POST', f'/instructor/products/{product.id}/courses', json=dict(title='Journey course', description='Realistic isolated course content', category='Outillage', level='Beginner', language='French', duration=20))
    base = f"/instructor/courses/{course['id']}"
    module = ok('POST', base + '/modules', json=dict(title='Getting started', order_index=0))
    lesson_path = base + f"/modules/{module['id']}/lessons"
    lesson = ok('POST', lesson_path, json=dict(title='Safety lesson', content='Read the safety instructions.', duration_minutes=10, order_index=0, is_published=True))
    ok('PATCH', base + '/publish')
    yield dict(ok=ok, client=client, db=db, course=course, base=base, lesson=lesson, lesson_path=lesson_path, uploads=tmp_path)
    client.close(); db.close(); engine.dispose()


@pytest.fixture
def mixed_quiz(journey):
    j = journey; ok = j['ok']; cid = j['course']['id']
    quiz = ok('POST', j['base'] + '/quizzes', json={'title': 'Mixed assessment'})
    path = j['base'] + '/quizzes/' + quiz['id']
    yes = ok('POST', path + '/questions', json=dict(text='Wear gloves?', question_type='yes_no', correct_yes=False, points=1))
    written = ok('POST', path + '/questions', json=dict(text='Explain preparation.', question_type='written', points=3, order_index=1))
    answers = ok('GET', path + '/questions/' + yes['id'] + '/answers')
    assert len(answers) == 2
    assert next(a for a in answers if a['is_correct'])['text'] == 'No'
    ok('POST', f'/student/courses/{cid}/enroll', role='student')
    j.update(quiz=quiz, quiz_path=path, yes=yes, written=written, selections=[dict(question_id=yes['id'], answer_id=next(a for a in answers if a['text'] == 'No')['id']), dict(question_id=written['id'], text_answer='Clean and dry the surface.')])
    return j


def submit_mixed(j):
    return j['ok']('POST', f"/student/quizzes/{j['quiz']['id']}/submit", role='student', json={'answers': j['selections']})


def test_mixed_submission_review_and_persisted_feedback(mixed_quiz):
    j = mixed_quiz; ok = j['ok']
    before = ok('GET', f"/student/quizzes/{j['quiz']['id']}", role='student')
    assert before['result'] is None
    assert all('is_correct' not in a for q in before['questions'] for a in q['answers'])
    result = submit_mixed(j)
    assert result['status'] == 'pending_review' and result['percentage'] is None and result['passed'] is None
    assert result['quiz_result_id'] is None and result['pending_questions'] == 1
    assert j['db'].query(QuizResult).count() == 0
    assert result['responses'][0]['correct_answer'] == 'No'
    queue = ok('GET', j['base'] + '/quiz-submissions')
    assert queue[0]['student_name'] == 'Journey student'
    review_path = j['base'] + f"/quiz-submissions/{result['attempt_id']}/review"
    ok('PUT', j['quiz_path'] + f"/questions/{j['written']['id']}", json={'text': 'Changed question', 'points': 50})
    final = ok('POST', review_path, json={'grades': [dict(question_id=j['written']['id'], points_awarded=2, feedback='Mention primer too.')]})
    assert final['percentage'] == 75 and final['passed'] is True
    assert final['responses'][1]['question_text'] == 'Explain preparation.'
    assert final['responses'][1]['points'] == 3
    saved = ok('GET', f"/student/quizzes/{j['quiz']['id']}", role='student')['result']
    assert saved == final and saved['responses'][1]['feedback'] == 'Mention primer too.'
    assert j['db'].query(QuizResult).count() == 1
    assert j['client'].post(review_path, json={'grades': [dict(question_id=j['written']['id'], points_awarded=3)]}).status_code == 409
    assert j['client'].post(f"/student/quizzes/{j['quiz']['id']}/submit", headers={'x-test-role':'student'}, json={'answers':j['selections']}).status_code == 409


@pytest.mark.parametrize('bad', ['', '   ', None])
def test_written_answer_must_be_nonempty(mixed_quiz, bad):
    j = mixed_quiz; j['selections'][1]['text_answer'] = bad
    response = j['client'].post(f"/student/quizzes/{j['quiz']['id']}/submit", headers={'x-test-role':'student'}, json={'answers':j['selections']})
    assert response.status_code == 422


@pytest.mark.parametrize('case', ['missing', 'too_high', 'negative', 'duplicate', 'wrong_question', 'nonfinite'])
def test_invalid_teacher_grades_do_not_publish(mixed_quiz, case):
    j = mixed_quiz; result = submit_mixed(j)
    grade = dict(question_id=j['written']['id'], points_awarded=2); rows = [grade]
    if case == 'missing': rows = []
    if case == 'too_high': grade['points_awarded'] = 4
    if case == 'negative': grade['points_awarded'] = -1
    if case == 'duplicate': rows = [grade, grade]
    if case == 'wrong_question': grade['question_id'] = j['yes']['id']
    if case == 'nonfinite': grade['points_awarded'] = 'Infinity'
    response = j['client'].post(j['base'] + f"/quiz-submissions/{result['attempt_id']}/review", json={'grades':rows})
    assert response.status_code == 422
    assert j['ok']('GET', f"/student/quizzes/{j['quiz']['id']}", role='student')['result']['status'] == 'pending_review'


def test_submission_and_grading_authorization(mixed_quiz):
    j = mixed_quiz; result = submit_mixed(j)
    for role in ('student', 'outsider'):
        assert j['client'].get(j['base'] + '/quiz-submissions', headers={'x-test-role':role}).status_code == 403
        assert j['client'].post(j['base'] + f"/quiz-submissions/{result['attempt_id']}/review", headers={'x-test-role':role}, json={'grades':[dict(question_id=j['written']['id'], points_awarded=1)]}).status_code == 403
    assert j['client'].get(f"/student/quizzes/{j['quiz']['id']}", headers={'x-test-role':'outsider'}).status_code == 403
    outsider = j['db'].query(User).filter_by(email='outsider@journey.test').one()
    outsider.role = UserRole.INSTRUCTOR; j['db'].commit()
    assert j['client'].get(j['base'] + '/quiz-submissions', headers={'x-test-role':'outsider'}).status_code == 403


def test_automatic_wrong_answer_review_survives_reload(mixed_quiz):
    j = mixed_quiz
    quiz = j['ok']('POST', j['base'] + '/quizzes', json={'title':'Automatic'})
    path = j['base'] + '/quizzes/' + quiz['id']
    q = j['ok']('POST', path + '/questions', json={'text':'Use gloves?', 'question_type':'yes_no', 'correct_yes':True})
    answers = j['ok']('GET', path + f"/questions/{q['id']}/answers")
    wrong = next(a for a in answers if a['text'] == 'No')
    result = j['ok']('POST', f"/student/quizzes/{quiz['id']}/submit", role='student', json={'answers':[dict(question_id=q['id'], answer_id=wrong['id'])]})
    assert result['status'] == 'graded' and result['percentage'] == 0
    assert result['responses'][0]['selected_answer'] == 'No'
    assert result['responses'][0]['correct_answer'] == 'Yes'
    assert result['responses'][0]['is_correct'] is False
    assert j['ok']('GET', f"/student/quizzes/{quiz['id']}", role='student')['result'] == result


def test_written_only_and_zero_teacher_grade(mixed_quiz):
    j = mixed_quiz; q = j['ok']('POST', j['base'] + '/quizzes', json={'title':'Written only'})
    question = j['ok']('POST', j['base'] + f"/quizzes/{q['id']}/questions", json={'text':'Explain safety', 'question_type':'written', 'points':2})
    result = j['ok']('POST', f"/student/quizzes/{q['id']}/submit", role='student', json={'answers':[dict(question_id=question['id'], text_answer='My response')]})
    final = j['ok']('POST', j['base'] + f"/quiz-submissions/{result['attempt_id']}/review", json={'grades':[dict(question_id=question['id'], points_awarded=0, feedback='Review the lesson.')]})
    assert final['percentage'] == 0 and final['passed'] is False


def test_wrong_answer_types_duplicates_and_question_type_validation(mixed_quiz):
    j = mixed_quiz; client = j['client']; url = f"/student/quizzes/{j['quiz']['id']}/submit"
    written = j['selections'][1]
    for rows in ([j['selections'][0], written, written], [j['selections'][0], dict(question_id=j['written']['id'], answer_id=j['selections'][0]['answer_id'])], [dict(question_id=j['yes']['id'], text_answer='Yes'), written]):
        assert client.post(url, headers={'x-test-role':'student'}, json={'answers':rows}).status_code == 422
    assert client.post(j['quiz_path'] + '/questions', json={'text':'Bad', 'question_type':'unsupported'}).status_code == 422
    assert client.post(j['quiz_path'] + f"/questions/{j['written']['id']}/answers", json={'text':'Not an option', 'is_correct':True}).status_code == 422


def test_catalog_reset_preserves_accounts_and_chats_and_seeds_real_courses(journey):
    from scripts.reset_learning_catalog import load_manifest, reset_and_seed
    from app.models.conversation import Conversation
    from app.models.message import Message
    from app.models.course import Course
    from app.models.resource import Resource
    from app.models.product import Product
    from app.models.question import Question
    from app.models.course_instructor import CourseInstructor
    from app.models.product_instructor import ProductInstructor
    db = journey['db']
    instructor = db.query(User).filter_by(email='instructor@journey.test').one()
    student = db.query(User).filter_by(email='student@journey.test').one()
    admin = db.query(User).filter_by(email='outsider@journey.test').one()
    instructor.email = 'mo@gmail.com'; student.email = 'akrout@gmail.com'
    admin.email = 'admin@buildlearn.local'; admin.role = UserRole.ADMIN
    extra = User(first_name='Demo', last_name='User', email='demo@journey.test', hashed_password='demo')
    db.add(extra); db.flush()
    keep_chat = Conversation(user_id=student.id, title='Keep my chat')
    delete_chat = Conversation(user_id=extra.id, title='Demo chat')
    db.add_all([keep_chat, delete_chat]); db.flush()
    db.add_all([Message(conversation_id=keep_chat.id, role='user', content='My question'), Message(conversation_id=delete_chat.id, role='user', content='Demo question')])
    db.commit()
    before = {u.email: (u.id, u.hashed_password, u.role) for u in (instructor, student, admin)}
    manifest = load_manifest()
    reset_and_seed(db, manifest, ['/uploads/source-1.pdf', '/uploads/source-2.pdf', '/uploads/source-3.pdf'])
    db.commit()
    assert {u.email: (u.id, u.hashed_password, u.role) for u in db.query(User)} == before
    assert db.query(Conversation).count() == 1 and db.query(Message).count() == 1
    assert db.query(Message).one().content == 'My question'
    assert db.query(Product).count() == 3 and db.query(Course).count() == 3
    assert db.query(Resource).count() == 3 and db.query(Question).count() == 9
    assert db.query(CourseInstructor).count() == 3 and db.query(ProductInstructor).count() == 3
    assert all(c.duration == sum(l.duration_minutes for m in c.modules for l in m.lessons) for c in db.query(Course))


def test_catalog_reset_refuses_missing_accounts_before_any_deletion(journey):
    from scripts.reset_learning_catalog import load_manifest, reset_and_seed
    from app.models.course import Course
    db = journey['db']; before = db.query(Course).count()
    with pytest.raises(ValueError, match='three requested accounts'):
        reset_and_seed(db, load_manifest(), ['/uploads/source.pdf'] * 3)
    assert db.query(Course).count() == before


@pytest.mark.parametrize('scores,expected', [([100, 81], True), ([100, 80], False), ([100, 79], False), ([100, None], False), ([], False)])
def test_certificate_requires_every_quiz_strictly_above_80(journey, scores, expected):
    from app.models.quiz import Quiz
    j = journey; ok = j['ok']; cid = j['course']['id']
    ok('POST', f'/student/courses/{cid}/enroll', role='student')
    student = j['db'].query(User).filter_by(email='student@journey.test').one()
    for index, score in enumerate(scores):
        quiz = Quiz(course_id=cid, title=f'Assessment {index}')
        # ORM UUID columns require native UUID values.
        from uuid import UUID
        quiz.course_id = UUID(cid)
        j['db'].add(quiz); j['db'].flush()
        if score is not None:
            j['db'].add(QuizResult(student_id=student.id, course_id=quiz.course_id, quiz_id=quiz.id, score=score))
    j['db'].commit()
    result = ok('POST', f"/student/lessons/{j['lesson']['id']}/complete", role='student')
    assert result['certificate_issued'] is expected
    assert len(ok('GET', '/student/certificates', role='student')) == int(expected)
    repeated = ok('POST', f"/student/lessons/{j['lesson']['id']}/complete", role='student')
    assert repeated['certificate_issued'] is False


def test_certificate_issued_after_last_automatic_quiz(journey):
    j = journey; ok = j['ok']; cid = j['course']['id']
    quiz = ok('POST', j['base'] + '/quizzes', json={'title': 'Automatic assessment'})
    question = ok('POST', j['base'] + f"/quizzes/{quiz['id']}/questions", json={'text': 'Follow instructions?', 'question_type': 'yes_no'})
    answer = next(a for a in ok('GET', j['base'] + f"/quizzes/{quiz['id']}/questions/{question['id']}/answers") if a['is_correct'])
    ok('POST', f'/student/courses/{cid}/enroll', role='student')
    result = ok('POST', f"/student/lessons/{j['lesson']['id']}/complete", role='student')
    assert result['certificate_issued'] is False
    assert ok('GET', '/student/certificates', role='student') == []
    ok('POST', f"/student/quizzes/{quiz['id']}/submit", role='student', json={'answers': [dict(question_id=question['id'], answer_id=answer['id'])]})
    assert len(ok('GET', '/student/certificates', role='student')) == 1


@pytest.mark.parametrize('written_points,eligible', [(3, True), (2.25, True), (2.2, False), (2, False)])
def test_teacher_grading_controls_certificate_eligibility(mixed_quiz, written_points, eligible):
    j = mixed_quiz; ok = j['ok']
    completed = ok('POST', f"/student/lessons/{j['lesson']['id']}/complete", role='student')
    assert completed['certificate_issued'] is False
    result = submit_mixed(j)
    assert ok('GET', '/student/certificates', role='student') == []
    ok('POST', j['base'] + f"/quiz-submissions/{result['attempt_id']}/review", json={'grades': [dict(question_id=j['written']['id'], points_awarded=written_points)]})
    assert len(ok('GET', '/student/certificates', role='student')) == int(eligible)


def test_course_authoring_enrollment_and_completion(journey):
    j = journey; ok = j['ok']; cid = j['course']['id']; lid = j['lesson']['id']
    detail = ok('GET', j['base'])
    assert detail['modules'][0]['lesson_count'] == 1
    ok('PUT', j['lesson_path'] + '/' + lid, json={'content': 'Updated learning instructions.'})
    catalog = ok('GET', '/public/courses', role='student')
    assert any(c['id'] == cid for c in catalog['items'])
    ok('POST', f'/student/courses/{cid}/enroll', role='student')
    lesson = ok('GET', f'/student/lessons/{lid}', role='student')
    assert lesson['content'] == 'Updated learning instructions.'
    quiz = ok('POST', j['base'] + '/quizzes', json={'title': 'Required course assessment'})
    question = ok('POST', j['base'] + f"/quizzes/{quiz['id']}/questions", json={'text': 'Follow safety instructions?', 'question_type': 'yes_no'})
    answer = next(a for a in ok('GET', j['base'] + f"/quizzes/{quiz['id']}/questions/{question['id']}/answers") if a['is_correct'])
    ok('POST', f"/student/quizzes/{quiz['id']}/submit", role='student', json={'answers': [dict(question_id=question['id'], answer_id=answer['id'])]})
    assert ok('GET', '/student/certificates', role='student') == []
    result = ok('POST', f'/student/lessons/{lid}/complete', role='student')
    assert result['course_completion_percentage'] == 100
    assert result['certificate_issued'] is True
    repeat = ok('POST', f'/student/lessons/{lid}/complete', role='student')
    assert repeat['certificate_issued'] is False
    assert len(ok('GET', '/student/certificates', role='student')) == 1


def test_multiple_uploads_student_visibility_and_video_deletion(journey):
    j = journey; ok = j['ok']; lid = j['lesson']['id']; cid = j['course']['id']
    path = j['base'] + f'/lessons/{lid}'
    resources = [ok('POST', path + '/resources', data={'title': name}, files={'file': (name, b'%PDF-1.4 sample', 'application/pdf')}) for name in ('guide.pdf', 'worksheet.pdf')]
    videos = [ok('POST', path + '/videos/upload', data={'title': name}, files={'file': (name, b'\x00\x00\x00\x18ftypisomtest', 'video/mp4')}) for name in ('intro.mp4', 'demo.mp4')]
    ok('POST', f'/student/courses/{cid}/enroll', role='student')
    lesson = ok('GET', f'/student/lessons/{lid}', role='student')
    assert len(lesson['resources']) == 4
    assert len({r['url'] for r in lesson['resources']}) == 4
    assert all((j['uploads'] / r['url'].removeprefix('/uploads/')).exists() for r in lesson['resources'])
    ok('DELETE', path + '/resources/' + videos[0]['id'])
    assert not (j['uploads'] / videos[0]['url'].removeprefix('/uploads/')).exists()
    assert (j['uploads'] / videos[1]['url'].removeprefix('/uploads/')).exists()
    assert len(ok('GET', path + '/resources')) == 3


def test_quiz_requires_complete_answers_and_scores_once(journey):
    j = journey; ok = j['ok']; cid = j['course']['id']
    quiz = ok('POST', j['base'] + '/quizzes', json={'title': 'Safety assessment'})
    path = j['base'] + '/quizzes/' + quiz['id']
    selections = []
    for index in range(2):
        question = ok('POST', path + '/questions', json=dict(text=f'Safe step {index}?', question_type='multiple_choice', points=1, order_index=index))
        answer = ok('POST', path + f"/questions/{question['id']}/answers", json={'text': 'Follow the instructions', 'is_correct': True})
        ok('POST', path + f"/questions/{question['id']}/answers", json={'text': 'Ignore the instructions', 'is_correct': False})
        selections.append(dict(question_id=question['id'], answer_id=answer['id']))
    ok('POST', f'/student/courses/{cid}/enroll', role='student')
    fetched = ok('GET', '/student/quizzes/' + quiz['id'], role='student')
    assert all('is_correct' not in answer for question in fetched['questions'] for answer in question['answers'])
    submit = '/student/quizzes/' + quiz['id'] + '/submit'
    incomplete = j['client'].post(submit, headers={'x-test-role': 'student'}, json={'answers': selections[:1]})
    assert incomplete.status_code == 422
    assert 'Not all questions' in incomplete.text
    result = ok('POST', submit, role='student', json={'answers': selections})
    assert result['percentage'] == 100
    assert j['client'].post(submit, headers={'x-test-role': 'student'}, json={'answers': selections}).status_code == 409


def test_unenrolled_student_and_non_instructor_uploads_denied(journey):
    j = journey; lid = j['lesson']['id']
    assert j['client'].get(f'/student/lessons/{lid}', headers={'x-test-role': 'outsider'}).status_code == 403
    response = j['client'].post(j['base'] + f'/lessons/{lid}/videos/upload', headers={'x-test-role': 'student'}, data={'title': 'Not allowed'}, files={'file': ('x.mp4', b'\x00\x00\x00\x18ftypisomtest', 'video/mp4')})
    assert response.status_code == 403
    assert not list(j['uploads'].rglob('*.mp4'))
