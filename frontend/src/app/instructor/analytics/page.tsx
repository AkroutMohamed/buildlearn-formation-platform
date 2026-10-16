"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getCourseAnalytics, getInstructorCourses } from "@/services/instructor";
import type { Course, CourseAnalytics } from "@/types/instructor";
import PageHeader from "@/components/ui/PageHeader";
import ErrorState from "@/components/ui/ErrorState";
import EmptyState from "@/components/ui/EmptyState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";

export default function InstructorAnalyticsPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [analytics, setAnalytics] = useState<Record<string, CourseAnalytics>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getInstructorCourses()
      .then(async (items) => {
        setCourses(items);
        const results = await Promise.all(
          items.map(async (course) => {
            const data = await getCourseAnalytics(course.id).catch(() => null);
            return data ? [course.id, data] : null;
          }),
        );
        setAnalytics(Object.fromEntries(results.filter((entry): entry is [string, CourseAnalytics] => entry !== null)));
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load analytics."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl space-y-8 p-5 md:p-8">
        <SkeletonGrid count={2} className="h-40" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-5 md:p-8">
      <PageHeader
        eyebrow="Insights"
        title="Course analytics"
        description="Performance and completion metrics for each of your courses."
      />

      {error && <ErrorState title="Could not load analytics" message={error} />}

      {courses.length === 0 && !error ? (
        <EmptyState
          title="No courses yet"
          message="You are not assigned to any products yet. Contact an administrator."
        />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-slate-500">
              <tr>
                <th className="p-4 font-medium">Course</th>
                <th className="p-4 font-medium">Students</th>
                <th className="p-4 font-medium">Completed</th>
                <th className="p-4 font-medium">Completion</th>
                <th className="p-4 font-medium">Avg quiz</th>
                <th className="p-4 font-medium">Avg progress</th>
                <th className="p-4" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {courses.map((course) => {
                const a = analytics[course.id];
                return (
                  <tr key={course.id} className="hover:bg-slate-50">
                    <td className="p-4 font-medium text-slate-900">{course.title}</td>
                    <td className="p-4 text-slate-600">{a?.total_students ?? "?"}</td>
                    <td className="p-4 text-slate-600">{a?.completed_students ?? "?"}</td>
                    <td className="p-4 text-slate-600">{a ? `${a.completion_rate}%` : "?"}</td>
                    <td className="p-4 text-slate-600">{a ? `${a.average_quiz_score}%` : "?"}</td>
                    <td className="p-4 text-slate-600">{a ? `${a.average_progress}%` : "?"}</td>
                    <td className="p-4">
                      <Link href={`/instructor/courses/${course.id}/analytics`} className="text-sm font-semibold text-[#b91c27] hover:underline">
                        Details
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
