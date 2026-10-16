import Link from "next/link";

interface SidebarItem {
  label: string;
  href: string;
}

interface SidebarProps {
  items?: SidebarItem[];
}

const defaultItems: SidebarItem[] = [
  { label: "Dashboard", href: "/instructor/dashboard" },
  { label: "Courses", href: "/instructor/courses" },
  { label: "Students", href: "/instructor/students" },
  { label: "Analytics", href: "/instructor/analytics" },
  { label: "Messages", href: "/instructor/messages" },
];

export default function Sidebar({ items = defaultItems }: SidebarProps) {
  return (
    <aside className="w-64 shrink-0 border-r bg-white p-5">
      <Link href="/instructor" className="text-xl font-bold">
        Instructor
      </Link>
      <nav className="mt-8 space-y-2" aria-label="Instructor navigation">
        {items.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="block rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}