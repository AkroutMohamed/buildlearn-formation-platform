"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { getAdminProduct, updateAdminProduct } from "@/services/admin.service";
import type { Product } from "@/types/product";
import PageHeader from "@/components/ui/PageHeader";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";

export default function AdminProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getAdminProduct(id);
      setProduct(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load product.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      const timer = window.setTimeout(() => void load(), 0);
      return () => window.clearTimeout(timer);
    }
  }, [id, load]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!product) return;
    setError("");
    if (product.name.trim().length < 3 || (product.description ?? "").trim().length < 10) {
      return setError("Title must be 3+ characters and description 10+ characters.");
    }
    setSaving(true);
    try {
      await updateAdminProduct(id, {
        name: product.name,
        description: product.description,
        category: product.category,
        status: product.status,
      });
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save changes.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl p-5 md:p-8">
          <SkeletonGrid count={1} className="h-96" />
        </div>
    );
  }

  if (!product) {
    return (
      <div className="mx-auto max-w-4xl p-5 md:p-8">
          <ErrorState title="Product not found" message={error || "The requested product could not be loaded."} onRetry={load} />
        </div>
    );
  }

  const change = (key: keyof Product, value: string | null) =>
    setProduct((current) => (current ? { ...current, [key]: value } : current));

  return (
    <div className="mx-auto max-w-4xl p-5 md:p-8">
        <PageHeader eyebrow="Products" title={product.name} description="Edit product details." />

        {error && <ErrorState title="We could not complete that action" message={error} onRetry={load} />}

        <form onSubmit={submit} className="mt-6 space-y-5 rounded-2xl border bg-white p-6 shadow-sm">
          <div className="grid gap-5 md:grid-cols-2">
            <Field label="Product title" value={product.name} onChange={(v) => change("name", v)} required />
            <Field label="Category" value={product.category ?? ""} onChange={(v) => change("category", v)} />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700">Description</label>
            <textarea
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-red-500"
              rows={4}
              value={product.description ?? ""}
              onChange={(e) => change("description", e.target.value)}
              required
            />
          </div>
          <div className="flex justify-between gap-3">
            <Link
              href={`/admin/products/${product.id}/instructors`}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              Manage instructors
            </Link>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => router.back()}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27] disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save changes"}
              </button>
            </div>
          </div>
        </form>
      </div>
  );
}

function Field({ label, value, onChange, required }: { label: string; value: string; onChange: (value: string) => void; required?: boolean }) {
  const classes = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-red-500";
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      <input className={classes} type="text" value={value} onChange={(e) => onChange(e.target.value)} required={required} />
    </label>
  );
}
