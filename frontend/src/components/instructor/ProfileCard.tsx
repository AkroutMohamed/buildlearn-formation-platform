export interface ProfileCardProps {
  name: string;
  email: string;
  role?: string;
}

export default function ProfileCard({ name, email, role = "Instructor" }: ProfileCardProps) {
  return (
    <article className="rounded-xl border bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold">{name}</h2>
      <p className="mt-1 text-sm text-gray-500">{role}</p>
      <p className="mt-3 text-sm text-gray-700">{email}</p>
    </article>
  );
}