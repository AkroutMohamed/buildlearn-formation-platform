export interface StatCardProps {
  label: string;
  value: string | number;
  detail?: string;
}

export default function StatCard({ label, value, detail }: StatCardProps) {
  return (
    <article className="studio-stat rounded-xl border bg-white p-5 shadow-sm">
      <h2 className="text-sm text-gray-500">{label}</h2>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
      {detail && <p className="mt-1 text-xs text-gray-500">{detail}</p>}
    </article>
  );
}