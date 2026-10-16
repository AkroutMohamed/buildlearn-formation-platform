"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createAdminProduct } from "@/services/admin.service";
import PageHeader from "@/components/ui/PageHeader";
import ErrorState from "@/components/ui/ErrorState";

const initial = {
  name: "",
  description: "",
  category: "",
  status: "Draft" as "Draft" | "Published" | "Archived",
};

export default function AdminCreateProductPage() {
  const router = useRouter();
  const [form, setForm] = useState(initial);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const change = (key: string, value: string) =>
    setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    if (form.name.trim().length < 3) {
      return setError("Product name must be at least 3 characters.");
    }
    setSaving(true);
    try {
      const result = await createAdminProduct({
        name: form.name.trim(),
        description: form.description.trim() || null,
        category: form.category.trim() || null,
        status: form.status,
      });
      router.push(`/admin/products/${result.id}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create the product.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl p-5 md:p-8">
        <PageHeader
          eyebrow="Products"
          title="Create product"
          description="Add a new product to the platform catalog."
        />

        {error && <ErrorState title="We could not complete that action" message={error} onRetry={() => {}} />}

        <form onSubmit={submit} className="mt-6 space-y-5 rounded-2xl border bg-white p-6 shadow-sm">
          <div className="grid gap-5 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700">Product name</label>
              <input
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-red-500"
                value={form.name}
                onChange={(e) => change("name", e.target.value)}
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700">Description</label>
              <textarea
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-red-500"
                rows={4}
                value={form.description}
                onChange={(e) => change("description", e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Category</label>
              <input
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-red-500"
                value={form.category}
                onChange={(e) => change("category", e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Status</label>
              <select
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-red-500"
                value={form.status}
                onChange={(e) => change("status", e.target.value)}
              >
                <option value="Draft">Draft</option>
                <option value="Published">Published</option>
                <option value="Archived">Archived</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3">
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
              {saving ? "Creating..." : "Create product"}
            </button>
          </div>
        </form>
      </div>
  );
}
