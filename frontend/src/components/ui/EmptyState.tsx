import type { ReactNode } from "react";
import NavigationIcon from "@/components/ui/NavigationIcon";

export interface EmptyStateProps {
  title: string;
  message?: string;
  action?: ReactNode;
  icon?: ReactNode;
}

export default function EmptyState({ title, message, action, icon }: EmptyStateProps) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center">
      {icon && <div className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-full bg-slate-100 text-slate-400">{icon}</div>}
      <div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-[#e8efec] text-[#35585c]"><NavigationIcon href="/student/courses" className="h-6 w-6" /></div>
      <h2 className="text-base font-semibold text-slate-800">{title}</h2>
      {message && <p className="mx-auto mt-1.5 max-w-md text-sm text-slate-500">{message}</p>}
      {action && <div className="mt-5 flex justify-center">{action}</div>}
    </div>
  );
}
