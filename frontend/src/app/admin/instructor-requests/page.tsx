"use client";

import { useEffect, useState } from "react";
import { getPendingInstructorRequests, approveInstructor, rejectInstructor } from "@/services/admin.service";
import type { InstructorResponse } from "@/types/user";
import PageHeader from "@/components/ui/PageHeader";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";

export default function InstructorRequestsPage() {
  const [requests, setRequests] = useState<InstructorResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getPendingInstructorRequests();
      setRequests(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load instructor requests.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(load, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const handleApprove = async (userId: string) => {
    setBusy(userId);
    setError("");
    try {
      await approveInstructor(userId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not approve instructor.");
    } finally {
      setBusy(null);
    }
  };

  const handleReject = async (userId: string) => {
    setBusy(userId);
    setError("");
    try {
      await rejectInstructor(userId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not reject instructor.");
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="mx-auto max-w-6xl p-5 md:p-8">
        <PageHeader
          eyebrow="Instructors"
          title="Instructor requests"
          description="Review and manage instructor access requests."
        />

        {error && <ErrorState title="We could not complete that action" message={error} onRetry={load} />}

        {loading && <SkeletonGrid count={3} className="h-24" />}

        {!loading && requests.length === 0 && !error && (
          <EmptyState
            title="No pending requests"
            message="All instructor requests have been reviewed."
          />
        )}

        {!loading && requests.length > 0 && (
          <div className="mt-6 overflow-x-auto rounded-xl border bg-white">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b bg-slate-50 text-slate-500">
                <tr>
                  <th className="p-4">Name</th>
                  <th className="p-4">Email</th>
                  <th className="p-4">Status</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((req) => (
                  <tr key={req.id} className="border-b">
                    <td className="p-4 font-medium">{req.first_name} {req.last_name}</td>
                    <td className="p-4">{req.email}</td>
                    <td className="p-4">
                      <span className="inline-flex rounded-full bg-yellow-50 px-2 py-1 text-xs font-semibold text-yellow-700">
                        PENDING
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          disabled={busy === req.id}
                          onClick={() => void handleApprove(req.id)}
                          className="rounded-lg bg-green-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          disabled={busy === req.id}
                          onClick={() => void handleReject(req.id)}
                          className="rounded-lg bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                        >
                          Reject
                        </button>
                      </div>
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
