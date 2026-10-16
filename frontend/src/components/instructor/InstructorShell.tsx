"use client";

import Link from "next/link";
import NavigationIcon from "@/components/ui/NavigationIcon";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import RoleGuard from "@/components/auth/RoleGuard";
import { logout } from "@/lib/auth";
import WorkspaceNavbar from "@/components/layout/WorkspaceNavbar";

interface NavLink {
  label: string;
  href: string;
  icon: string;
}

const sections: { title: string; links: NavLink[] }[] = [
  {
    title: "Main",
    links: [
      { label: "Dashboard", href: "/instructor/dashboard", icon: "▦" },
      { label: "My Courses", href: "/instructor/courses", icon: "▤" },
      { label: "My Products", href: "/instructor/products", icon: "▤" },
    ],
  },
  {
    title: "Learners",
    links: [{ label: "Students", href: "/instructor/students", icon: "◉" }],
  },
  {
    title: "Insights",
    links: [{ label: "Analytics", href: "/instructor/analytics", icon: "↗" }],
  },
  {
    title: "Account",
    links: [
      { label: "Profile", href: "/instructor/profile", icon: "◨" },
      { label: "Settings", href: "/instructor/settings", icon: "⚙" },
      { label: "Messages", href: "/instructor/messages", icon: "✉" },
    ],
  },
];

function Navigation({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  return (
    <nav className="space-y-5" aria-label="Instructor navigation">
      {sections.map((section) => (
        <div key={section.title}>
          <p className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">{section.title}</p>
          <div className="mt-1.5 space-y-0.5">
            {section.links.map((link) => {
              const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={onNavigate}
                  aria-current={active ? "page" : undefined}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                    active ? "bg-red-50 text-[#b91c27]" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  }`}
                >
                  <NavigationIcon href={link.href} className="h-4 w-4 shrink-0" />
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </nav>
  );
}

export default function InstructorShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const close = (event: KeyboardEvent) => { if (event.key === "Escape") setOpen(false); };
    window.addEventListener("keydown", close);
    return () => { document.body.style.overflow = overflow; window.removeEventListener("keydown", close); };
  }, [open]);

  const handleLogout = () => {
    logout((path) => router.replace(path));
  };

  return (
    <RoleGuard role="instructor">
      <div className="workspace-shell min-h-screen text-slate-900">
        <WorkspaceNavbar onOpenMenu={() => setOpen(true)} notificationHref="/instructor/messages" onLogout={handleLogout} />

        {/* Mobile drawer */}
        {open && (
          <div className="fixed inset-0 z-40 md:hidden">
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
              <div className="mt-5 flex-1 overflow-y-auto">
                <Navigation pathname={pathname} onNavigate={() => setOpen(false)} />
              </div>
            </aside>
          </div>
        )}

        {/* Desktop sidebar */}
        <aside className="workspace-sidebar fixed inset-y-0 left-0 z-20 hidden w-64 flex-col border-r border-slate-200 bg-white p-5 md:flex">
          <Link href="/instructor/dashboard" className="text-2xl font-bold tracking-tight text-[#d81f2a]">
            BuildLearn<span className="text-slate-900">.</span>
          </Link>
          <p className="mt-2 text-xs font-medium uppercase tracking-wider text-slate-400">Instructor workspace</p>
          <div className="mt-6 flex-1 overflow-y-auto">
            <Navigation pathname={pathname} />
          </div>
        </aside>

        <main className="pt-4 pb-24 md:ml-64 md:pb-8">{children}</main>
      </div>
    </RoleGuard>
  );
}
