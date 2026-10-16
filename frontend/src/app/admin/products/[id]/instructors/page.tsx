"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getProductInstructors, getInstructors, assignProductInstructor, unassignProductInstructor } from "@/services/admin.service";
import type { InstructorResponse } from "@/types/user";
import PageHeader from "@/components/ui/PageHeader";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";

export default function AdminProductInstructorsPage() {
  const params = useParams();
  const id = params.id as string;
  const [assigned, setAssigned] = useState<InstructorResponse[]>([]);
  const [available, setAvailable] = useState<InstructorResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [selected, setSelected] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [assignedData, availableData] = await Promise.all([
        getProductInstructors(id),
        getInstructors(),
      ]);
      setAssigned(assignedData);
      setAvailable(availableData.filter((i) => !assignedData.some((a) => a.id === i.id)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load instructors.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      const timer = window.setTimeout(() => void load(), 0);
      return () => window.clearTimeout(timer);
    }
  }, [id, load]);

  const handleAssign = async () => {
    if (!selected) return;
    setBusy(selected);
    setError("");
    try {
      await assignProductInstructor(id, selected);
      await load();
      setSelected("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not assign instructor.");
    } finally {
      setBusy(null);
    }
  };

  const handleUnassign = async (instructorId: string) => {
    setBusy(instructorId);
    setError("");
    try {
      await unassignProductInstructor(id, instructorId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not unassign instructor.");
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="mx-auto max-w-6xl p-5 md:p-8">
        <PageHeader
          eyebrow="Products"
          title="Assigned instructors"
          description="Manage which instructors can teach this product."
        />

        {error && <ErrorState title="We could not complete that action" message={error} onRetry={load} />}

        {loading && <SkeletonGrid count={3} className="h-24" />}

        {!loading && (
          <div className="mt-6 space-y-8">
            <div className="rounded-xl border bg-white p-5">
              <h2 className="text-lg font-semibold text-slate-900">Assign instructor</h2>
              <p className="mt-1 text-sm text-slate-500">Only ACTIVE instructors can be assigned.</p>
              <div className="mt-4 flex gap-3">
                <select
                  className="flex-1 rounded-lg border border-slate-300 px-3 py-2"
                  value={selected}
                  onChange={(e) => setSelected(e.target.value)}
                >
                  <option value="">Select an instructor</option>
                  {available.map((instructor) => (
                    <option key={instructor.id} value={instructor.id}>
                      {instructor.first_name} {instructor.last_name} ({instructor.email})
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  disabled={!selected || busy === selected}
                  onClick={() => void handleAssign()}
                  className="rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27] disabled:opacity-50"
                >
                  Assign
                </button>
              </div>
            </div>

            <div className="rounded-xl border bg-white">
              <div className="border-b px-5 py-3 text-sm font-semibold text-slate-900">
                Current assignments ({assigned.length})
              </div>
              {assigned.length === 0 ? (
                <div className="p-5 text-sm text-slate-500">No instructors assigned yet.</div>
              ) : (
                <div className="divide-y">
                  {assigned.map((inst) => (
                    <div key={inst.id} className="flex items-center justify-between px-5 py-3">
                      <div>
                        <p className="font-medium text-slate-900">
                          {inst.first_name} {inst.last_name}
                        </p>
                        <p className="text-sm text-slate-500">{inst.email}</p>
                      </div>
                      <button
                        type="button"
                        disabled={busy === inst.id}
                        onClick={() => void handleUnassign(inst.id)}
                        className="rounded-lg border border-red-200 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
                      >
                        Unassign
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
  );
}
