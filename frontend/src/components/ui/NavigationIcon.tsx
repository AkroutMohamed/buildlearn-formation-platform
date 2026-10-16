export default function NavigationIcon({ href, className = "h-5 w-5" }: { href: string; className?: string }) {
  const key = href.split("/").filter(Boolean).at(1) ?? "dashboard";
  const paths: Record<string, string> = {
    dashboard: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
    courses: "M4 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-3H4z M13 7a3 3 0 0 1 3-3h5v14h-4a4 4 0 0 0-4 3",
    products: "m12 3 9 5-9 5-9-5z M3 8v9l9 5 9-5V8 M12 13v9",
    students: "M15 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0 M5 21v-3a7 7 0 0 1 14 0v3 M19 4a3 3 0 0 1 0 6",
    analytics: "M4 3v18h17 M8 16v-4 M13 16V8 M18 16V5",
    certificates: "M17 8a5 5 0 1 1-10 0 5 5 0 0 1 10 0 M8 12l-2 9 6-3 6 3-2-9",
    chat: "M21 11a8 8 0 0 1-8 8H9l-6 3 2-6a8 8 0 0 1 8-13h1 M19 2v6 M16 5h6",
    notifications: "M5 17h14l-2-3V9a5 5 0 0 0-10 0v5z M10 21h4",
    profile: "M15 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0 M4 21a8 8 0 0 1 16 0",
    messages: "M3 5h18v14H3z m0 0 9 8 9-8",
    settings: "M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8 M12 2v3 M12 19v3 M2 12h3 M19 12h3 M5 5l2 2 M17 17l2 2 M5 19l2-2 M17 7l2-2",
  };
  const aliases: Record<string, string> = { formations: 'courses', 'my-courses': 'courses', progress: 'analytics', instructors: 'students', 'instructor-requests': 'students' };
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[aliases[key] ?? key] ?? paths.courses} /></svg>;
}
