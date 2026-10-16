"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { loginUser } from "@/services/auth.service";
import { getDashboardPath, getTokenRole } from "@/lib/auth";
import { Button } from "@/components/ui/Button";

function isSafeRedirect(value: string | null): value is string {
  if (!value) return false;
  if (value.startsWith("/") && !value.startsWith("//")) return true;
  return false;
}

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const redirect = searchParams.get("redirect");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      const role = getTokenRole(token);
      if (role) {
        router.replace(getDashboardPath(role));
      }
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setError("");
    setSubmitting(true);
    try {
      const data = await loginUser(form);
      const role = getTokenRole(data.access_token);
      if (!role) throw new Error("Your session is invalid or has expired. Please sign in again.");
      localStorage.setItem("token", data.access_token);
      const safeRedirect = isSafeRedirect(redirect) ? redirect : getDashboardPath(role);
      router.replace(safeRedirect);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to sign in. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="studio-stat rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h1 className="text-xl font-bold text-slate-900">Welcome back</h1>
      <p className="mt-1 text-sm text-slate-500">Enter your credentials to continue.</p>

      <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
        {error && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2.5 text-sm text-red-700">
            {error}
          </p>
        )}

        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-700">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm shadow-sm focus:border-[#d81f2a] focus:outline-none"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm shadow-sm focus:border-[#d81f2a] focus:outline-none"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>

        <Button type="submit" size="lg" loading={submitting} className="w-full">
          {submitting ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </div>
  );
}

export default function LoginPage() {
  return (
    <main className="studio-hero flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Link href="/" className="text-2xl font-bold tracking-tight text-[#d81f2a]">
            BuildLearn<span className="text-slate-900">.</span>
          </Link>
          <p className="mt-2 text-sm text-slate-500">Sign in to your learning workspace.</p>
        </div>

        <Suspense fallback={<div className="studio-stat rounded-2xl border border-slate-200 bg-white p-8 shadow-sm"><div className="h-64 rounded-xl bg-slate-200" /></div>}>
          <LoginForm />
        </Suspense>

        <p className="mt-6 text-center text-sm text-slate-500">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="font-semibold text-[#d81f2a] hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </main>
  );
}
