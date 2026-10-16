"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAuthenticatedUser } from "@/services/auth.service";
import { logout as logoutUser } from "@/lib/auth";
import type { AuthenticatedUser } from "@/types/user";

export default function StudentProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getAuthenticatedUser()
      .then(setUser)
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : "Unable to load your profile.");
      });
  }, []);

  const logout = () => {
    setUser(null);
    logoutUser((path) => router.replace(path));
  };

  if (error) return <div className="mx-auto max-w-3xl"><div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-5 text-red-700"><p className="font-semibold">Profile unavailable</p><p className="mt-1 text-sm">{error}</p><button onClick={() => router.replace("/login")} className="mt-4 rounded-lg border border-red-300 px-3 py-2 text-sm font-semibold">Return to login</button></div></div>;
  if (!user) return <div className="mx-auto max-w-3xl"><div className="animate-pulse rounded-2xl border bg-white p-7"><div className="h-16 w-16 rounded-full bg-slate-200" /><div className="mt-5 h-6 w-48 rounded bg-slate-200" /><div className="mt-3 h-4 w-64 rounded bg-slate-100" /></div></div>;

  const fields = [{ label: "First name", value: user.first_name }, { label: "Last name", value: user.last_name }, { label: "Email", value: user.email }, { label: "Role", value: user.role }];
  return <div className="mx-auto max-w-3xl space-y-6"><section className="overflow-hidden rounded-2xl border bg-white shadow-sm"><div className="h-24 bg-red-600" /><div className="px-6 pb-6"><div className="-mt-10 grid h-20 w-20 place-items-center rounded-2xl border-4 border-white bg-red-100 text-3xl font-bold text-red-700 shadow-sm">{user.first_name.charAt(0)}{user.last_name.charAt(0)}</div><div className="mt-4"><p className="text-sm font-semibold uppercase tracking-wider text-red-600">Student profile</p><h1 className="mt-1 text-3xl font-bold text-slate-900">{user.first_name} {user.last_name}</h1><p className="mt-1 text-slate-500">Manage your BuildLearn account information.</p></div></div></section><section className="rounded-2xl border bg-white p-6 shadow-sm"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-lg font-bold">Account details</h2><p className="mt-1 text-sm text-slate-500">Details linked to your authenticated account.</p></div><span className="rounded-full bg-red-50 px-3 py-1 text-sm font-semibold capitalize text-red-700">{user.role}</span></div><dl className="mt-6 grid gap-4 sm:grid-cols-2">{fields.map(field => <div key={field.label} className="rounded-xl border bg-slate-50 p-4"><dt className="text-xs font-semibold uppercase tracking-wider text-slate-500">{field.label}</dt><dd className="mt-1 break-words font-medium text-slate-800">{field.value}</dd></div>)}</dl></section><section className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-red-100 bg-red-50 p-5"><div><h2 className="font-bold text-slate-900">Sign out</h2><p className="mt-1 text-sm text-slate-600">This removes your active session from this device.</p></div><button onClick={logout} className="rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-red-700">Logout</button></section></div>;
}
