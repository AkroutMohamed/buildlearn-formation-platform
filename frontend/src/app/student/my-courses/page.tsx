"use client";

import BlueprintArt from "@/components/ui/BlueprintArt";
import Link from "next/link";
import { useEffect, useState } from "react";
import { studentLearning } from "@/services/student-learning.service";
import type { MyCourse } from "@/types/learning";
import PageHeader from "@/components/ui/PageHeader";
import ProgressBar from "@/components/ui/ProgressBar";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import Cover from "@/components/ui/Cover";

export default function MyCoursesPage() {
  const [courses, setCourses] = useState<MyCourse[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    studentLearning
      .myCourses()
      .then(setCourses)
      .catch((e) => setError(e instanceof Error ? e.message : "Unable to load your courses."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="space-y-3">
          <div className="h-3 w-24 animate-pulse rounded bg-slate-200" />
          <div className="h-7 w-56 animate-pulse rounded bg-slate-200" />
        </div>
        <SkeletonGrid count={2} className="h-64" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="My learning"
        title="My courses"
        description="Pick up where you left off."
      />

      {error && <ErrorState title="Could not load your courses" message={error} />}

      {courses.length === 0 && !error ? (
        <EmptyState
          title="You have not enrolled in any courses yet"
          message="Explore the catalog and enroll in a course to start learning."
          action={
            <Link
              href="/student/formations"
              className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
            >
              Explore the course catalog
            </Link>
          }
        />
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {courses.map((course) => (
            <article
              key={course.id}
              className="studio-course flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
            >
              <div className="flex h-36 items-center justify-center overflow-hidden bg-[#172b3a]">
                {course.thumbnail ? <Cover src={course.thumbnail} /> : (
                  <BlueprintArt className="h-full max-h-64 w-full" />
                )}
              </div>
              <div className="flex flex-1 flex-col p-5">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  {course.instructor}
                </p>
                <h2 className="mt-1 text-lg font-semibold text-slate-900">{course.title}</h2>
                <div className="mt-4">
                  <ProgressBar
                    value={course.progress}
                    tone="brand"
                    sublabel={`${course.completed_lessons} / ${course.total_lessons} lessons`}
                  />
                </div>
                <div className="mt-5 flex gap-2">
                  <Link
                    href={`/student/courses/${course.id}`}
                    className="inline-flex flex-1 items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
                  >
                    Continue learning
                  </Link>
                  {course.status === "completed" && (
                    <Link
                      href="/student/certificates"
                      className="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      Certificate
                    </Link>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
