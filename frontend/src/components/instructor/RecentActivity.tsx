export interface ActivityItem {
  id: string | number;
  title: string;
  timestamp: string;
}

interface RecentActivityProps {
  items: ActivityItem[];
}

export default function RecentActivity({ items }: RecentActivityProps) {
  return (
    <section className="rounded-xl border bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold">Recent activity</h2>
      <ul className="mt-4 divide-y">
        {items.map((item) => (
          <li key={item.id} className="flex justify-between gap-4 py-3 text-sm">
            <span className="text-gray-700">{item.title}</span>
            <time className="shrink-0 text-gray-500">{item.timestamp}</time>
          </li>
        ))}
      </ul>
    </section>
  );
}