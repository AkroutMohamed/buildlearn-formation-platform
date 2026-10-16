"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getAuthenticatedUser } from "@/services/auth.service";
import NavigationIcon from "@/components/ui/NavigationIcon";
import Avatar from "@/components/ui/Avatar";
import type { AuthenticatedUser } from "@/types/user";

interface WorkspaceNavbarProps {
  onOpenMenu?: () => void;
  notificationHref?: string;
  onLogout?: () => void;
}

export default function WorkspaceNavbar({ onOpenMenu, notificationHref, onLogout }: WorkspaceNavbarProps) {
  const router = useRouter();
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getAuthenticatedUser().then(setUser).catch(() => router.replace("/login"));
  }, [router]);

  useEffect(() => {
    if (!menuOpen) return;
    const handleClick = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMenuOpen(false);
        menuRef.current?.querySelector("button")?.focus();
      }
    };
    document.addEventListener("mousedown", handleClick);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleKey);
    };
  }, [menuOpen]);

  return (
    <header className="workspace-navbar sticky top-0 z-30 flex min-h-20 items-center justify-between border-b border-slate-200 bg-white px-4 py-3 lg:px-8">
      <div className="flex items-center gap-3">
        {onOpenMenu && (
          <button
            type="button"
            onClick={onOpenMenu}
            aria-label="Open navigation menu"
            className="grid h-9 w-9 place-items-center rounded-lg text-slate-600 hover:bg-slate-100 md:hidden"
          >
            <span aria-hidden="true">☰</span>
          </button>
        )}
        <p className="text-sm font-medium text-slate-500">BuildLearn / Your workspace</p>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {notificationHref ? (
          <Link
            href={notificationHref}
            aria-label="Notifications"
            className="relative grid h-9 w-9 place-items-center rounded-lg text-slate-600 hover:bg-slate-100"
          >
            <NavigationIcon href="/student/notifications" />
          </Link>
        ) : null}

        {onLogout && (
          <div className="relative" ref={menuRef}>
            <button
              type="button"
              onClick={() => setMenuOpen((value) => !value)}
              aria-expanded={menuOpen}
              aria-label="Open user menu"
              className="flex items-center gap-2 rounded-lg hover:bg-slate-100"
            >
              <Avatar name={user ? `${user.first_name} ${user.last_name}` : "?"} size="sm" />
              <div className="hidden md:block min-w-0 text-left">
                <p className="truncate text-sm font-semibold text-slate-800">
                  {user ? `${user.first_name} ${user.last_name}` : "Loading…"}
                </p>
                <p className="truncate text-xs text-slate-500">{user?.email ?? ""}</p>
              </div>
            </button>

            {menuOpen && (
              <div className="absolute right-0 top-full mt-2 w-48 rounded-xl border border-slate-200 bg-white py-1 shadow-lg">
                <button
                  type="button"
                  onClick={() => {
                    setMenuOpen(false);
                    onLogout();
                  }}
                  className="flex w-full items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        )}

        {!onLogout && (
          <>
            <Avatar name={user ? `${user.first_name} ${user.last_name}` : "?"} size="sm" />
            <div className="hidden md:block min-w-0">
              <p className="truncate text-sm font-semibold text-slate-800">
                {user ? `${user.first_name} ${user.last_name}` : "Loading…"}
              </p>
              <p className="truncate text-xs text-slate-500">{user?.email ?? ""}</p>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
