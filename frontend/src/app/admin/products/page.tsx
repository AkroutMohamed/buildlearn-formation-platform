"use client";

import BlueprintArt from "@/components/ui/BlueprintArt";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getAdminProducts, deleteAdminProduct, publishAdminProduct, unpublishAdminProduct } from "@/services/admin.service";
import type { Product } from "@/types/product";
import PageHeader from "@/components/ui/PageHeader";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import StatusBadge from "@/components/ui/StatusBadge";

export default function AdminProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getAdminProducts();
      setProducts(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load products.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(load, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const remove = async (product: Product) => {
    if (!window.confirm(`Delete "${product.name}"? This cannot be undone.`)) return;
    setBusy(product.id);
    setError("");
    try {
      await deleteAdminProduct(product.id);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not delete the product.");
    } finally {
      setBusy(null);
    }
  };

  const togglePublish = async (product: Product) => {
    setBusy(product.id);
    setError("");
    try {
      if (product.status === "Published") {
        await unpublishAdminProduct(product.id);
      } else {
        await publishAdminProduct(product.id);
      }
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not update the product.");
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-5 md:p-8">
        <PageHeader
          eyebrow="Products"
          title="All products"
          description="Manage the platform catalog."
          actions={
            <Link
              href="/admin/products/create"
              className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
            >
              Create product
            </Link>
          }
        />

        {error && <ErrorState title="We could not complete that action" message={error} onRetry={load} />}

        {loading && <SkeletonGrid count={3} className="h-52" />}

        {!loading && products.length === 0 && !error && (
          <EmptyState
            title="No products yet"
            message="Create your first product to get started."
            action={
              <Link
                href="/admin/products/create"
                className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
              >
                Create product
              </Link>
            }
          />
        )}

        {!loading && products.length > 0 && (
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
                  <div className="mt-4 flex flex-wrap gap-2">
                    <Link
                      href={`/admin/products/${product.id}`}
                      className="rounded-lg bg-[#d81f2a] px-3 py-2 text-sm font-semibold text-white hover:bg-[#b91c27]"
                    >
                      Edit
                    </Link>
                    <Link
                      href={`/admin/products/${product.id}/instructors`}
                      className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      Instructors
                    </Link>
                    <button
                      type="button"
                      disabled={busy === product.id}
                      onClick={() => void togglePublish(product)}
                      className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                    >
                      {product.status === "Published" ? "Unpublish" : "Publish"}
                    </button>
                    <button
                      type="button"
                      disabled={busy === product.id}
                      onClick={() => void remove(product)}
                      className="rounded-lg border border-red-200 px-3 py-2 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
  );
}
