export interface ProgressBarProps {
  value: number;
  label?: string;
  sublabel?: string;
  tone?: "brand" | "default";
}

export default function ProgressBar({ value, label, sublabel, tone = "default" }: ProgressBarProps) {
  const progress = Math.min(100, Math.max(0, Number.isFinite(value) ? value : 0));
  return (
    <div>
      {label && (
        <div className="mb-1.5 flex items-center justify-between text-sm">
          <span className="text-slate-600">{label}</span>
          <span className="font-semibold text-slate-900">{progress}%</span>
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
        className="h-2 overflow-hidden rounded-full bg-slate-100"
      >
        <div
          className={`h-full rounded-full transition-all ${tone === "brand" ? "bg-[#d81f2a]" : "bg-slate-500"}`}
          style={{ width: `${progress}%` }}
        />
      </div>
      {sublabel && <p className="mt-1 text-xs text-slate-500">{sublabel}</p>}
    </div>
  );
}
