import Link from "next/link";

export default function CTA() {
  return (
    <section className="bg-[#d81f2a] py-16">
      <div className="mx-auto max-w-4xl px-6 text-center text-white">
        <h2 className="text-3xl font-bold leading-tight tracking-tight sm:text-4xl">
          Start your technical learning journey today
        </h2>
        <p className="mt-5 text-lg text-red-50">
          Access professional construction product training, improve your skills, and earn certifications.
        </p>
        <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
          <Link
            href="/register"
            className="inline-flex items-center justify-center rounded-lg bg-white px-8 py-3 font-semibold text-[#b91c27] shadow-sm transition hover:bg-slate-100"
          >
            Get started
          </Link>
          <Link
              href="/formations"
            className="inline-flex items-center justify-center rounded-lg border border-white px-8 py-3 font-semibold text-white transition hover:bg-[#b91c27]"
          >
            Browse formations
          </Link>
        </div>
      </div>
    </section>
  );
}
