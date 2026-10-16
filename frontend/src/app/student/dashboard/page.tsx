"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { studentLearning } from "@/services/student-learning.service";
import type { CourseProgress, StudentDashboard } from "@/types/learning";
import NavigationIcon from "@/components/ui/NavigationIcon";
import StatCard from "@/components/ui/StatCard";
import ProgressBar from "@/components/ui/ProgressBar";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";

export default function StudentDashboardPage() {
  const [dashboard, setDashboard] = useState<StudentDashboard | null>(null);
  const [courses, setCourses] = useState<CourseProgress[]>([]);
  const [error, setError] = useState("");
  const [progressError, setProgressError] = useState("");
  const [progressLoading, setProgressLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    studentLearning.dashboard().then((data) => { if (active) { setDashboard(data); setError(""); } }).catch((reason) => {
      if (active) setError(reason instanceof Error ? reason.message : "Unable to load your dashboard.");
    });
    studentLearning.progress().then((data) => { if (active) { setCourses(data); setProgressError(""); } }).catch((reason) => {
      if (active) setProgressError(reason instanceof Error ? reason.message : "Unable to load your learning progress.");
    }).finally(() => { if (active) setProgressLoading(false); });
    return () => { active = false; };
  }, [attempt]);

  const retry = () => { setError(""); setProgressError(""); setProgressLoading(true); setAttempt((value) => value + 1); };

  if (error && !dashboard) return <ErrorState title="Dashboard unavailable" message={error} onRetry={retry} />;

  if (!dashboard) {
    return (
      <div className="space-y-8">
        <LoadingSkeleton className="h-8 w-64" />
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <LoadingSkeleton key={i} className="h-28" />)}
        </div>
        <div className="grid gap-4 md:grid-cols-2">{[1, 2].map((i) => <LoadingSkeleton key={i} className="h-40" />)}</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="studio-welcome flex flex-wrap items-center justify-between gap-6 p-7 sm:p-9">
        <div className="relative z-10"><p className="text-xs font-semibold uppercase tracking-[.18em] text-[#b3d2d0]">YOUR NEXT CHAPTER</p><h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Good work starts<br />with good knowledge.</h1><p className="mt-3 max-w-md text-sm leading-6 text-slate-300">Explore real products, keep your learning moving and build skills you can explain.</p></div>
        <Link href="/student/formations" className="studio-primary relative z-10">Find your next course <span aria-hidden="true">&#8599;</span></Link>
      </section>

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Enrolled courses" value={dashboard.enrolled_courses} icon={<NavigationIcon href="/student/courses" />} />
        <StatCard label="Completed" value={dashboard.completed_courses} icon={<NavigationIcon href="/student/progress" />} />
        <StatCard label="Certificates" value={dashboard.certificates_count} icon={<NavigationIcon href="/student/certificates" />} />
        <StatCard label="Overall progress" value={`${dashboard.overall_progress}%`} />
      </section>

      <section>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight text-slate-900">Continue learning</h2>
          <Link href="/student/my-courses" className="text-sm font-semibold text-[#b91c27] hover:underline">
            View all
          </Link>
        </div>

        {progressLoading ? <LoadingSkeleton className="mt-4 h-40" /> : progressError ? (
          <ErrorState message={progressError} onRetry={retry} />
        ) : courses.filter((course) => course.percentage < 100).length === 0 ? (
          <EmptyState
            title="Nothing in progress yet"
            message="Explore the catalog and enroll in a course to get started."
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
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {courses.filter((course) => course.percentage < 100).slice(0, 4).map((c) => (
              <Link
                key={c.course_id}
                href={`/student/courses/${c.course_id}`}
                className="studio-course rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
              >
                <h3 className="font-semibold text-slate-900">{c.title}</h3>
                <div className="mt-4">
                  <ProgressBar value={c.percentage} tone="brand" sublabel={`${c.completed_lessons} lessons complete`} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
