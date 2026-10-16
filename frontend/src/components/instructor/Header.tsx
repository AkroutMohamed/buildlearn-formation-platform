interface HeaderProps {
  title: string;
  description?: string;
}

export default function Header({ title, description }: HeaderProps) {
  return (
    <header className="border-b bg-white px-6 py-5">
      <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
      {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
    </header>
  );
}