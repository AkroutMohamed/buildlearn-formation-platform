"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createInstructor } from "@/services/admin.service";
import { Button } from "@/components/ui/Button";

export default function CreateInstructorPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setError("");
    setSubmitting(true);
    try {
      await createInstructor(form);
      router.replace("/admin/instructors");
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Could not create instructor.");
    } finally {
      setSubmitting(false);
    }
  };

  const inputClass =
    "w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm shadow-sm focus:border-[#d81f2a] focus:outline-none";
  const labelClass = "mb-1.5 block text-sm font-medium text-slate-700";

  return (
    <div className="mx-auto max-w-6xl p-5 md:p-8">
        <div className="mb-6">
          <Link href="/admin/instructors" className="text-sm font-medium text-[#d81f2a] hover:underline">
            ← Back to instructors
          </Link>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <h1 className="text-xl font-bold text-slate-900">Create instructor</h1>
          <p className="mt-1 text-sm text-slate-500">Add a new instructor directly. They will be active immediately.</p>

          <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
            {error && (
              <p role="alert" className="rounded-lg bg-red-50 px-3 py-2.5 text-sm text-red-700">
                {error}
              </p>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className={labelClass}>First name</label>
                <input
                  id="first_name"
                  type="text"
                  required
                  className={inputClass}
                  value={form.first_name}
                  onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                />
              </div>
              <div>
                <label htmlFor="last_name" className={labelClass}>Last name</label>
                <input
                  id="last_name"
                  type="text"
                  required
                  className={inputClass}
                  value={form.last_name}
                  onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className={labelClass}>Email</label>
              <input
                id="email"
                type="email"
                required
                className={inputClass}
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>

            <div>
              <label htmlFor="password" className={labelClass}>Password</label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                className={inputClass}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
              <p className="mt-1 text-xs text-slate-500">Use at least 8 characters.</p>
            </div>

            <div className="flex items-center gap-3">
              <Button type="submit" size="lg" loading={submitting}>
                {submitting ? "Creating…" : "Create instructor"}
              </Button>
              <Link
                href="/admin/instructors"
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </Link>
            </div>
          </form>
        </div>
      </div>
  );
}
