"use client";

import Link from "next/link";
import NavigationIcon from "@/components/ui/NavigationIcon";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const links = [
  { name: "Dashboard", href: "/student/dashboard", icon: "▦" },
  { name: "Course catalog", href: "/student/formations", icon: "□" },
  { name: "My courses", href: "/student/my-courses", icon: "▤" },
  { name: "Progress", href: "/student/progress", icon: "↗" },
  { name: "Certificates", href: "/student/certificates", icon: "☆" },
  { name: "AI Assistant", href: "/student/chat", icon: "◌" },
  { name: "Notifications", href: "/student/notifications", icon: "◌" },
  { name: "Profile", href: "/student/profile", icon: "◉" },
];

export const STUDENT_NAV_EVENT = "buildlearn:open-student-nav";
export function openStudentNav() {
  if (typeof window !== "undefined") window.dispatchEvent(new Event(STUDENT_NAV_EVENT));
}

function NavItems({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  return (
    <nav className="mt-6 space-y-1" aria-label="Student navigation">
      {links.map((link) => {
        const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
        return (
          <Link
            key={link.href}
            href={link.href}
            onClick={onNavigate}
            aria-current={active ? "page" : undefined}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
              active ? "bg-red-50 text-[#b91c27]" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            }`}
          >
            <NavigationIcon href={link.href} className="h-4 w-4 shrink-0" />
            {link.name}
          </Link>
        );
      })}
    </nav>
  );
}

export default function StudentSidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = () => setOpen(true);
    window.addEventListener(STUDENT_NAV_EVENT, handler);
    return () => window.removeEventListener(STUDENT_NAV_EVENT, handler);
  }, []);

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="workspace-sidebar hidden w-64 shrink-0 lg:sticky lg:top-0 lg:h-screen border-r border-slate-200 bg-white p-5 lg:flex lg:flex-col">
        <Link href="/student/dashboard" className="px-2 text-xl font-bold tracking-tight text-[#d81f2a]">
          BuildLearn<span className="text-slate-900">.</span>
        </Link>
        <p className="mt-2 px-2 text-xs font-medium uppercase tracking-wider text-slate-400">
          Learning workspace
        </p>
        <NavItems pathname={pathname} />
        <div className="mt-auto rounded-xl bg-slate-50 p-4">
          <p className="text-sm font-semibold text-slate-800">Need help?</p>
          <p className="mt-1 text-xs leading-5 text-slate-500">Contact support for assistance with your training.</p>
        </div>
      </aside>

      {/* Mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-slate-900/40" onClick={() => setOpen(false)} aria-hidden="true" />
          <aside className="workspace-sidebar absolute left-0 top-0 flex h-full w-72 flex-col border-r border-slate-200 bg-white p-5 shadow-xl">
            <div className="flex items-center justify-between">
              <span className="text-xl font-bold tracking-tight text-[#d81f2a]">
                BuildLearn<span className="text-slate-900">.</span>
              </span>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Close navigation menu"
                className="grid h-8 w-8 place-items-center rounded-lg text-slate-500 hover:bg-slate-100"
              >
                ✕
              </button>
            </div>
            <NavItems pathname={pathname} onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}
    </>
  );
}
