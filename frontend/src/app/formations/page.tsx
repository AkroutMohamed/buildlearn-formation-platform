"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import FormationCard from "@/components/student/formations/FormationCard";
import FormationFilter, { type FormationFilters } from "@/components/student/formations/FormationFilter";
import { getFormations } from "@/services/formation.service";
import type { Formation } from "@/types/formation";
import PageHeader from "@/components/ui/PageHeader";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";

export const CATALOG_PAGE_SIZE = 12;

const emptyFilters: FormationFilters = { search: "" };

export default function PublicFormationsPage() {
  const [formations, setFormations] = useState<Formation[]>([]);
  const [nextPage, setNextPage] = useState(1);
  const [hasNext, setHasNext] = useState(true);
  const [initialLoading, setInitialLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState<FormationFilters>(emptyFilters);
  const requestedPages = useRef(new Set<number>());
  const requestGeneration = useRef(0);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const loadPage = useCallback(
    async (page: number) => {
      if (requestedPages.current.has(page)) return;
      requestedPages.current.add(page);
      const generation = requestGeneration.current;
      setError("");
      if (page === 1) setInitialLoading(true);
      else setLoadingMore(true);
      try {
        const response = await getFormations(page, CATALOG_PAGE_SIZE, filters);
        if (generation !== requestGeneration.current) return;
        setFormations((current) => (page === 1 ? response.items : [...current, ...response.items]));
        setNextPage(page + 1);
        setHasNext(response.has_next);
      } catch (reason) {
        if (generation !== requestGeneration.current) return;
        requestedPages.current.delete(page);
        setError(reason instanceof Error ? reason.message : "Unable to load the course catalog.");
      } finally {
        if (generation === requestGeneration.current) {
          if (page === 1) setInitialLoading(false);
          else setLoadingMore(false);
        }
      }
    },
    [filters],
  );

  useEffect(() => {
    requestedPages.current.clear();
    const timer = window.setTimeout(() => {
      setLoadingMore(false);
      void loadPage(1);
    }, 0);
    return () => { window.clearTimeout(timer); requestGeneration.current += 1; };
  }, [loadPage]);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasNext || initialLoading || loadingMore || error) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) void loadPage(nextPage);
      },
      { rootMargin: "240px" },
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [error, hasNext, initialLoading, loadPage, loadingMore, nextPage]);

  const showGrid = !initialLoading && formations.length > 0;

  return (
    <div className="mx-auto w-full max-w-7xl space-y-8 px-5 py-10 lg:px-8">
      <PageHeader
        eyebrow="Course catalog"
        title="Formations"
        description="Explore all published courses and start learning at your own pace."
      />

      <FormationFilter filters={filters} onChange={setFilters} onClear={() => setFilters(emptyFilters)} />

      {initialLoading && <SkeletonGrid count={3} className="h-72" />}

      {!initialLoading && formations.length === 0 && error && (
        <ErrorState
          title="We could not load the catalog"
          message={error}
          onRetry={() => void loadPage(1)}
        />
      )}

      {!initialLoading && formations.length === 0 && !error && (
        <EmptyState
          title="No courses match those filters"
          message="Try clearing your search or choosing different options."
          action={
            <button
              type="button"
              onClick={() => setFilters(emptyFilters)}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              Clear filters
            </button>
          }
        />
      )}

      {showGrid && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {formations.map((formation) => (
            <FormationCard key={formation.id} {...formation} basePath="/courses" />
          ))}
        </div>
      )}

      {showGrid && error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <p>{error}</p>
          <button
            type="button"
            onClick={() => void loadPage(nextPage)}
            className="mt-2 rounded-lg border border-red-300 px-3 py-1.5 text-sm font-semibold"
          >
            Retry
          </button>
        </div>
      )}

      {loadingMore && <p className="text-center text-sm text-slate-500">Loading more courses…</p>}
      <div ref={sentinelRef} aria-hidden="true" />
    </div>
  );
}
