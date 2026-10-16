import Link from "next/link";
import BlueprintArt from "@/components/ui/BlueprintArt";
import Badge from "@/components/ui/Badge";
import Cover from "@/components/ui/Cover";

interface FormationCardProps {
  id: string;
  title: string;
  description: string;
  thumbnail: string | null;
  category: string;
  level: string;
  language: string;
  duration: number;
  instructor: string;
  basePath?: string;
}

const levelTone: Record<string, "neutral" | "success" | "warning" | "danger"> = {
  Beginner: "success",
  Intermediate: "warning",
  Advanced: "danger",
};

export default function FormationCard({
  id,
  title,
  description,
  thumbnail,
  category,
  level,
  language,
  duration,
  instructor,
  basePath = "/student/courses",
}: FormationCardProps) {
  const coursePath = `${basePath}/${id}`;
  return (
    <article className="studio-course group flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:border-red-200 hover:shadow-md">
      <Link href={coursePath} className="flex h-44 items-center justify-center overflow-hidden bg-[#172b3a]" aria-label={`View ${title}`}>
        {thumbnail ? <Cover src={thumbnail} /> : (
          <BlueprintArt category={category} className="h-full w-full" />
        )}
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-[#b91c27]">{category}</span>
          <Badge tone={levelTone[level] ?? "neutral"}>{level}</Badge>
        </div>
        <h3 className="mt-2 text-lg font-semibold leading-snug text-slate-900">
          <Link href={coursePath} className="hover:underline">
            {title}
          </Link>
        </h3>
        <p className="mt-1.5 line-clamp-2 text-sm text-slate-500">{description}</p>
        <dl className="mt-4 space-y-1 text-sm text-slate-500">
          <div className="flex justify-between gap-2">
            <dt className="text-slate-400">Instructor</dt>
            <dd className="truncate font-medium text-slate-600">{instructor}</dd>
          </div>
          <div className="flex justify-between gap-2">
            <dt className="text-slate-400">Duration</dt>
            <dd className="font-medium text-slate-600">{duration} min</dd>
          </div>
          <div className="flex justify-between gap-2">
            <dt className="text-slate-400">Language</dt>
            <dd className="font-medium text-slate-600">{language || "—"}</dd>
          </div>
        </dl>
        <Link
          href={coursePath}
          className="studio-secondary mt-5 justify-between"
        >
          Explore this course <span aria-hidden="true">&#8599;</span>
        </Link>
      </div>
    </article>
  );
}
