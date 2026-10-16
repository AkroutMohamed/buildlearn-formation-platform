"use client";

import BlueprintArt from "@/components/ui/BlueprintArt";
import Link from "next/link";
import { useEffect, useState } from "react";
import { createProductCourse, getProductCourses } from "@/services/product";
import type { ProductCourse } from "@/types/product";
import PageHeader from "@/components/ui/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import type { CourseCategory, CourseLevel } from "@/types/instructor";

const page = "mx-auto max-w-6xl p-5 md:p-8";

interface InstructorProductCoursesPageClientProps {
  productId: string;
}

export default function InstructorProductCoursesPageClient({
  productId,
}: InstructorProductCoursesPageClientProps) {
  const [courses, setCourses] = useState<ProductCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", category: "Outillage" as CourseCategory, level: "Beginner" as CourseLevel, duration: 0 });

  const load = () => {
    setLoading(true);
    setError("");
    getProductCourses(productId)
      .then(setCourses)
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load courses."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const timer = window.setTimeout(load, 0);
    return () => window.clearTimeout(timer);
  }, [productId]);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.description.trim()) return;
    setCreating(true);
    setError("");
    try {
      await createProductCourse(productId, { ...form, title: form.title.trim(), description: form.description.trim() });
      setForm({ title: "", description: "", category: "Outillage", level: "Beginner", duration: 0 });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not create course.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className={page}>
      <PageHeader
        eyebrow="Product"
        title="Courses"
        description="Manage courses for this product."
      />

      {error && <ErrorState title="We could not complete that action" message={error} onRetry={load} />}

      <form onSubmit={create} className="mt-6 rounded-xl border bg-white p-5">
        <h3 className="font-semibold">Create new course</h3>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-700">Title</label>
            <input
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-700">Description</label>
            <textarea
              className="mt-1 w-full rounded-lg border px-3 py-2"
              rows={3}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Category</label>
            <select
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value as CourseCategory })}
            >
              <option value="Outillage">Outillage</option>
              <option value="Étanchéité">Étanchéité</option>
              <option value="Gypstant">Gypstant</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Level</label>
            <select
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={form.level}
              onChange={(e) => setForm({ ...form, level: e.target.value as CourseLevel })}
            >
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Duration (min)</label>
            <input
              type="number"
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={form.duration}
              onChange={(e) => setForm({ ...form, duration: parseInt(e.target.value || "0", 10) })}
              min={0}
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            type="submit"
            disabled={creating}
            className="rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white hover:bg-[#b91c27] disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create course"}
          </button>
        </div>
      </form>

      <div className="mt-8">
        <h2 className="text-xl font-semibold tracking-tight text-slate-900">Existing courses</h2>
        {loading ? (
          <div className="mt-4">
            <SkeletonGrid count={2} className="h-44" />
          </div>
        ) : courses.length === 0 ? (
          <EmptyState title="No courses yet" message="Create your first course for this product." />
        ) : (
          <div className="mt-4 grid gap-5 md:grid-cols-2">
            {courses.map((course) => (
              <article
                key={course.id}
                className="studio-course flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
              >
                <div className="flex h-36 items-center justify-center overflow-hidden bg-[#172b3a]">
                  {course.thumbnail ? (
                    <img src={course.thumbnail} alt="" className="h-full w-full object-cover" />
                  ) : (
                    <BlueprintArt category={course.category} className="h-full max-h-64 w-full" />
                  )}
                </div>
                <div className="flex flex-1 flex-col p-5">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-semibold text-slate-900">{course.title}</h3>
                    <StatusBadge status={course.status} />
                  </div>
                  <p className="mt-1 text-sm text-slate-500">{course.description}</p>
                  <p className="mt-3 text-xs text-slate-500">
                    {course.category} · {course.level} · {course.duration} min
                  </p>
                  <div className="mt-5 flex gap-2">
                    <Link
                      href={`/instructor/courses/${course.id}`}
                      className="inline-flex flex-1 items-center justify-center rounded-lg bg-[#d81f2a] px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
                    >
                      Manage
                    </Link>
                    <Link
                      href={`/instructor/courses/${course.id}/modules`}
                      className="inline-flex flex-1 items-center justify-center rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      Content
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
