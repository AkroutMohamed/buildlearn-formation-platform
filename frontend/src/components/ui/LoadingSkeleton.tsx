export function Spinner({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={`inline-block animate-spin rounded-full border-2 border-current border-t-transparent ${className}`}
    />
  );
}

export function LoadingSkeleton({ className = "h-32" }: { className?: string }) {
  return <div className={`animate-pulse rounded-xl bg-slate-200/80 ${className}`} />;
}

export function SkeletonGrid({ count = 3, className = "h-40" }: { count?: number; className?: string }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <LoadingSkeleton key={i} className={className} />
      ))}
    </div>
  );
}
