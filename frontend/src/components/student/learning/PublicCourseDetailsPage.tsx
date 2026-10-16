"use client";

import BlueprintArt from "@/components/ui/BlueprintArt";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import type { PublicCourseDetails } from "@/types/learning";
import Cover from "@/components/ui/Cover";
import { getAuthenticatedUser } from "@/services/auth.service";
import { apiRequest, ApiError } from "@/services/api-client";
import type { AuthenticatedUser } from "@/types/user";

export default function PublicCourseDetailsPage({ courseId }: { courseId: string }) {
  const [course, setCourse] = useState<PublicCourseDetails | null>(null);
  const [error, setError] = useState("");
  const [enrolling, setEnrolling] = useState(false);
  const [notice, setNotice] = useState("");
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const searchParams = useSearchParams();

  useEffect(() => {
    getAuthenticatedUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setAuthLoading(false));
  }, []);

  useEffect(() => {
    if (!courseId) return;
    apiRequest<PublicCourseDetails>(`/public/courses/${courseId}`)
      .then((data) => {
        setCourse(data);
        setError("");
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Unable to load this course."));
  }, [courseId]);

  async function enroll() {
    setEnrolling(true);
    setNotice("");
    setError("");
    try {
      await apiRequest(`/student/courses/${courseId}/enroll`, { method: "POST" });
      window.location.href = `/student/courses/${courseId}`;
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        window.location.href = `/student/courses/${courseId}`;
        return;
      }
      setError(e instanceof Error ? e.message : "Unable to enroll. Please try again.");
    } finally {
      setEnrolling(false);
    }
  }

  function getSafeRedirect(): string {
    const redirect = searchParams.get("redirect");
    if (redirect && redirect.startsWith("/") && !redirect.startsWith("//")) {
      return redirect;
    }
    return `/courses/${courseId}`;
  }

  if (error && !course) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
        <h1 className="text-xl font-semibold text-red-800">Course unavailable</h1>
        <p className="mt-2 text-sm text-red-700">{error}</p>
        <Link href="/formations" className="mt-5 inline-block font-semibold text-[#b91c27] underline">
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

  const isStudent = user?.role === "student";

  return (
    <div className="mx-auto w-full max-w-7xl space-y-7 px-5 py-8 lg:px-8">
      <Link href="/formations" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-red-700"><span aria-hidden="true">←</span> Back to the catalog</Link>

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

          {notice && <p role="status" className="mt-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
          {error && <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

          <div className="mt-6">
            {authLoading ? (
              <p role="status" className="text-sm text-slate-500">Checking your account…</p>
            ) : isStudent ? (
              <button
                type="button"
                disabled={enrolling}
                onClick={() => void enroll()}
                className="rounded-lg bg-[#d81f2a] px-6 py-3 font-semibold text-white shadow-sm hover:bg-[#b91c27] disabled:opacity-60"
              >
                {enrolling ? "Enrolling..." : "Enroll now"}
              </button>
            ) : user ? (
              <p className="text-sm text-slate-600">Course enrollment is available to student accounts.</p>
            ) : (
              <Link
                href={`/login?redirect=${encodeURIComponent(getSafeRedirect())}`}
                className="inline-block rounded-lg bg-[#d81f2a] px-6 py-3 font-semibold text-white shadow-sm transition hover:bg-[#b91c27]"
              >
                Enroll now
              </Link>
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
                    <li key={lesson.id} className="flex items-center justify-between gap-3 px-4 py-3 text-sm">
                      <span className="flex items-center gap-3">
                        <span aria-hidden="true" className="grid h-6 w-6 place-items-center rounded-full bg-slate-100 text-xs font-bold text-slate-400">{lesson.order_index + 1}</span>
                        <span className="text-slate-500">{lesson.title}</span>
                      </span>
                      <span className="text-xs text-slate-400">Enroll to access</span>
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
          </div>
          <ul className="mt-4 space-y-2">
            {course.quizzes.map((quiz) => (
              <li key={quiz.id} className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 px-4 py-3">
                <span className="text-sm font-medium text-slate-700">{quiz.title}</span>
                <span className="text-xs text-slate-400">Enroll to access</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
