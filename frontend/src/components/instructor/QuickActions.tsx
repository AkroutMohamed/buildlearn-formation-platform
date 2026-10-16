import Link from "next/link";

interface QuickAction {
  label: string;
  href: string;
}

interface QuickActionsProps {
  actions: QuickAction[];
}

export default function QuickActions({ actions }: QuickActionsProps) {
  return (
    <section className="rounded-xl border bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold">Quick actions</h2>
      <div className="mt-4 flex flex-wrap gap-3">
        {actions.map((action) => (
          <Link
            key={action.href}
            href={action.href}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            {action.label}
          </Link>
        ))}
      </div>
    </section>
  );
}