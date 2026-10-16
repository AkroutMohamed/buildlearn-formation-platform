import Link from "next/link";

export default function SearchSection() {
  return (
    <section className="border-y border-slate-200 bg-white py-12">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col items-center justify-between gap-6 rounded-2xl border border-slate-200 bg-slate-50 p-8 sm:flex-row lg:px-10">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">Ready to start learning?</h2>
            <p className="mt-2 max-w-xl text-slate-600">
              Browse the full course catalog, filter by category and level, and enroll at your own pace.
            </p>
          </div>
          <Link
            href="/formations"
            className="inline-flex shrink-0 items-center justify-center rounded-lg bg-[#d81f2a] px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#b91c27]"
          >
            Browse the catalog
          </Link>
        </div>
      </div>
    </section>
  );
}