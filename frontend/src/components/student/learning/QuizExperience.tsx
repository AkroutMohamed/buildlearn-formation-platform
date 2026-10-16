"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { studentLearning } from "@/services/student-learning.service";
import type { QuizDetails, QuizResult } from "@/types/learning";
import ErrorState from "@/components/ui/ErrorState";

export default function QuizExperience({ quizId }: { quizId: string }) {
  const [quiz, setQuiz] = useState<QuizDetails | null>(null);
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    studentLearning.quiz(quizId).then((data) => { if (active) { setQuiz(data); setResult(data.result ?? null); } }).catch((reason) => {
      if (active) setError(reason instanceof Error ? reason.message : "Unable to load quiz.");
    });
    return () => { active = false; };
  }, [quizId, attempt]);
  const back = <Link href="/student/my-courses" className="inline-block text-sm font-semibold text-red-700 hover:underline">Back to my courses</Link>;
  if (error) return <div className="space-y-4"><ErrorState message={error} onRetry={() => { setError(""); setAttempt((value) => value + 1); }} />{back}</div>;
  if (!quiz) return <div aria-label="Loading quiz" className="h-96 animate-pulse rounded-xl bg-slate-200" />;

  if (result) return <div className="mx-auto max-w-3xl space-y-5 rounded-xl border bg-white p-8 shadow-sm">
    <h1 className="text-3xl font-bold">{result.status === "pending_review" ? "Submitted - awaiting teacher review" : "Quiz result"}</h1>
    <p className="text-sm text-slate-600">Course certificate: complete all lessons and score above 80% on every course quiz. Written answers must be graded first.</p>
    {result.status === "pending_review" ? <><p>Your answers have been saved. {result.pending_questions} written answer(s) await grading. Your final score will appear after teacher review.</p><button disabled={busy} className="rounded-lg border px-4 py-2 disabled:opacity-50" onClick={async () => { setBusy(true); setSubmitError(""); try { const data = await studentLearning.quiz(quizId); setResult(data.result ?? null); } catch (reason) { setSubmitError(reason instanceof Error ? reason.message : "Unable to refresh results."); } finally { setBusy(false); } }}>Refresh grading status</button></> : <><p className="text-2xl font-semibold">{result.percentage?.toFixed(1)}%</p><p>{result.passed ? "Passed" : "Not passed"}</p></>}
    {submitError && <ErrorState message={submitError} />}
    {result.responses?.map((response, index) => <article key={response.question_id} className="space-y-2 rounded-lg border p-4">
      <h2 className="font-semibold">{index + 1}. {response.question_text}</h2>
      <p className="whitespace-pre-wrap">Your answer: {response.text_answer ?? response.selected_answer}</p>
      {response.question_type === "written" ? <p>{response.points_awarded === null ? "Awaiting teacher review" : `Teacher score: ${response.points_awarded} / ${response.points}`}</p> : <><p className={response.is_correct ? "text-emerald-700" : "text-red-700"}>{response.is_correct ? "Correct" : "Incorrect"}</p><p>Correct answer: {response.correct_answer}</p></>}
      {response.feedback && <p className="whitespace-pre-wrap">Teacher feedback: {response.feedback}</p>}
    </article>)}{back}</div>;

  if (!quiz.questions.length) return <div className="space-y-4 rounded-xl border bg-white p-8"><h1 className="text-xl font-semibold">{quiz.title}</h1><p>This quiz has no questions yet.</p>{back}</div>;
  const activeQuiz = quiz;
  const question = quiz.questions[current];
  const answered = quiz.questions.filter((item) => selected[item.id]?.trim()).length;
  async function submit() {
    if (busy) return;
    setBusy(true);
    setSubmitError("");
    try {
      setResult(await studentLearning.submitQuiz(quizId, activeQuiz.questions.flatMap((item) => selected[item.id] ? [item.question_type === "written" ? { question_id: item.id, text_answer: selected[item.id] } : { question_id: item.id, answer_id: selected[item.id] }] : [])));
    } catch (reason) {
      setSubmitError(reason instanceof Error ? reason.message : "Unable to submit quiz. Your answers are preserved; please try again.");
    } finally { setBusy(false); }
  }
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {back}
      <div><p className="text-sm font-semibold text-red-700">Question {current + 1} of {quiz.questions.length}</p><h1 className="mt-1 text-3xl font-bold">{quiz.title}</h1>{quiz.description && <p className="mt-2 text-slate-600">{quiz.description}</p>}</div>
      <p className="text-sm text-slate-500">{answered} of {quiz.questions.length} questions answered. Review previous answers before submitting.</p>
      <p className="text-sm text-slate-600">To earn the course certificate, complete all lessons and score above 80% on every course quiz.</p>
      <div role="progressbar" aria-label="Questions answered" aria-valuemin={0} aria-valuemax={quiz.questions.length} aria-valuenow={answered} className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full bg-red-600" style={{ width: `${answered / quiz.questions.length * 100}%` }} /></div>
      <fieldset disabled={busy} className="rounded-xl border bg-white p-6">
        <legend className="px-2 text-xl font-semibold">{question.text}</legend>
        <p className="mb-3 text-sm text-slate-500">{question.question_type === "written" ? "Written answer - graded by your teacher" : "Choose one answer - automatically graded"}</p>
        {question.question_type === "written" ? <label className="block">Your answer<textarea maxLength={10000} rows={6} className="mt-2 w-full rounded-lg border p-3" value={selected[question.id] ?? ""} onChange={(event) => setSelected((values) => ({ ...values, [question.id]: event.target.value }))} /></label> : <div className="space-y-3">{question.answers.map((answer) => <label key={answer.id} className={`flex cursor-pointer gap-3 rounded-lg border p-4 ${selected[question.id] === answer.id ? "border-red-500 bg-red-50" : ""}`}><input type="radio" name={question.id} checked={selected[question.id] === answer.id} onChange={() => setSelected((values) => ({ ...values, [question.id]: answer.id }))} />{answer.text}</label>)}</div>}
      </fieldset>
      {submitError && <ErrorState title="Quiz not submitted" message={submitError} />}
      <div className="flex flex-wrap justify-between gap-3">
        <button disabled={!current || busy} onClick={() => setCurrent((value) => value - 1)} className="rounded-lg border px-4 py-2 disabled:opacity-40">Previous</button>
        {current === quiz.questions.length - 1 ? (
          <div className="space-y-2 text-right">
            {answered < quiz.questions.length && <p className="text-sm text-amber-700">{quiz.questions.length - answered} unanswered. Answer every question before submitting.</p>}
            <button disabled={busy || answered < quiz.questions.length} onClick={() => void submit()} className="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white disabled:opacity-60">{busy ? "Submitting…" : "Submit quiz"}</button>
          </div>
        ) : <button disabled={busy} onClick={() => setCurrent((value) => value + 1)} className="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white disabled:opacity-60">Next</button>}
      </div>
    </div>
  );
}
