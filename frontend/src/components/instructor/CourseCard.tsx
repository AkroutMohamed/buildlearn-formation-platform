import Link from "next/link";

export interface CourseCardProps {
  id: string | number;
  title: string;
  students: number;
  progress?: number;
}

export default function CourseCard({ id, title, students, progress }: CourseCardProps) {
  return (
    <article className="studio-course rounded-xl border bg-white p-5 shadow-sm">
      <h2 className="font-semibold text-gray-900">{title}</h2>
      <p className="mt-2 text-sm text-gray-500">{students} students</p>
      {progress !== undefined && <p className="mt-1 text-sm text-gray-500">{progress}% complete</p>}
      <Link href={`/instructor/courses/${id}`} className="mt-4 inline-block text-sm font-medium text-red-600 hover:underline">
        View course
      </Link>
    </article>
  );
}