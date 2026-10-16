"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { registerUser, loginUser } from "@/services/auth.service";
import type { UserRole } from "@/types/user";
import { getTokenRole, getDashboardPath } from "@/lib/auth";
import { Button } from "@/components/ui/Button";

function isSafeRedirect(value: string | null): value is string {
  if (!value) return false;
  if (value.startsWith("/") && !value.startsWith("//")) return true;
  return false;
}

const ROLE_OPTIONS: { value: UserRole; label: string; note?: string }[] = [
  { value: "student", label: "Learn as a student" },
  { value: "instructor", label: "Teach as an instructor", note: "Requires administrator approval before access is granted." },
];

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect");

  const [form, setForm] = useState<{
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    role: UserRole;
  }>({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setError("");
    setSubmitting(true);
    try {
      await registerUser(form);
      const data = await loginUser({ email: form.email, password: form.password });
      const role = getTokenRole(data.access_token);
      if (!role) throw new Error("Your session is invalid or has expired. Please sign in again.");
      localStorage.setItem("token", data.access_token);
      const safeRedirect = isSafeRedirect(redirect) ? redirect : getDashboardPath(role);
      router.replace(safeRedirect);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Registration failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const inputClass =
    "w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm shadow-sm focus:border-[#d81f2a] focus:outline-none";
  const labelClass = "mb-1.5 block text-sm font-medium text-slate-700";

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h1 className="text-xl font-bold text-slate-900">Create your account</h1>
      <p className="mt-1 text-sm text-slate-500">Choose the experience that fits you.</p>

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
              autoComplete="given-name"
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
              autoComplete="family-name"
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
            autoComplete="email"
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
            autoComplete="new-password"
            required
            minLength={8}
            className={inputClass}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <p className="mt-1 text-xs text-slate-500">Use at least 8 characters.</p>
        </div>

        <div>
          <span className={labelClass}>I want to</span>
          <div className="grid grid-cols-2 gap-3">
            {ROLE_OPTIONS.map((option) => (
              <label
                key={option.value}
                className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border px-3 py-2.5 text-sm font-medium transition ${
                  form.role === option.value
                    ? "border-[#d81f2a] bg-red-50 text-[#b91c27]"
                    : "border-slate-300 bg-white text-slate-600 hover:bg-slate-50"
                }`}
              >
                <input
                  type="radio"
                  name="role"
                  value={option.value}
                  checked={form.role === option.value}
                  onChange={() => setForm({ ...form, role: option.value })}
                  className="sr-only"
                />
                <span>{option.label}</span>
                {option.note && (
                  <span className="mt-1 text-xs text-slate-500">{option.note}</span>
                )}
              </label>
            ))}
          </div>
        </div>

        <Button type="submit" size="lg" loading={submitting} className="w-full">
          {submitting ? "Creating account…" : "Create account"}
        </Button>
      </form>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Link href="/" className="text-2xl font-bold tracking-tight text-[#d81f2a]">
            BuildLearn<span className="text-slate-900">.</span>
          </Link>
          <p className="mt-2 text-sm text-slate-500">Create your account to get started.</p>
        </div>

        <Suspense fallback={<div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm"><div className="h-64 rounded-xl bg-slate-200" /></div>}>
          <RegisterForm />
        </Suspense>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link href="/login" className="font-semibold text-[#d81f2a] hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
