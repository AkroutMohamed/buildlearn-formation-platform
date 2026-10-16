import Link from "next/link";

const categories = [
  { title: "Outillage", description: "Learn about tools, machines, and construction equipment.", letter: "O" },
  { title: "Étanchéité", description: "Discover waterproofing systems, membranes, and sealing products.", letter: "É" },
  { title: "Gypstant", description: "Explore gypsum products, partitions, ceilings, and finishes.", letter: "G" },
];

export default function Categories() {
  return (
    <section className="bg-slate-50 py-16">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="text-center">
          <p className="text-xs font-semibold uppercase tracking-wider text-[#d81f2a]">Product families</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Explore categories</h2>
          <p className="mx-auto mt-3 max-w-xl text-slate-600">
            Browse technical formations by product family.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {categories.map((category) => (
            <Link
              key={category.title}
              href="/formations"
              className="studio-course group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-red-200 hover:shadow-md"
            >
              <span
                aria-hidden="true"
                className="grid h-12 w-12 place-items-center rounded-lg bg-red-50 text-xl font-bold text-[#d81f2a]"
              >
                {category.letter}
              </span>
              <h3 className="mt-4 text-lg font-semibold text-slate-900">{category.title}</h3>
              <p className="mt-1.5 text-sm text-slate-500">{category.description}</p>
              <span className="mt-4 inline-block text-sm font-semibold text-[#b91c27] transition group-hover:underline">
                View courses →
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
