import type { ReactNode } from "react";

export interface StatCardProps {
  label: string;
  value: string | number;
  detail?: string;
  icon?: ReactNode;
}

export default function StatCard({ label, value, detail, icon }: StatCardProps) {
  return (
    <article className="studio-stat rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="text-sm font-medium text-slate-500">{label}</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{value}</p>
          {detail && <p className="mt-1 text-xs text-slate-500">{detail}</p>}
        </div>
        {icon && <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-red-50 text-[#d81f2a]">{icon}</div>}
      </div>
    </article>
  );
}
