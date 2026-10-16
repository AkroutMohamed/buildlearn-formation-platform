import StatCard, { type StatCardProps } from "./StatCard";

interface DashboardStatsProps {
  stats: StatCardProps[];
}

export default function DashboardStats({ stats }: DashboardStatsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4" aria-label="Dashboard statistics">
      {stats.map((stat) => (
        <StatCard key={stat.label} {...stat} />
      ))}
    </section>
  );
}