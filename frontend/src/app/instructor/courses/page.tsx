"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { deleteCourse, getInstructorCourses, setCoursePublished } from "@/services/instructor";
import type { Course } from "@/types/instructor";
import PageHeader from "@/components/ui/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import Cover from "@/components/ui/Cover";

export default function InstructorCoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError("");
    getInstructorCourses()
      .then(setCourses)
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load your courses."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const timer = window.setTimeout(load, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const togglePublish = async (course: Course) => {
    setBusy(course.id);
    setError("");
    try {
      await setCoursePublished(course.id, course.status !== "Published");
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not update the course.");
    } finally {
      setBusy(null);
    }
  };

  const remove = async (course: Course) => {
    if (!window.confirm(`Delete "${course.title}"? This cannot be undone.`)) return;
    setBusy(course.id);
    setError("");
    try {
      await deleteCourse(course.id);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not delete the course.");
    } finally {
      setBusy(null);
    }
  };

  if (loading) {
    return (
      <div className="p-5 md:p-8">
        <SkeletonGrid count={3} className="h-52" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-5 md:p-8">
      <PageHeader
        eyebrow="Courses"
        title="My courses"
        description="Manage courses you have created inside your assigned products."
      />

      {error && <ErrorState title="We could not complete that action" message={error} onRetry={load} />}

      {courses.length === 0 && !error ? (
        <EmptyState
          title="No courses yet"
          message="You have assigned products, but you have not created any courses yet. Go to My Products to create your first course."
          action={
            <Link
              href="/instructor/products"
              className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
            >
              View My Products
            </Link>
          }
        />
      ) : (
        <div className="grid gap-5 md:grid-cols-2">
          {courses.map((course) => (
            <article
              key={course.id}
              className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
            >
              {course.thumbnail && (
                <div className="h-32 overflow-hidden bg-slate-100">
                  <Cover src={course.thumbnail} />
                </div>
              )}
              <div className="flex flex-1 flex-col p-5">
                <div className="flex items-center justify-between gap-3">
                  <h2 className="font-semibold text-slate-900">{course.title}</h2>
                  <StatusBadge status={course.status} />
                </div>
                 <p className="mt-2 line-clamp-2 text-sm text-slate-500">{course.description}</p>
                 <p className="mt-3 text-xs text-slate-500">
                   {course.product?.name ?? "No product"} · {course.category} · {course.level} · {course.duration} min
                 </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  <Link
                    href={`/instructor/courses/${course.id}`}
                    className="rounded-lg bg-[#d81f2a] px-3 py-2 text-sm font-semibold text-white hover:bg-[#b91c27]"
                  >
                    Manage
                  </Link>
                  <Link
                    href={`/instructor/courses/${course.id}/modules`}
                    className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    Content
                  </Link>
                  <button
                    type="button"
                    disabled={busy === course.id}
                    onClick={() => void togglePublish(course)}
                    className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                  >
                    {course.status === "Published" ? "Unpublish" : "Publish"}
                  </button>
                  <button
                    type="button"
                    disabled={busy === course.id}
                    onClick={() => void remove(course)}
                    className="rounded-lg border border-red-200 px-3 py-2 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
