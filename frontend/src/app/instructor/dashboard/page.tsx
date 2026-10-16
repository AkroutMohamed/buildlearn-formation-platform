"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getCourseAnalytics, getInstructorCourses } from "@/services/instructor";
import { getInstructorProducts } from "@/services/product";
import type { Course, CourseAnalytics } from "@/types/instructor";
import type { Product } from "@/types/product";
import StatCard from "@/components/ui/StatCard";
import StatusBadge from "@/components/ui/StatusBadge";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import BlueprintArt from "@/components/ui/BlueprintArt";
import Cover from "@/components/ui/Cover";

export default function InstructorDashboardPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [analytics, setAnalytics] = useState<CourseAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    Promise.all([
      getInstructorCourses(),
      getInstructorProducts(),
    ])
      .then(([items, prods]) => {
        setCourses(items);
        setProducts(prods);
        return Promise.all(
          items.map((item) => getCourseAnalytics(item.id).catch(() => null)),
        );
      })
      .then((values) => setAnalytics(values.filter((v): v is CourseAnalytics => v !== null)))
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load your dashboard."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const timer = window.setTimeout(load, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const totalStudents = analytics.reduce((sum, item) => sum + item.total_students, 0);
  const average = (key: "average_progress" | "average_quiz_score") =>
    analytics.length ? analytics.reduce((sum, item) => sum + item[key], 0) / analytics.length : 0;

  if (loading) {
    return (
      <div className="p-5 md:p-8">
        <SkeletonGrid count={4} className="h-28" />
        <div className="mt-8">
          <SkeletonGrid count={2} className="h-44" />
        </div>
      </div>
    );
  }

  if (error && courses.length === 0 && products.length === 0) {
    return (
      <div className="p-5 md:p-8">
        <ErrorState title="We could not load your dashboard" message={error} onRetry={load} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-5 md:p-8">
      <section className="studio-welcome flex flex-wrap items-center justify-between gap-6 p-7 sm:p-9">
        <div className="relative z-10"><p className="text-xs font-semibold uppercase tracking-[.18em] text-[#b3d2d0]">THE INSTRUCTOR STUDIO</p><h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Your knowledge.<br />Their next step.</h1><p className="mt-3 max-w-md text-sm leading-6 text-slate-300">Shape useful lessons, guide your learners and turn product expertise into progress.</p></div>
        <Link href="/instructor/courses" className="studio-primary relative z-10">Manage your courses <span aria-hidden="true">&#8599;</span></Link>
      </section>

      {error && <ErrorState title="Some data could not be loaded" message={error} onRetry={load} />}

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-5">
        <StatCard label="Assigned products" value={products.length} />
        <StatCard label="Total courses" value={courses.length} />
        <StatCard label="Published courses" value={courses.filter((c) => c.status === "Published").length} />
        <StatCard label="Enrolled students" value={totalStudents} />
        <StatCard label="Average progress" value={`${average("average_progress").toFixed(1)}%`} />
      </section>

      <section>
        <h2 className="text-xl font-semibold tracking-tight text-slate-900">My products</h2>

        {products.length === 0 ? (
          <div className="mt-4">
            <EmptyState
              title="No products yet"
              message="You are not assigned to any products yet. Contact an administrator."
            />
          </div>
        ) : (
          <div className="mt-4 grid gap-5 md:grid-cols-2">
            {products.map((product) => (
              <article
                key={product.id}
                className="studio-course flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
              >
                <div className="flex h-40 items-center justify-center overflow-hidden bg-[#172b3a]">
                  <BlueprintArt category={product.category ?? "Gypstant"} className="h-full w-full" />
                </div>
                <div className="flex flex-1 flex-col p-5">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-semibold text-slate-900">{product.name}</h3>
                    <StatusBadge status={product.status} />
                  </div>
                  <p className="mt-1 text-sm text-slate-500">{product.category ?? "Uncategorized"}</p>
                  <p className="mt-3 text-sm text-slate-500">Updated {new Date(product.updated_at).toLocaleDateString()}</p>
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
      </section>

      <section>
        <h2 className="text-xl font-semibold tracking-tight text-slate-900">My courses</h2>

        {courses.length === 0 ? (
          <div className="mt-4">
            <EmptyState
              title="No courses yet"
              message="Create a course within one of your assigned products to get started."
            />
          </div>
        ) : (
          <div className="mt-4 grid gap-5 md:grid-cols-2">
            {courses.map((course) => (
              <article
                key={course.id}
                className="studio-course flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
              >
                <div className="flex h-36 items-center justify-center overflow-hidden bg-slate-100">
                  {course.thumbnail ? <Cover src={course.thumbnail} /> : (
                    <BlueprintArt category={course.category} className="h-full w-full" />
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
                      href={`/instructor/courses/${course.id}/analytics`}
                      className="inline-flex flex-1 items-center justify-center rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      Analytics
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
