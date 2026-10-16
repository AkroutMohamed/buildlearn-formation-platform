export interface StudentRow {
  id: string | number;
  name: string;
  email: string;
  courses: number;
}

interface StudentTableProps {
  students: StudentRow[];
}

export default function StudentTable({ students }: StudentTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b bg-gray-50 text-gray-500">
          <tr>
            <th className="px-5 py-3 font-medium">Student</th>
            <th className="px-5 py-3 font-medium">Email</th>
            <th className="px-5 py-3 font-medium">Courses</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {students.map((student) => (
            <tr key={student.id}>
              <td className="px-5 py-4 font-medium">{student.name}</td>
              <td className="px-5 py-4 text-gray-600">{student.email}</td>
              <td className="px-5 py-4 text-gray-600">{student.courses}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}