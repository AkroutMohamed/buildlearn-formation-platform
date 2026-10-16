import Link from "next/link";

export interface CourseRow {
  id: string | number;
  title: string;
  students: number;
  status: string;
}

interface CourseTableProps {
  courses: CourseRow[];
}

export default function CourseTable({ courses }: CourseTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b bg-gray-50 text-gray-500">
          <tr>
            <th className="px-5 py-3 font-medium">Course</th>
            <th className="px-5 py-3 font-medium">Students</th>
            <th className="px-5 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {courses.map((course) => (
            <tr key={course.id}>
              <td className="px-5 py-4">
                <Link href={`/instructor/courses/${course.id}`} className="font-medium hover:underline">
                  {course.title}
                </Link>
              </td>
              <td className="px-5 py-4 text-gray-600">{course.students}</td>
              <td className="px-5 py-4 text-gray-600">{course.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}