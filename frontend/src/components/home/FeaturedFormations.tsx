"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getFormations } from "@/services/formation.service";
import type { Formation } from "@/types/formation";
import FormationCard from "@/components/student/formations/FormationCard";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import ErrorState from "@/components/ui/ErrorState";

export default function FeaturedFormations() {
  const [courses, setCourses] = useState<Formation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    getFormations(1, 3).then((data) => { if (active) setCourses(data.items); }).catch((reason) => {
      if (active) setError(reason instanceof Error ? reason.message : "Unable to load available courses.");
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [attempt]);
  return <section className="bg-slate-50 py-16">
    <div className="mx-auto max-w-7xl px-5 lg:px-8">
      <div className="text-left">
        <p className="text-xs font-semibold uppercase tracking-wider text-[#d81f2a]">Explore the catalog</p>
        <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Available trainings</h2>
        <p className="mt-3 max-w-xl text-slate-600">Browse published technical courses across our product categories.</p>
      </div>
      <div className="mt-10">
        {loading ? <SkeletonGrid count={3} className="h-80" /> : error ? <ErrorState message={error} onRetry={() => { setError(""); setLoading(true); setAttempt((value) => value + 1); }} /> : courses.length ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">{courses.map((course) => <FormationCard key={course.id} {...course} basePath="/courses" />)}</div>
        ) : <p className="rounded-xl border border-dashed bg-white p-8 text-center text-slate-500">No courses are published yet. Please check back later.</p>}
      </div>
      <div className="mt-8 text-center"><Link href="/formations" className="inline-block rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 hover:border-red-300 hover:text-red-700">Browse all courses</Link></div>
    </div>
  </section>;
}
