const features = [
  { title: "Expert technical training", description: "Structured construction product courses built around professional practice.", letter: "T" },
  { title: "Flexible learning", description: "Access courses anytime and anywhere, on any device.", letter: "F" },
  { title: "Track your progress", description: "Follow your advancement through lessons, quizzes, and certifications.", letter: "P" },
  { title: "Certified learning", description: "Earn a certificate after successfully completing a course.", letter: "C" },
];

export default function WhyChooseUs() {
  return (
    <section className="bg-white py-16">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="text-center">
          <p className="text-xs font-semibold uppercase tracking-wider text-[#d81f2a]">Why BuildLearn</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Built for serious learning</h2>
          <p className="mx-auto mt-3 max-w-xl text-slate-600">
            Designed to improve technical knowledge and simplify learning.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <div key={feature.title} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <span
                aria-hidden="true"
                className="grid h-11 w-11 place-items-center rounded-lg bg-red-50 text-lg font-bold text-[#d81f2a]"
              >
                {feature.letter}
              </span>
              <h3 className="mt-4 font-semibold text-slate-900">{feature.title}</h3>
              <p className="mt-1.5 text-sm text-slate-500">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}