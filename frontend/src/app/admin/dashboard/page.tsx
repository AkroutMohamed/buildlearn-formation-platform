"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAdminDashboard, getAdminCourses, getInstructors, getPendingInstructorRequests } from "@/services/admin.service";
import PageHeader from "@/components/ui/PageHeader";
import StatCard from "@/components/ui/StatCard";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";

export default function AdminDashboardPage() {
  const [message, setMessage] = useState("");
  const [courseCount, setCourseCount] = useState<number | null>(null);
  const [instructorCount, setInstructorCount] = useState<number | null>(null);
  const [pendingCount, setPendingCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      getAdminDashboard().catch(() => ({ message: "" })),
      getAdminCourses().catch(() => []),
      getInstructors().catch(() => []),
      getPendingInstructorRequests().catch(() => []),
    ]).then(([dashboard, courses, instructors, pending]) => {
      if (cancelled) return;
      setMessage(dashboard.message);
      setCourseCount(Array.isArray(courses) ? courses.length : 0);
      setInstructorCount(Array.isArray(instructors) ? instructors.length : 0);
      setPendingCount(Array.isArray(pending) ? pending.length : 0);
      setLoading(false);
    }).catch((e) => {
      if (cancelled) return;
      setError(e instanceof Error ? e.message : "Could not load dashboard.");
      setLoading(false);
    });
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-5 md:p-8">
        <PageHeader
          eyebrow="Dashboard"
          title={message || "Welcome Admin"}
          description="Platform overview and quick actions."
        />

        {error && <ErrorState title="We could not load the dashboard" message={error} onRetry={() => window.location.reload()} />}

        {loading && (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => <SkeletonGrid key={i} count={1} className="h-28" />)}
          </div>
        )}

        {!loading && !error && (
          <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="Courses" value={courseCount ?? 0} />
            <StatCard label="Instructors" value={instructorCount ?? 0} />
            <StatCard label="Pending requests" value={pendingCount ?? 0} />
            <StatCard label="Status" value="Active" />
          </section>
        )}

        {!loading && !error && (
          <section className="grid gap-4 md:grid-cols-3">
            <Link href="/admin/instructor-requests" className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-red-300 hover:shadow-md">
              <h3 className="font-semibold text-slate-900">Instructor requests</h3>
              <p className="mt-1 text-sm text-slate-500">Review pending instructor access requests.</p>
            </Link>
            <Link href="/admin/products" className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-red-300 hover:shadow-md">
              <h3 className="font-semibold text-slate-900">All products</h3>
              <p className="mt-1 text-sm text-slate-500">Manage the platform catalog.</p>
            </Link>
            <Link href="/admin/instructors" className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-red-300 hover:shadow-md">
              <h3 className="font-semibold text-slate-900">Instructors</h3>
              <p className="mt-1 text-sm text-slate-500">View and manage instructors.</p>
            </Link>
          </section>
        )}
      </div>
  );
}
