"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function CourseNavigation({ courseId }: { courseId: string }) {
  const pathname = usePathname();
  const base = `/instructor/courses/${courseId}`;
  if (pathname === base) return null;
  const tabs = [["Overview", ""], ["Modules & lessons", "modules"], ["Quizzes", "quizzes"], ["Students", "students"], ["Analytics", "analytics"], ["Certificates", "certificates"]];
  return <div className="mx-auto max-w-6xl px-5 pt-5 md:px-8">
    <Link href="/instructor/courses" className="text-sm font-medium text-slate-500 hover:text-red-700">Back to my courses</Link>
    <nav aria-label="Course navigation" className="mt-4 flex flex-wrap gap-2 border-b border-slate-200">
      {tabs.map(([label, path]) => {
        const active = path === "modules" && pathname === `${base}/lessons` || !!path && pathname.startsWith(`${base}/${path}`);
        return <Link key={path} href={`${base}${path ? `/${path}` : ""}`} aria-current={active ? "page" : undefined} className={`rounded-t-lg px-3 py-2 text-sm ${active ? "border border-b-white bg-white text-red-700" : "text-slate-500 hover:text-slate-700"}`}>{label}</Link>;
      })}
    </nav>
  </div>;
}
