"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getInstructors } from "@/services/admin.service";
import type { InstructorResponse } from "@/types/user";
import PageHeader from "@/components/ui/PageHeader";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";

export default function InstructorsPage() {
  const [instructors, setInstructors] = useState<InstructorResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getInstructors();
      setInstructors(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load instructors.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(load, 0);
    return () => window.clearTimeout(timer);
  }, []);

  return (
    <div className="mx-auto max-w-6xl p-5 md:p-8">
        <PageHeader
          eyebrow="Instructors"
          title="Instructors"
          description="Manage platform instructors."
          actions={
            <Link
              href="/admin/instructors/create"
              className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
            >
              Create instructor
            </Link>
          }
        />

        {error && <ErrorState title="We could not complete that action" message={error} onRetry={load} />}

        {loading && <SkeletonGrid count={3} className="h-24" />}

        {!loading && instructors.length === 0 && !error && (
          <EmptyState
            title="No instructors yet"
            message="Create an instructor to get started."
            action={
              <Link
                href="/admin/instructors/create"
                className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
              >
                Create instructor
              </Link>
            }
          />
        )}

        {!loading && instructors.length > 0 && (
          <div className="mt-6 overflow-x-auto rounded-xl border bg-white">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b bg-slate-50 text-slate-500">
                <tr>
                  <th className="p-4">Name</th>
                  <th className="p-4">Email</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Status</th>
                </tr>
              </thead>
              <tbody>
                {instructors.map((inst) => (
                  <tr key={inst.id} className="border-b">
                    <td className="p-4 font-medium">{inst.first_name} {inst.last_name}</td>
                    <td className="p-4">{inst.email}</td>
                    <td className="p-4 capitalize">{inst.role}</td>
                    <td className="p-4">
                      <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                        inst.instructor_status === "ACTIVE" ? "bg-green-50 text-green-700" :
                        inst.instructor_status === "PENDING" ? "bg-yellow-50 text-yellow-700" :
                        "bg-red-50 text-red-700"
                      }`}>
                        {inst.instructor_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
  );
}
