from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_result import QuizResult
from app.models.quiz import Quiz
from app.models.user import User

class QuizAttemptService:
    def __init__(self, db):
        self.db = db

    def find(self, student_id, quiz_id):
        return self.db.query(QuizAttempt).filter_by(student_id=student_id, quiz_id=quiz_id).first()

    def response(self, attempt):
        rows = attempt.responses
        graded = attempt.status == "graded"
        score = sum(r["points_awarded"] or 0 for r in rows) / (sum(r["points"] for r in rows) or 1) * 100 if graded else None
        result = self.db.query(QuizResult).filter_by(student_id=attempt.student_id, quiz_id=attempt.quiz_id).first()
        return dict(attempt_id=attempt.id, quiz_result_id=result.id if result else None,
            status=attempt.status, score=score, percentage=score, passed=score >= 50 if score is not None else None,
            correct_answers=[r["question_id"] for r in rows if r["is_correct"] is True],
            wrong_answers=[r["question_id"] for r in rows if r["is_correct"] is False],
            pending_questions=sum(r["points_awarded"] is None for r in rows), responses=rows)

    def add_final_result(self, attempt):
        rows = attempt.responses
        total = sum(r["points"] for r in rows)
        self.db.add(QuizResult(student_id=attempt.student_id, course_id=attempt.course_id, quiz_id=attempt.quiz_id,
            score=sum(r["points_awarded"] or 0 for r in rows) / (total or 1) * 100,
            correct_answers=sum(r["is_correct"] is True for r in rows), total_questions=len(rows)))

    def submit(self, student_id, quiz, selections):
        if self.find(student_id, quiz.id) or self.db.query(QuizResult).filter_by(student_id=student_id, quiz_id=quiz.id).first():
            raise HTTPException(409, "Quiz has already been submitted.")
        by_id = {s.question_id: s for s in selections}
        if len(by_id) != len(selections):
            raise HTTPException(422, "Duplicate question in submission")
        if not quiz.questions or set(by_id) != {q.id for q in quiz.questions}:
            raise HTTPException(422, "Not all questions have been answered or an answer does not belong to this quiz")
        rows = []
        for q in sorted(quiz.questions, key=lambda q: (q.order_index, str(q.id))):
            s = by_id[q.id]
            row = dict(question_id=str(q.id), question_text=q.text, question_type=q.question_type,
                points=q.points, points_awarded=None, is_correct=None, selected_answer=None,
                correct_answer=None, text_answer=None, feedback="")
            if q.question_type == "written":
                if s.answer_id is not None or not s.text_answer or not s.text_answer.strip():
                    raise HTTPException(422, "A written answer is required")
                row["text_answer"] = s.text_answer.strip()
            elif q.question_type in ("multiple_choice", "yes_no"):
                options = q.answers
                correct = [a for a in options if a.is_correct]
                if len(options) < 2 or len(correct) != 1 or (q.question_type == "yes_no" and (len(options) != 2 or {a.text for a in options} != {"Yes", "No"})):
                    raise HTTPException(422, "This question is not ready: ask the instructor to configure its answer options")
                selected = next((a for a in options if a.id == s.answer_id), None)
                if selected is None or s.text_answer is not None:
                    raise HTTPException(422, "An answer does not belong to its question")
                row.update(selected_answer=selected.text, correct_answer=correct[0].text,
                    is_correct=bool(selected.is_correct), points_awarded=q.points if selected.is_correct else 0)
            else:
                raise HTTPException(422, "Unsupported question type")
            rows.append(row)
        attempt = QuizAttempt(student_id=student_id, course_id=quiz.course_id, quiz_id=quiz.id,
            status="pending_review" if any(r["points_awarded"] is None for r in rows) else "graded", responses=rows)
        self.db.add(attempt)
        if attempt.status == "graded": self.add_final_result(attempt)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(409, "Quiz has already been submitted.")
        self.db.refresh(attempt)
        return self.response(attempt)

    def list_for_course(self, course_id):
        rows = self.db.query(QuizAttempt, User, Quiz).join(User, User.id == QuizAttempt.student_id).join(Quiz, Quiz.id == QuizAttempt.quiz_id).filter(QuizAttempt.course_id == course_id).order_by(QuizAttempt.submitted_at.desc()).all()
        return [dict(**self.response(a), student_name=f"{u.first_name} {u.last_name}", quiz_title=q.title, submitted_at=a.submitted_at) for a,u,q in rows]

    def review(self, instructor_id, course_id, attempt_id, grades):
        attempt = self.db.query(QuizAttempt).filter_by(id=attempt_id, course_id=course_id).with_for_update().first()
        if not attempt: raise HTTPException(404, "Submission not found")
        if attempt.status != "pending_review": raise HTTPException(409, "This submission has already been graded")
        by_id = {str(g.question_id): g for g in grades}
        required = {r["question_id"] for r in attempt.responses if r["question_type"] == "written"}
        if len(by_id) != len(grades) or set(by_id) != required:
            raise HTTPException(422, "Grade every written answer exactly once")
        rows = [dict(r) for r in attempt.responses]
        for r in rows:
            if r["question_id"] in by_id:
                g = by_id[r["question_id"]]
                if g.points_awarded > r["points"]: raise HTTPException(422, "Awarded points exceed the question maximum")
                r.update(points_awarded=g.points_awarded, feedback=g.feedback.strip(), is_correct=g.points_awarded == r["points"])
        attempt.responses = rows
        attempt.status = "graded"
        attempt.reviewed_at = datetime.utcnow()
        attempt.reviewed_by = instructor_id
        self.add_final_result(attempt)
        try: self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(409, "This submission has already been graded")
        self.db.refresh(attempt)
        return self.response(attempt)
