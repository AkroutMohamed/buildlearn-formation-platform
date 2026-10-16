"use client";

import BlueprintArt from "@/components/ui/BlueprintArt";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getProduct, getProductCourses } from "@/services/product";
import type { Product, ProductCourse } from "@/types/product";
import PageHeader from "@/components/ui/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";

const page = "mx-auto max-w-6xl p-5 md:p-8";

interface InstructorProductPageClientProps {
  productId: string;
}

export default function InstructorProductPageClient({
  productId,
}: InstructorProductPageClientProps) {
  const pathname = usePathname();
  const [product, setProduct] = useState<Product | null>(null);
  const [courses, setCourses] = useState<ProductCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    getProduct(productId)
      .then(setProduct)
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load product."))
      .finally(() => setLoading(false));
  };

  const loadCourses = () => {
    getProductCourses(productId)
      .then(setCourses)
      .catch(() => {});
  };

  useEffect(() => {
    const timer = window.setTimeout(load, 0);
    return () => window.clearTimeout(timer);
  }, [productId]);

  useEffect(() => {
    loadCourses();
  }, [productId]);

  if (loading) {
    return (
      <div className={page}>
        <SkeletonGrid count={2} className="h-28" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className={page}>
        <ErrorState title="We could not load this product" message={error || "Product not found"} />
      </div>
    );
  }

  const tabs: [string, string][] = [
    ["Overview", ""],
    ["Courses", "courses"],
  ];

  const isActive = (path: string) => (path === "" ? pathname === `/instructor/products/${productId}` : pathname.startsWith(`/instructor/products/${productId}/${path}`));

  return (
    <div className={page}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-[#b91c27]">
            {product.category ?? "Uncategorized"}
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{product.name}</h1>
            <StatusBadge status={product.status} />
          </div>
          <p className="mt-2 max-w-3xl text-slate-600">{product.description ?? "No description provided."}</p>
        </div>
      </div>

      <nav className="mt-6 flex flex-wrap gap-2 border-b">
        {tabs.map(([label, path]) => (
          <Link
            key={path}
            href={`/instructor/products/${productId}${path ? `/${path}` : ""}`}
            className={`rounded-t-lg px-3 py-2 text-sm ${isActive(path) ? "border border-b-white bg-white text-red-700" : "text-slate-500 hover:text-slate-700"}`}
          >
            {label}
          </Link>
        ))}
      </nav>

      {isActive("courses") && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold tracking-tight text-slate-900">Courses</h2>
          {courses.length === 0 ? (
            <EmptyState
              title="No courses yet"
              message="Create a course for this product to get started."
            />
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
                    <p className="mt-1 text-sm text-slate-500">
                      {course.category} · {course.level} · {course.duration} min
                    </p>
                    <p className="mt-3 text-sm text-slate-500">Updated {new Date(course.updated_at).toLocaleDateString()}</p>
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
      )}

      {!isActive("courses") && (
        <div className="mt-6 rounded-xl border bg-white p-6">
          <h2 className="text-lg font-semibold">Product overview</h2>
          <dl className="mt-4 grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-slate-500">Status</dt>
              <dd className="mt-1 font-medium"><StatusBadge status={product.status} /></dd>
            </div>
            <div>
              <dt className="text-sm text-slate-500">Category</dt>
              <dd className="mt-1 font-medium">{product.category ?? "Uncategorized"}</dd>
            </div>
            <div>
              <dt className="text-sm text-slate-500">Created</dt>
              <dd className="mt-1 font-medium">{new Date(product.created_at).toLocaleDateString()}</dd>
            </div>
            <div>
              <dt className="text-sm text-slate-500">Last updated</dt>
              <dd className="mt-1 font-medium">{new Date(product.updated_at).toLocaleDateString()}</dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
