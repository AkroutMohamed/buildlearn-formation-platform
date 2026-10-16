"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { studentLearning } from "@/services/student-learning.service";
import type { Certificate } from "@/types/learning";
import PageHeader from "@/components/ui/PageHeader";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import { SkeletonGrid } from "@/components/ui/LoadingSkeleton";

export default function CertificatesPage() {
  const [certificates, setCertificates] = useState<Certificate[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    studentLearning
      .certificates()
      .then(setCertificates)
      .catch((e) => {
        setCertificates([]);
        setError(e instanceof Error ? e.message : "Unable to load your certificates.");
      });
  }, []);

  if (certificates === null) {
    return (
      <div className="space-y-8">
        <div className="space-y-3">
          <div className="h-3 w-24 animate-pulse rounded bg-slate-200" />
          <div className="h-7 w-56 animate-pulse rounded bg-slate-200" />
        </div>
        <SkeletonGrid count={2} className="h-44" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Credentials"
        title="My certificates"
        description="Certificates you earned by completing courses."
      />

      {error && <ErrorState title="Could not load your certificates" message={error} />}

      {certificates.length === 0 && !error ? (
        <EmptyState
          title="No certificates yet"
          message="Complete a course to earn your first BuildLearn certificate."
          action={
            <Link
              href="/student/formations"
              className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
            >
              Browse courses
            </Link>
          }
        />
      ) : (
        <div className="grid gap-5 md:grid-cols-2">
          {certificates.map((c) => (
            <article key={c.id} className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="flex items-center justify-between gap-3 bg-gradient-to-r from-[#d81f2a] to-[#b91c27] px-5 py-4">
                <p className="text-sm font-semibold text-white">BuildLearn certificate</p>
                <span aria-hidden="true" className="text-3xl text-white/70">★</span>
              </div>
              <div className="p-5">
                <h2 className="text-xl font-semibold text-slate-900">{c.course_title}</h2>
                <dl className="mt-4 space-y-1.5 text-sm text-slate-600">
                  <div>
                    <dt className="inline font-medium text-slate-800">Issued: </dt>
                    <dd className="inline">{new Date(c.issued_at).toLocaleDateString()}</dd>
                  </div>
                  <div>
                    <dt className="inline font-medium text-slate-800">Certificate ID: </dt>
                    <dd className="inline break-all text-xs">{c.id}</dd>
                  </div>
                </dl>
                {c.certificate_url && (
                  <a
                    href={c.certificate_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-5 inline-block rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    View certificate
                  </a>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
