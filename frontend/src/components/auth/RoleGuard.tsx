"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDashboardPath, getStoredRole } from "@/lib/auth";
import type { UserRole } from "@/types/user";

export default function RoleGuard({ role, children }: { role: UserRole; children: React.ReactNode }) {
  const router = useRouter();
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    const storedRole = getStoredRole();
    if (!storedRole) {
      router.replace("/login");
      return;
    }
    if (storedRole !== role) {
      router.replace(getDashboardPath(storedRole));
      return;
    }
    window.setTimeout(() => setAllowed(true), 0);
  }, [role, router]);

  if (!allowed) return <div className="grid min-h-screen place-items-center text-slate-600">Checking your session…</div>;
  return <>{children}</>;
}
