interface AnalyticsChartProps {
  title: string;
  values: number[];
}

export default function AnalyticsChart({ title, values }: AnalyticsChartProps) {
  const maximum = Math.max(...values, 1);

  return (
    <section className="rounded-xl border bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="mt-5 flex h-40 items-end gap-2" aria-label={title}>
        {values.map((value, index) => (
          <div key={`${value}-${index}`} className="flex-1 rounded-t bg-red-600" style={{ height: `${(value / maximum) * 100}%` }} title={String(value)} />
        ))}
      </div>
    </section>
  );
}