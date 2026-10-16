"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { updateCourse } from "@/services/instructor";
import type { Course, CourseInput } from "@/types/instructor";

export default function CourseForm({ course }: { course: Course }) {
  const router = useRouter();
  const [form, setForm] = useState<CourseInput>({
    title: course.title,
    description: course.description,
    objectives: course.objectives ?? "",
    thumbnail: course.thumbnail ?? "",
    language: course.language,
    duration: course.duration,
    category: course.category,
    level: course.level,
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const change = (key: keyof CourseInput, value: string | number) =>
    setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    if (form.title.trim().length < 3 || form.description.trim().length < 10)
      return setError("Add a title (3+ characters) and a description (10+ characters).");
    if (!Number.isInteger(form.duration) || form.duration < 0) return setError("Duration must be a whole number of minutes, zero or greater.");
    if (!form.language.trim()) return setError("Specify the course language.");
    setSaving(true);
    try {
      const result = await updateCourse(course.id, { ...form, title: form.title.trim(), description: form.description.trim(), language: form.language.trim(), thumbnail: form.thumbnail?.trim() || null });
      router.push(`/instructor/courses/${result.id}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to save the course.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-5 rounded-2xl border bg-white p-6 shadow-sm">
      <div className="grid gap-5 md:grid-cols-2">
        <Field label="Course title" value={form.title} onChange={(v) => change("title", v)} required />
        <Field label="Thumbnail URL" value={form.thumbnail ?? ""} onChange={(v) => change("thumbnail", v)} />
        <div className="md:col-span-2">
          <Field label="Description" value={form.description} onChange={(v) => change("description", v)} multiline required />
        </div>
        <div className="md:col-span-2">
          <Field label="Learning objectives" value={form.objectives ?? ""} onChange={(v) => change("objectives", v)} multiline />
        </div>
        <Field label="Language" value={form.language} onChange={(v) => change("language", v)} />
        <Field label="Duration (minutes)" value={String(form.duration)} onChange={(v) => change("duration", Number(v))} type="number" />
        <Select label="Category" value={form.category} options={["Outillage", "Étanchéité", "Gypstant"]} onChange={(v) => change("category", v)} />
        <Select label="Level" value={form.level} options={["Beginner", "Intermediate", "Advanced"]} onChange={(v) => change("level", v)} />
      </div>
      {error && <p role="alert" className="rounded bg-red-50 p-4 text-sm text-red-700">{error}</p>}
      <button type="submit" disabled={saving} className="rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white hover:bg-[#b91c27] disabled:opacity-50">
        {saving ? "Saving..." : "Save changes"}
      </button>
      <Link href={`/instructor/courses/${course.id}`} className="ml-3 inline-block rounded-lg border px-4 py-2 text-sm font-medium text-slate-700">Cancel</Link>
    </form>
  );
}

function Field({ label, value, onChange, multiline, type = "text", required }: { label: string; value: string; onChange: (value: string) => void; multiline?: boolean; type?: string; required?: boolean }) {
  const classes = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-red-500";
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      {multiline ? (
        <textarea className={classes} rows={4} value={value} onChange={(e) => onChange(e.target.value)} required={required} />
      ) : (
        <input className={classes} type={type} min={type === "number" ? 0 : undefined} value={value} onChange={(e) => onChange(e.target.value)} required={required} />
      )}
    </label>
  );
}

function Select({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      <select className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
