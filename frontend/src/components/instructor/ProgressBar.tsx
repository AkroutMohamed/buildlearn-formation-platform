interface ProgressBarProps {
  value: number;
  label?: string;
}

export default function ProgressBar({ value, label }: ProgressBarProps) {
  const progress = Math.min(100, Math.max(0, value));

  return (
    <div>
      {label && <div className="mb-1 flex justify-between text-sm text-gray-600"><span>{label}</span><span>{progress}%</span></div>}
      <div className="h-2 overflow-hidden rounded-full bg-gray-200" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
        <div className="h-full rounded-full bg-red-600" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}