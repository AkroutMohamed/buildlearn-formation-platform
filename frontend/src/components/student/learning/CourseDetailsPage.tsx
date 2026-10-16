"use client";

import BlueprintArt from "@/components/ui/BlueprintArt";
import Link from "next/link";
import { useEffect, useState } from "react";
import { studentLearning } from "@/services/student-learning.service";
import type { CourseDetails } from "@/types/learning";
import ProgressBar from "@/components/ui/ProgressBar";
import Cover from "@/components/ui/Cover";

export default function CourseDetailsPage({ courseId }: { courseId: string }) {
  const [course, setCourse] = useState<CourseDetails | null>(null);
  const [error, setError] = useState("");
  const [enrolling, setEnrolling] = useState(false);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    studentLearning
      .course(courseId)
      .then((data) => {
        setCourse(data);
        setNotice("");
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Unable to load this course."));
  }, [courseId]);

  async function enroll() {
    setEnrolling(true);
    setNotice("");
    setError("");
    try {
      await studentLearning.enroll(courseId);
      await studentLearning.course(courseId).then(setCourse);
      setNotice("Enrollment successful. You can start learning now.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to enroll in this course.");
    } finally {
      setEnrolling(false);
    }
  }

  if (error && !course) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
        <h1 className="text-xl font-semibold text-red-800">Course unavailable</h1>
        <p className="mt-2 text-sm text-red-700">{error}</p>
        <Link href="/student/formations" className="mt-5 inline-block font-semibold text-[#b91c27] underline">
          Back to courses
        </Link>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="animate-pulse space-y-5">
        <div className="h-64 rounded-xl bg-slate-200" />
        <div className="h-8 w-2/3 rounded bg-slate-200" />
        <div className="h-36 rounded-xl bg-slate-200" />
      </div>
    );
  }

  const firstLesson = course.modules.flatMap((m) => m.lessons)[0];
  const enrolled = course.is_enrolled;

  return (
    <div className="space-y-7">
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:grid md:grid-cols-[minmax(0,1fr)_320px]">
        <div className="p-6 lg:p-8">
          <p className="text-xs font-semibold uppercase tracking-wide text-[#b91c27]">
            {course.category} · {course.level}
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{course.title}</h1>
          <p className="mt-4 max-w-2xl leading-7 text-slate-600">{course.description}</p>

          <dl className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-sm text-slate-600">
            <div><dt className="inline text-slate-400">Instructor: </dt><dd className="inline font-medium">{course.instructor}</dd></div>
            <div><dt className="inline text-slate-400">Language: </dt><dd className="inline font-medium">{course.language}</dd></div>
            <div><dt className="inline text-slate-400">Duration: </dt><dd className="inline font-medium">{course.duration} min</dd></div>
          </dl>

          {enrolled && (
            <div className="mt-5 max-w-md">
              <ProgressBar value={course.completion_percentage} tone="brand" label={`${course.completed_lessons} of ${course.total_lessons} lessons`} />
            </div>
          )}

          {notice && <p role="status" className="mt-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
          {error && <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

          <div className="mt-6">
            {enrolled && firstLesson ? (
              <Link
                href={`/student/lessons/${firstLesson.id}`}
                className="inline-block rounded-lg bg-[#d81f2a] px-6 py-3 font-semibold text-white shadow-sm hover:bg-[#b91c27]"
              >
                {course.completion_percentage > 0 ? "Continue learning" : "Start learning"}
              </Link>
            ) : (
              <button
                type="button"
                disabled={enrolling}
                onClick={() => void enroll()}
                className="rounded-lg bg-[#d81f2a] px-6 py-3 font-semibold text-white shadow-sm hover:bg-[#b91c27] disabled:opacity-60"
              >
                {enrolling ? "Enrolling..." : "Enroll now"}
              </button>
            )}
          </div>
        </div>

        <div className="min-h-52 bg-[#172b3a]">
          {course.thumbnail ? <Cover src={course.thumbnail} /> : (
            <div className="grid h-full min-h-52 place-items-center">
              <BlueprintArt category={course.category} className="h-full max-h-64 w-full" />
            </div>
          )}
        </div>
      </section>

      {course.objectives && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold tracking-tight text-slate-900">Course objectives</h2>
          <ul className="mt-4 grid gap-2 text-slate-700 sm:grid-cols-2">
            {course.objectives.split(/\n|•/).filter(Boolean).map((item) => (
              <li key={item} className="flex gap-2 text-sm">
                <span aria-hidden="true" className="text-[#d81f2a]">+</span>
                {item.trim()}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-[#d81f2a]">Curriculum</p>
            <h2 className="mt-1 text-lg font-semibold tracking-tight text-slate-900">Course content</h2>
          </div>
        </div>

        {course.modules.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">This course has no content yet.</p>
        ) : (
          <div className="mt-5 space-y-4">
            {course.modules.map((module, moduleIndex) => (
              <div key={module.id} className="rounded-xl border border-slate-200">
                <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
                  <p className="text-sm font-semibold text-slate-800">Module {moduleIndex + 1} · {module.title}</p>
                  {module.description && <p className="mt-0.5 text-xs text-slate-500">{module.description}</p>}
                </div>
                <ul className="divide-y divide-slate-100">
                  {module.lessons.map((lesson) => (
                    <li key={lesson.id}>
                      {enrolled ? (
                        <Link href={`/student/lessons/${lesson.id}`} className="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-slate-50">
                          <span className="flex items-center gap-3">
                            <span aria-hidden="true" className={`grid h-6 w-6 place-items-center rounded-full text-xs font-bold ${lesson.is_completed ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-400"}`}>
                              {lesson.is_completed ? "Y" : lesson.order_index + 1}
                            </span>
                            <span className="font-medium text-slate-700">{lesson.title}</span>
                          </span>
                          <span className="shrink-0 text-xs text-slate-400">{lesson.duration_minutes} min</span>
                        </Link>
                      ) : (
                        <div className="flex items-center justify-between gap-3 px-4 py-3 text-sm">
                          <span className="flex items-center gap-3">
                            <span aria-hidden="true" className="grid h-6 w-6 place-items-center rounded-full bg-slate-100 text-xs font-bold text-slate-400">{lesson.order_index + 1}</span>
                            <span className="text-slate-500">{lesson.title}</span>
                          </span>
                          <span className="text-xs text-slate-400">Enroll to access</span>
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </section>

      {course.quizzes.length > 0 && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-[#d81f2a]">Assessments</p>
            <h2 className="mt-1 text-lg font-semibold tracking-tight text-slate-900">Quizzes</h2>
            <p className="mt-2 text-sm text-slate-600">Certificate requirement: complete all lessons and score above 80% on every quiz. Written answers require teacher grading.</p>
          </div>
          <ul className="mt-4 space-y-2">
            {course.quizzes.map((quiz) => (
              <li key={quiz.id} className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 px-4 py-3">
                <span className="text-sm font-medium text-slate-700">{quiz.title}</span>
                {enrolled ? (
                  <Link href={`/student/quizzes/${quiz.id}`} className="text-sm font-semibold text-[#b91c27] hover:underline">Take quiz</Link>
                ) : (
                  <span className="text-xs text-slate-400">Enroll to access</span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
