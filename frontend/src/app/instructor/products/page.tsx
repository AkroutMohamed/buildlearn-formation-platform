"use client";

import BlueprintArt from "@/components/ui/BlueprintArt";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getInstructorProducts } from "@/services/product";
import type { Product } from "@/types/product";
import PageHeader from "@/components/ui/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";

export default function InstructorProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    getInstructorProducts()
      .then(setProducts)
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load your products."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const timer = window.setTimeout(load, 0);
    return () => window.clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="p-5 md:p-8">
        <SkeletonGrid count={3} className="h-44" />
      </div>
    );
  }

  if (error && products.length === 0) {
    return (
      <div className="p-5 md:p-8">
        <ErrorState title="We could not load your products" message={error} onRetry={load} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-5 md:p-8">
      <PageHeader
        eyebrow="Products"
        title="My Products"
        description="Products assigned to you by an administrator."
      />

      {error && <ErrorState title="Some data could not be loaded" message={error} onRetry={load} />}

      {products.length === 0 ? (
        <EmptyState
          title="No products yet"
          message="You are not assigned to any products yet. Contact an administrator."
        />
      ) : (
        <div className="grid gap-5 md:grid-cols-2">
          {products.map((product) => (
            <article
              key={product.id}
              className="studio-course flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
            >
              <div className="flex h-36 items-center justify-center overflow-hidden bg-[#172b3a]">
                <BlueprintArt category={product.category ?? "Gypstant"} className="h-full max-h-64 w-full" />
              </div>
              <div className="flex flex-1 flex-col p-5">
                <div className="flex items-center justify-between gap-3">
                  <h2 className="font-semibold text-slate-900">{product.name}</h2>
                  <StatusBadge status={product.status} />
                </div>
                <p className="mt-2 line-clamp-2 text-sm text-slate-500">{product.description ?? "No description"}</p>
                <p className="mt-3 text-xs text-slate-500">
                  {product.category ?? "Uncategorized"} · Updated {new Date(product.updated_at).toLocaleDateString()}
                </p>
                <div className="mt-5 flex gap-2">
                  <Link
                    href={`/instructor/products/${product.id}`}
                    className="inline-flex flex-1 items-center justify-center rounded-lg bg-[#d81f2a] px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
                  >
                    Open Product
                  </Link>
                  <Link
                    href={`/instructor/products/${product.id}/courses`}
                    className="inline-flex flex-1 items-center justify-center rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    Courses
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
