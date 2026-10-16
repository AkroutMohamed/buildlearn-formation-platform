"use client";

import { useEffect, useState } from "react";
import {
  getEnrolledStudents,
  getInstructorCourses,
  getStudentProgress,
  getStudentQuizResults,
} from "@/services/instructor";
import type { Course, EnrolledStudent, StudentProgress, StudentQuizResult } from "@/types/instructor";

export default function InstructorStudentsPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [courseId, setCourseId] = useState("");
  const [students, setStudents] = useState<EnrolledStudent[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<EnrolledStudent | null>(null);
  const [progress, setProgress] = useState<StudentProgress | null>(null);
  const [quizResults, setQuizResults] = useState<StudentQuizResult[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getInstructorCourses()
      .then((items) => {
        setCourses(items);
        setCourseId(items[0]?.id ?? "");
      })
      .catch((requestError: Error) => setError(requestError.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!courseId) return;
    const timer = window.setTimeout(() => {
      setLoading(true);
      setError("");
      setSelectedStudent(null);
      void getEnrolledStudents(courseId)
        .then(setStudents)
        .catch((requestError: Error) => setError(requestError.message))
        .finally(() => setLoading(false));
    }, 0);
    return () => window.clearTimeout(timer);
  }, [courseId]);

  const selectStudent = async (student: EnrolledStudent) => {
    setSelectedStudent(student);
    setProgress(null);
    setQuizResults([]);
    setError("");
    try {
      const [studentProgress, results] = await Promise.all([
        getStudentProgress(courseId, student.id),
        getStudentQuizResults(courseId, student.id),
      ]);
      setProgress(studentProgress);
      setQuizResults(results);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not load student data");
    }
  };

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Student management</h1>
        <p className="mt-1 text-sm text-gray-600">Review enrolled learners, lesson completion, and quiz results.</p>
      </div>

      <label className="block max-w-md text-sm font-medium">
        Course
        <select className="mt-1 w-full rounded border p-2" value={courseId} onChange={(event) => setCourseId(event.target.value)}>
          {courses.length === 0 && <option value="">No courses available</option>}
          {courses.map((course) => <option key={course.id} value={course.id}>{course.title}</option>)}
        </select>
      </label>

      {error && <p role="alert" className="rounded bg-red-50 p-3 text-red-700">{error}</p>}
      {loading && <p className="text-gray-600">Loading…</p>}

      {!loading && courseId && (
        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <section className="overflow-hidden rounded-lg border bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600"><tr><th className="p-3">Student</th><th className="p-3">Status</th><th className="p-3">Enrolled</th></tr></thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student.id} className="cursor-pointer border-t hover:bg-gray-50" onClick={() => void selectStudent(student)}>
                    <td className="p-3"><p className="font-medium">{student.first_name} {student.last_name}</p><p className="text-gray-500">{student.email}</p></td>
                    <td className="p-3 capitalize">{student.status}</td>
                    <td className="p-3">{new Date(student.enrolled_at).toLocaleDateString()}</td>
                  </tr>
                ))}
                {students.length === 0 && <tr><td className="p-5 text-gray-500" colSpan={3}>No students are enrolled in this course.</td></tr>}
              </tbody>
            </table>
          </section>

          <aside className="rounded-lg border bg-white p-5">
            {!selectedStudent ? <p className="text-gray-600">Select a student to view their progress and quiz results.</p> : (
              <>
                <h2 className="text-lg font-semibold">{selectedStudent.first_name} {selectedStudent.last_name}</h2>
                {progress && <div className="mt-4"><p className="font-medium">Lesson progress: {progress.completion_percent}%</p><div className="mt-2 h-2 overflow-hidden rounded bg-gray-200"><div className="h-full bg-blue-600" style={{ width: `${progress.completion_percent}%` }} /></div><p className="mt-1 text-sm text-gray-600">{progress.completed_lessons} of {progress.total_lessons} lessons completed</p></div>}
                <h3 className="mt-6 font-semibold">Quiz results</h3>
                <ul className="mt-2 space-y-2 text-sm">
                  {quizResults.map((result) => <li key={result.id} className="rounded bg-gray-50 p-3"><p className="font-medium">{result.quiz_title}</p><p>{result.score}% · {result.correct_answers}/{result.total_questions} correct</p></li>)}
                  {progress && quizResults.length === 0 && <li className="text-gray-500">No completed quizzes yet.</li>}
                </ul>
              </>
            )}
          </aside>
        </div>
      )}
    </main>
  );
}
