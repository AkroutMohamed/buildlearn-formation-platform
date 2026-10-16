"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { studentLearning } from "@/services/student-learning.service";
import type { CourseProgress } from "@/types/learning";
import PageHeader from "@/components/ui/PageHeader";
import ProgressBar from "@/components/ui/ProgressBar";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";

export default function ProgressPage() {
  const [items, setItems] = useState<CourseProgress[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    studentLearning
      .progress()
      .then(setItems)
      .catch((reason) => {
        setItems([]);
        setError(reason instanceof Error ? reason.message : "Unable to load your progress.");
      });
  }, []);

  if (items === null) {
    return (
      <div className="space-y-8">
        <LoadingHeader />
        <SkeletonGrid count={2} className="h-36" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Learning progress"
        title="Your progress"
        description="Track your course completion across everything you are learning."
      />

      {error && <ErrorState title="We could not load your progress" message={error} />}

      {items.length === 0 && !error ? (
        <EmptyState
          title="No progress yet"
          message="Enroll in a course from the catalog and complete lessons to see your progress here."
          action={
            <Link
              href="/student/formations"
              className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
            >
              Explore courses
            </Link>
          }
        />
      ) : (
        <div className="space-y-4">
          {items.map((item) => {
            const total = item.completed_lessons + item.remaining_lessons;
            return (
              <article key={item.course_id} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h2 className="font-semibold text-slate-900">{item.title}</h2>
                    <p className="mt-1 text-sm text-slate-500">
                      {item.completed_lessons} / {total} lessons completed
                    </p>
                  </div>
                  <Link
                    href={`/student/courses/${item.course_id}`}
                    className="text-sm font-semibold text-[#b91c27] hover:underline"
                  >
                    Open course
                  </Link>
                </div>
                <div className="mt-4">
                  <ProgressBar value={item.percentage} tone="brand" />
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

function LoadingHeader() {
  return (
    <div className="space-y-3">
      <div className="h-3 w-24 animate-pulse rounded bg-slate-200" />
      <div className="h-7 w-56 animate-pulse rounded bg-slate-200" />
    </div>
  );
}
