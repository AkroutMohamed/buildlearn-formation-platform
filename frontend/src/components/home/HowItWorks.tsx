const steps = [
  {
    number: "01",
    title: "Create an Account",
    description:
      "Sign up and create your personal learning profile.",
  },
  {
    number: "02",
    title: "Choose a Formation",
    description:
      "Browse categories and select the technical training you need.",
  },
  {
    number: "03",
    title: "Learn & Practice",
    description:
      "Watch videos, read resources, and complete lessons step by step.",
  },
  {
    number: "04",
    title: "Pass Quizzes",
    description:
      "Test your knowledge and validate your understanding.",
  },
  {
    number: "05",
    title: "Get Certified",
    description:
      "Earn your certificate after completing the formation successfully.",
  },
];

export default function HowItWorks() {
  return (
    <section className="bg-slate-50 py-16">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="text-center">
          <p className="text-xs font-semibold uppercase tracking-wider text-[#d81f2a]">How it works</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Start learning in a few simple steps</h2>
        </div>

        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
          {steps.map((step) => (
            <div key={step.number} className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <span
                aria-hidden="true"
                className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-red-50 text-base font-bold text-[#d81f2a]"
              >
                {step.number}
              </span>
              <h3 className="mt-4 font-semibold text-slate-900">{step.title}</h3>
              <p className="mt-1.5 text-sm text-slate-500">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}