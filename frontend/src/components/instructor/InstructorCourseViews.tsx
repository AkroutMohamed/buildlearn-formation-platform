"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useEffectEvent, useRef, useState } from "react";
import * as api from "@/services/instructor";
import StatusBadge from "@/components/ui/StatusBadge";
import LocalVideoUploads from "@/components/instructor/LocalVideoUploads";
import type { CourseAnalytics, EnrolledStudent, Lesson, LiveSession, Module, Quiz, RecordedVideo } from "@/types/instructor";

const page = "mx-auto max-w-6xl p-5 md:p-8";
const button = "rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50";

function State({ error, loading, empty }: { error: string; loading: boolean; empty?: boolean }) {
  return (
    <>
      {loading && <p className="rounded-xl bg-white p-5 text-slate-500">Loading…</p>}
      {error && <p role="alert" className="rounded-xl bg-red-50 p-4 text-red-700">{error}</p>}
      {!loading && !error && empty && <p className="rounded-xl border border-dashed bg-white p-8 text-center text-slate-500">Nothing has been added yet.</p>}
    </>
  );
}

function useData<T>(load: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const run = useEffectEvent(() => {
    load().then(setData).catch((e) => setError(e instanceof Error ? e.message : "Unable to load this information.")).finally(() => setLoading(false));
  });
  const reload = () => {
    setLoading(true);
    setError("");
    load().then(setData).catch((e) => setError(e instanceof Error ? e.message : "Unable to load this information.")).finally(() => setLoading(false));
  };
  useEffect(() => {
    const timer = window.setTimeout(run, 0);
    return () => window.clearTimeout(timer);
  }, []);
  return { data, error, loading, reload };
}

export function CourseOverview({ courseId }: { courseId: string }) {
  const { data: course, error, loading, reload } = useData(() => api.getCourse(courseId));
  const quizzes = useData(() => api.getQuizzes(courseId));
  const analytics = useData(() => api.getCourseAnalytics(courseId));
  const pathname = usePathname();
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");
  if (loading || error || !course) return <div className={page}><State loading={loading} error={error} /></div>;
  const publish = async () => {
    setBusy(true);
    setActionError("");
    try {
      await api.setCoursePublished(courseId, course.status !== "Published");
      reload();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "Could not update the course.");
    } finally {
      setBusy(false);
    }
  };
  const remove = async () => {
    if (!window.confirm(`Delete "${course.title}"? This cannot be undone.`)) return;
    setBusy(true);
    setActionError("");
    try {
      await api.deleteCourse(courseId);
      window.location.href = "/instructor/courses";
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "Could not delete the course.");
    } finally {
      setBusy(false);
    }
  };
  const tabs: [string, string][] = [
    ["Overview", ""],
    ["Modules & lessons", "modules"],
    ["Quizzes", "quizzes"],
    ["Students", "students"],
    ["Analytics", "analytics"],
    ["Certificates", "certificates"],
  ];
  const isActive = (path: string) => (path === "" ? pathname === `/instructor/courses/${courseId}` : pathname.startsWith(`/instructor/courses/${courseId}/${path}`));
  return (
    <div className={page}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-[#b91c27]">{course.category} · {course.level}</p>
          <div className="mt-1 flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{course.title}</h1>
            <StatusBadge status={course.status} />
          </div>
          <p className="mt-2 max-w-3xl text-slate-600">{course.description}</p>
        </div>
        <div className="flex flex-wrap items-start gap-2">
          {actionError && <p role="alert" className="w-full text-sm text-red-700">{actionError}</p>}
          <button onClick={publish} disabled={busy} className="rounded-lg border px-3 py-2 text-sm">
            {course.status === "Published" ? "Unpublish" : "Publish"}
          </button>
          <button onClick={remove} disabled={busy} className="rounded-lg border border-red-200 px-3 py-2 text-sm text-red-700">
            Delete
          </button>
        </div>
      </div>
      <nav className="mt-6 flex flex-wrap gap-2 border-b">
        {tabs.map(([label, path]) => (
          <Link
            key={path}
            href={`/instructor/courses/${courseId}${path ? `/${path}` : ""}`}
            className={`rounded-t-lg px-3 py-2 text-sm ${isActive(path) ? "border border-b-white bg-white text-red-700" : "text-slate-500 hover:text-slate-700"}`}
          >
            {label}
          </Link>
        ))}
      </nav>
      <div className="mt-6 space-y-6">
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {[
            ["Modules", course.modules.length],
            ["Lessons", course.modules.reduce((total, module) => total + module.lesson_count, 0)],
            ["Quizzes", quizzes.loading ? "Loading…" : quizzes.error ? "Unavailable" : quizzes.data?.length ?? "Unavailable"],
            ["Enrolled students", analytics.loading ? "Loading…" : analytics.error ? "Unavailable" : analytics.data?.total_students ?? "Unavailable"],
            ["Completion rate", analytics.loading ? "Loading…" : analytics.error || !analytics.data ? "Unavailable" : `${analytics.data.completion_rate.toFixed(1)}%`],
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl border border-slate-200 bg-white p-5">
              <dt className="text-sm text-slate-500">{label}</dt>
              <dd className="mt-2 text-2xl font-semibold text-slate-900">{value}</dd>
            </div>
          ))}
        </dl>
        {[quizzes, analytics].map((result, index) => result.error && (
          <div key={index} role="alert" className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-700">
            <span>{index === 0 ? "Quiz statistics" : "Student statistics"} could not be loaded: {result.error}</span>
            <button type="button" onClick={result.reload} disabled={result.loading} className="font-semibold underline disabled:opacity-50">Retry</button>
          </div>
        ))}
        <div className="grid items-start gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <section className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="text-lg font-semibold text-slate-900">Learning objectives</h2>
              <p className="mt-3 whitespace-pre-line text-sm leading-6 text-slate-600">
                {course.objectives?.trim() || "Learning objectives have not been added yet."}
              </p>
            </section>
            <section className="rounded-xl border border-slate-200 bg-white p-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-lg font-semibold text-slate-900">Course outline</h2>
                <Link href={`/instructor/courses/${courseId}/modules`} className="text-sm font-medium text-red-700 hover:underline">Manage modules</Link>
              </div>
              {course.modules.length === 0 ? (
                <p className="mt-4 rounded-lg border border-dashed border-slate-200 p-5 text-sm text-slate-500">No modules yet. Add a module to start building your course.</p>
              ) : (
                <ol className="mt-4 divide-y divide-slate-100">
                  {[...course.modules].sort((a, b) => a.order_index - b.order_index || a.id.localeCompare(b.id)).map((module, index) => (
                    <li key={module.id} className="flex items-center justify-between gap-4 py-3">
                      <span className="text-sm font-medium text-slate-800">{index + 1}. {module.title}</span>
                      <span className="shrink-0 text-sm text-slate-500">{module.lesson_count} {module.lesson_count === 1 ? "lesson" : "lessons"}</span>
                    </li>
                  ))}
                </ol>
              )}
            </section>
          </div>
          <div className="space-y-6">
            <section className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="text-lg font-semibold text-slate-900">Course details</h2>
              <dl className="mt-4 space-y-3 text-sm">
                {[
                  ["Category", course.category],
                  ["Level", course.level],
                  ["Language", course.language || "Not specified"],
                  ["Duration", course.duration > 0 ? `${course.duration} minutes` : "Not specified"],
                  ["Linked product", course.product?.name || (course.product_id ? "Unavailable" : "No linked product")],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between gap-4">
                    <dt className="text-slate-500">{label}</dt>
                    <dd className="text-right font-medium text-slate-800">{value}</dd>
                  </div>
                ))}
              </dl>
            </section>
            <section className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="text-lg font-semibold text-slate-900">Quick actions</h2>
              <div className="mt-4 grid gap-2">
                {[["Edit course", "edit"], ["Manage lessons", "modules"], ["Manage quizzes", "quizzes"], ["View students", "students"]].map(([label, path]) => (
                  <Link key={path} href={`/instructor/courses/${courseId}/${path}`} className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:border-red-200 hover:bg-red-50 hover:text-red-700">{label}</Link>
                ))}
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ModulesView({ courseId }: { courseId: string }) {
  const { data, error, loading, reload } = useData(() => api.getModules(courseId));
  const [title, setTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");
  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    if (busy) return;
    setBusy(true); setActionError("");
    try {
      await api.createModule(courseId, { title: title.trim(), description: null, order_index: Math.max(-1, ...(data ?? []).map((item) => item.order_index)) + 1 });
      setTitle(""); reload();
    } catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to add module."); }
    finally { setBusy(false); }
  };
  const remove = async (item: Module) => {
    if (!busy && confirm(`Delete "${item.title}" and its lessons? This cannot be undone.`)) {
      setBusy(true); setActionError("");
      try { await api.deleteModule(courseId, item.id); reload(); }
      catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to delete module."); }
      finally { setBusy(false); }
    }
  };
  return (
    <div className={page}>
      <h1 className="text-3xl font-bold">Modules & lessons</h1>
      <form onSubmit={add} className="mt-6 flex gap-2">
        <input aria-label="New module title" required className="min-w-0 w-full rounded-lg border px-3 py-2" placeholder="New module title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <button disabled={busy || loading || !!error || !title.trim()} className={button}>{busy ? "Saving…" : "Add module"}</button>
      </form>
      <div className="mt-6">
        {actionError && <p role="alert" className="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">{actionError}</p>}
        <State loading={loading} error={error} empty={data?.length === 0} />
        {data?.map((item) => (
          <article key={item.id} className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-white p-4">
            <div>
              <h2 className="font-semibold">{item.order_index + 1}. {item.title}</h2>
              <p className="text-sm text-slate-500">{item.description ?? "No description"}</p>
            </div>
            <div className="flex gap-2">
              <Link className="rounded-lg border px-3 py-2 text-sm" href={`/instructor/courses/${courseId}/lessons?module=${item.id}`}>
                Lessons
              </Link>
              <button disabled={busy} className="rounded-lg border border-red-200 px-3 py-2 text-sm text-red-700 disabled:opacity-50" onClick={() => remove(item)}>
                Delete
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

export function LessonsView({ courseId, moduleId }: { courseId: string; moduleId: string }) {
  const { data, error, loading, reload } = useData(() => api.getLessons(courseId, moduleId));
  const [title, setTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");
  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    if (busy) return;
    setBusy(true); setActionError("");
    try {
      await api.createLesson(courseId, moduleId, { title: title.trim(), content: null, duration_minutes: 0, order_index: Math.max(-1, ...(data ?? []).map((item) => item.order_index)) + 1, is_published: false });
      setTitle(""); reload();
    } catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to add lesson."); }
    finally { setBusy(false); }
  };
  return (
    <div className={page}>
      <h1 className="text-3xl font-bold">Lessons</h1>
      <form onSubmit={add} className="mt-6 flex gap-2">
        <input aria-label="New lesson title" required className="min-w-0 w-full rounded-lg border px-3 py-2" placeholder="New lesson title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <button disabled={busy || loading || !!error || !title.trim()} className={button}>{busy ? "Saving…" : "Add lesson"}</button>
      </form>
      <div className="mt-6">
        {actionError && <p role="alert" className="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">{actionError}</p>}
        <State loading={loading} error={error} empty={data?.length === 0} />
        {data?.map((item: Lesson) => (
          <article key={item.id} className="mt-3 rounded-xl border bg-white p-4">
            <div className="flex justify-between gap-3">
              <div>
                <h2 className="font-semibold">{item.order_index + 1}. {item.title}</h2>
                <p className="text-sm text-slate-500">{item.content ?? "No lesson content yet"}</p>
              </div>
              <button disabled={busy} className="text-sm text-red-700 disabled:opacity-50" onClick={async () => {
                if (busy || !confirm("Delete this lesson and its attached material? This cannot be undone.")) return;
                setBusy(true); setActionError("");
                try { await api.deleteLesson(courseId, moduleId, item.id); reload(); }
                catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to delete lesson."); }
                finally { setBusy(false); }
              }}>
                Delete
              </button>
            </div>
            <LessonEditor key={`${item.id}:${item.title}:${item.content}:${item.duration_minutes}:${item.is_published}`} courseId={courseId} moduleId={moduleId} lesson={item} onSaved={reload} />
            <ResourceManager courseId={courseId} lessonId={item.id} />
            <VideoManager courseId={courseId} lessonId={item.id} />
            <LiveSessionManager courseId={courseId} lessonId={item.id} />
          </article>
        ))}
      </div>
    </div>
  );
}

function LessonEditor({ courseId, moduleId, lesson, onSaved }: { courseId: string; moduleId: string; lesson: Lesson; onSaved: () => void }) {
  const [form, setForm] = useState({ title: lesson.title, content: lesson.content ?? "", duration_minutes: lesson.duration_minutes ?? 0, is_published: lesson.is_published });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (busy) return;
    setError("");
    if (!form.title.trim() || !Number.isInteger(form.duration_minutes) || form.duration_minutes < 0) { setError("Enter a title and a whole, non-negative duration in minutes."); return; }
    setBusy(true);
    try { await api.updateLesson(courseId, moduleId, lesson.id, { ...form, title: form.title.trim() }); onSaved(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to save lesson. Your edits are preserved."); }
    finally { setBusy(false); }
  };
  const input = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2";
  return <details className="mt-4 rounded-lg border border-slate-200 p-3">
    <summary className="cursor-pointer text-sm font-semibold text-red-700">Edit lesson · {lesson.is_published ? "Published" : "Draft"}</summary>
    <form onSubmit={save} className="mt-4 space-y-3">
      <label className="block text-sm font-medium">Lesson title<input required className={input} value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} /></label>
      <label className="block text-sm font-medium">Lesson content<textarea rows={6} className={input} value={form.content} onChange={(event) => setForm({ ...form, content: event.target.value })} /></label>
      <label className="block text-sm font-medium">Duration (minutes)<input type="number" min={0} step={1} required className={input} value={form.duration_minutes} onChange={(event) => setForm({ ...form, duration_minutes: Number(event.target.value) })} /></label>
      <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_published} onChange={(event) => setForm({ ...form, is_published: event.target.checked })} />Publish lesson for enrolled students</label>
      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      <button disabled={busy} className={button}>{busy ? "Saving…" : "Save lesson"}</button>
    </form>
  </details>;
}

function ResourceManager({ courseId, lessonId }: { courseId: string; lessonId: string }) {
  type Selected = { id: string; file: File; status: "ready" | "uploading" | "uploaded" | "failed"; error: string };
  const [files, setFiles] = useState<Selected[]>([]);
  const [busy, setBusy] = useState(false);
  const picker = useRef<HTMLInputElement>(null);
  const running = useRef(false);
  const valid = (file: File) => file.size > 0 && file.size <= 10 * 1024 * 1024 && /\.(pdf|jpg|jpeg|png|webp|txt)$/i.test(file.name);
  const choose = (selected: FileList | null) => {
    if (!selected || running.current) return;
    const additions = Array.from(selected).map((file): Selected => ({ id: `${file.name}:${file.size}:${file.lastModified}`, file, status: valid(file) ? "ready" : "failed", error: valid(file) ? "" : "Choose a non-empty PDF, image, or TXT file up to 10 MB." }));
    setFiles((current) => [...current, ...additions.filter((item, index) => !current.some((existing) => existing.id === item.id) && additions.findIndex((other) => other.id === item.id) === index)]);
    if (picker.current) picker.current.value = "";
  };
  const upload = async () => {
    if (running.current) return;
    running.current = true; setBusy(true);
    for (const item of files.filter((item) => item.status !== "uploaded" && valid(item.file))) {
      setFiles((current) => current.map((value) => value.id === item.id ? { ...value, status: "uploading", error: "" } : value));
      const form = new FormData(); form.append("file", item.file); form.append("title", item.file.name);
      try {
        await api.uploadResource(courseId, lessonId, form);
        setFiles((current) => current.map((value) => value.id === item.id ? { ...value, status: "uploaded" } : value));
      } catch (error) {
        setFiles((current) => current.map((value) => value.id === item.id ? { ...value, status: "failed", error: error instanceof Error ? error.message : "Upload failed. Try again." } : value));
      }
    }
    running.current = false; setBusy(false);
  };
  const pending = files.filter((item) => item.status !== "uploaded" && valid(item.file)).length;
  return (
    <section className="mt-4 space-y-3 border-t pt-4" aria-label="Lesson resource uploads">
      <h3 className="text-sm font-semibold text-slate-700">Lesson resources</h3>
      <div onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); choose(event.dataTransfer.files); }} className="rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-5 text-center">
        <p className="text-sm text-slate-600">Drag files here or choose several files from your computer.</p>
        <input ref={picker} type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.webp,.txt" className="hidden" onChange={(event) => choose(event.target.files)} aria-label="Choose resource files" />
        <button type="button" disabled={busy} onClick={() => picker.current?.click()} className="mt-3 rounded-lg bg-red-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50">Choose files</button>
        <p className="mt-3 text-xs text-slate-500">PDF, JPG, PNG, WebP, TXT · up to 10 MB per file</p>
      </div>
      {files.map((item) => <div key={item.id} className="rounded-lg border bg-white p-3">
        <div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="break-all text-sm font-medium">{item.file.name}</p><p className="text-xs text-slate-500">{(item.file.size / 1024 / 1024).toFixed(1)} MB · {item.status === "ready" ? "Ready to upload" : item.status === "uploading" ? "Uploading…" : item.status === "uploaded" ? "Uploaded" : "Needs attention"}</p></div><button type="button" disabled={busy} aria-label={`Remove ${item.file.name} from selection`} onClick={() => setFiles((current) => current.filter((value) => value.id !== item.id))} className="rounded border px-2 py-1 text-xs disabled:opacity-50">{item.status === "uploaded" ? "Dismiss" : "Remove"}</button></div>
        {item.error && <p role="alert" className="mt-2 text-sm text-red-700">{item.error}</p>}
      </div>)}
      {files.length > 0 && <div className="flex flex-wrap items-center gap-3"><button type="button" disabled={busy || !pending} onClick={() => void upload()} className="rounded-lg bg-red-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{busy ? "Uploading files…" : `Upload ${pending} file${pending === 1 ? "" : "s"}`}</button><p role="status" className="text-sm text-slate-500">{files.filter((item) => item.status === "uploaded").length} of {files.length} selected files uploaded</p></div>}
    </section>
  );
}

function VideoManager({ courseId, lessonId }: { courseId: string; lessonId: string }) {
  const { data: video, error, loading, reload } = useData(() => api.getVideo(courseId, lessonId));
  const [form, setForm] = useState({ title: "", description: "", video_url: "", duration_seconds: "", thumbnail_url: "" });
  const [message, setMessage] = useState("");
  const [mode, setMode] = useState<"file" | "url">("file");
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    if (busy) return;
    setMessage("");
    setFailed(false);
    const duration = form.duration_seconds ? Number(form.duration_seconds) : null;
    if (duration !== null && (!Number.isInteger(duration) || duration < 0)) { setFailed(true); setMessage("Enter a whole, non-negative duration in seconds."); return; }
    setBusy(true);
    try {
      const data: Record<string, unknown> = {
        title: form.title.trim(),
        description: form.description || null,
        video_url: form.video_url,
        duration_seconds: duration,
        thumbnail_url: form.thumbnail_url || null,
      };
      if (video) {
        await api.updateVideo(courseId, lessonId, data);
        setMessage("Video updated.");
      } else {
        await api.createVideo(courseId, lessonId, data);
        setMessage("Video added.");
      }
      reload();
    } catch (err) {
      setFailed(true);
      setMessage(err instanceof Error ? err.message : "Failed to save video.");
    } finally {
      setBusy(false);
    }
  };

  const remove = async () => {
    if (busy || !confirm("Delete this video?")) return;
    setBusy(true); setFailed(false);
    try {
      await api.deleteVideo(courseId, lessonId);
      setMessage("Video deleted.");
      setForm({ title: "", description: "", video_url: "", duration_seconds: "", thumbnail_url: "" });
      reload();
    } catch (err) {
      setFailed(true);
      setMessage(err instanceof Error ? err.message : "Failed to delete video.");
    } finally {
      setBusy(false);
    }
  };

  const fillForm = (v: RecordedVideo) => {
    setMode("url");
    setForm({
      title: v.title,
      description: v.description ?? "",
      video_url: v.video_url,
      duration_seconds: v.duration_seconds != null ? String(v.duration_seconds) : "",
      thumbnail_url: v.thumbnail_url ?? "",
    });
  };

  return (
    <div className="mt-4 border-t pt-3">
      <h3 className="text-sm font-semibold text-slate-700">🎥 Recorded Video</h3>
      {loading && <p className="mt-2 text-sm text-slate-500">Loading video…</p>}
      {error && <p role="alert" className="mt-2 text-sm text-red-700">{error}</p>}
      {!loading && !error && !video && <p className="mt-2 text-sm text-slate-500">No recorded video yet. Upload a local file or add a video URL.</p>}
      {video && !loading && (
        <div className="mt-2 rounded-lg border bg-slate-50 p-3">
          <p className="text-sm font-medium">{video.title}</p>
          <p className="text-xs text-slate-500">{video.description}</p>
          <p className="mt-1 text-xs text-slate-400">{video.video_url}</p>
          <div className="mt-2 flex gap-2">
            <button disabled={busy} type="button" onClick={() => fillForm(video)} className="rounded border px-2 py-1 text-xs">Edit details</button>
            <button disabled={busy} type="button" onClick={remove} className="rounded border border-red-200 px-2 py-1 text-xs text-red-700">Delete</button>
          </div>
        </div>
      )}
      <div className="mt-3 flex gap-3">
        <button type="button" disabled={busy} onClick={() => setMode("file")} aria-pressed={mode === "file"} className={`rounded-lg border px-3 py-2 text-sm ${mode === "file" ? "border-red-300 bg-red-50 text-red-700" : ""}`}>Upload local videos</button>
        <button type="button" disabled={busy} onClick={() => setMode("url")} aria-pressed={mode === "url"} className={`rounded-lg border px-3 py-2 text-sm ${mode === "url" ? "border-red-300 bg-red-50 text-red-700" : ""}`}>Use a URL / edit primary video</button>
      </div>
      {mode === "file" ? <LocalVideoUploads courseId={courseId} lessonId={lessonId} /> : <form onSubmit={save} className="mt-3 space-y-3">
        <fieldset disabled={busy || loading || !!error} className="space-y-3">
          <legend className="text-sm font-medium">Video source</legend>
          <label className="block text-sm">Title<input required maxLength={200} className="mt-1 block w-full max-w-md rounded border px-3 py-2" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></label>
          <label className="block text-sm">Video URL<input required className="mt-1 block w-full max-w-xl rounded border px-3 py-2" placeholder="https://?" value={form.video_url} onChange={(e) => setForm({ ...form, video_url: e.target.value })} /></label>
          <label className="block text-sm">Duration in seconds (optional)<input className="mt-1 block w-40 rounded border px-3 py-2" type="number" min="0" step="1" value={form.duration_seconds} onChange={(e) => setForm({ ...form, duration_seconds: e.target.value })} /></label>
          {mode === "url" && <label className="block text-sm">Thumbnail URL (optional)<input className="mt-1 block w-full max-w-xl rounded border px-3 py-2" value={form.thumbnail_url} onChange={(e) => setForm({ ...form, thumbnail_url: e.target.value })} /></label>}
          <button disabled={busy} className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">{busy ? "Saving..." : video ? "Update video" : "Add video"}</button>
        </fieldset>
        {message && <p role={failed ? "alert" : "status"} className={`text-sm ${failed ? "text-red-700" : "text-emerald-700"}`}>{message}</p>}
      </form>}
    </div>
  );
}

function LiveSessionManager({ courseId, lessonId }: { courseId: string; lessonId: string }) {
  const { data: sessions, error, loading, reload } = useData(() => api.getLiveSessions(courseId, lessonId));
  const [form, setForm] = useState({
    title: "",
    description: "",
    scheduled_start: "",
    scheduled_end: "",
    meeting_url: "",
    status: "UPCOMING" as LiveSession["status"],
    recording_url: "",
  });
  const [message, setMessage] = useState("");
  const [editId, setEditId] = useState<string | null>(null);

  const reset = () => {
    setForm({ title: "", description: "", scheduled_start: "", scheduled_end: "", meeting_url: "", status: "UPCOMING", recording_url: "" });
    setEditId(null);
    setMessage("");
  };

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    try {
      const data: Record<string, unknown> = {
        title: form.title,
        description: form.description || null,
        scheduled_start: new Date(form.scheduled_start).toISOString(),
        scheduled_end: new Date(form.scheduled_end).toISOString(),
        meeting_url: form.meeting_url,
        status: form.status,
        recording_url: form.recording_url || null,
      };
      if (editId) {
        await api.updateLiveSession(courseId, editId, data);
        setMessage("Session updated.");
      } else {
        await api.createLiveSession(courseId, lessonId, data);
        setMessage("Session created.");
      }
      reset();
      reload();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to save session.");
    }
  };

  const startEdit = (s: LiveSession) => {
    setEditId(s.id);
    setForm({
      title: s.title,
      description: s.description ?? "",
      scheduled_start: new Date(s.scheduled_start).toISOString().slice(0, 16),
      scheduled_end: new Date(s.scheduled_end).toISOString().slice(0, 16),
      meeting_url: s.meeting_url,
      status: s.status,
      recording_url: s.recording_url ?? "",
    });
  };

  const remove = async (id: string) => {
    if (!confirm("Delete this live session?")) return;
    try {
      await api.deleteLiveSession(courseId, id);
      setMessage("Session deleted.");
      if (editId === id) reset();
      reload();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to delete session.");
    }
  };

  const statusBadge = (s: string) => {
    if (s === "LIVE") return <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">LIVE</span>;
    if (s === "UPCOMING") return <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">UPCOMING</span>;
    if (s === "COMPLETED") return <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">COMPLETED</span>;
    return <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">{s}</span>;
  };

  return (
    <div className="mt-4 border-t pt-3">
      <h3 className="text-sm font-semibold text-slate-700">🔴 Live Sessions</h3>
      {loading && <p className="mt-2 text-sm text-slate-500">Loading sessions…</p>}
      {error && <p role="alert" className="mt-2 text-sm text-red-700">{error}</p>}
      {sessions && !loading && (
        <div className="mt-2 space-y-2">
          {sessions.map((s) => (
            <div key={s.id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border bg-slate-50 p-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{s.title}</span>
                  {statusBadge(s.status)}
                </div>
                <p className="text-xs text-slate-500">
                  {new Date(s.scheduled_start).toLocaleString()} — {new Date(s.scheduled_end).toLocaleString()}
                </p>
                {s.recording_url && <p className="text-xs text-slate-400">Recording: {s.recording_url}</p>}
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={() => startEdit(s)} className="rounded border px-2 py-1 text-xs">Edit</button>
                <button type="button" onClick={() => remove(s.id)} className="rounded border border-red-200 px-2 py-1 text-xs text-red-700">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
      <form onSubmit={save} className="mt-3 flex flex-wrap items-center gap-2">
        <input className="w-48 rounded border px-2 py-1.5 text-sm" placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
        <input className="w-56 rounded border px-2 py-1.5 text-sm" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <input className="w-44 rounded border px-2 py-1.5 text-sm" type="datetime-local" required value={form.scheduled_start} onChange={(e) => setForm({ ...form, scheduled_start: e.target.value })} />
        <input className="w-44 rounded border px-2 py-1.5 text-sm" type="datetime-local" required value={form.scheduled_end} onChange={(e) => setForm({ ...form, scheduled_end: e.target.value })} />
        <input className="w-56 rounded border px-2 py-1.5 text-sm" placeholder="Meeting URL" value={form.meeting_url} onChange={(e) => setForm({ ...form, meeting_url: e.target.value })} required />
        <select className="rounded border px-2 py-1.5 text-sm" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as LiveSession["status"] })}>
          <option value="UPCOMING">UPCOMING</option>
          <option value="LIVE">LIVE</option>
          <option value="COMPLETED">COMPLETED</option>
          <option value="CANCELLED">CANCELLED</option>
        </select>
        <input className="w-56 rounded border px-2 py-1.5 text-sm" placeholder="Recording URL" value={form.recording_url} onChange={(e) => setForm({ ...form, recording_url: e.target.value })} />
        <button className="rounded-lg border px-3 py-1.5 text-sm">{editId ? "Update" : "Add"} session</button>
        {message && <span className="text-sm text-slate-500">{message}</span>}
      </form>
    </div>
  );
}

export function QuizzesView({ courseId }: { courseId: string }) {
  const { data, error, loading, reload } = useData(() => api.getQuizzes(courseId));
  const [title, setTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");
  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    if (busy) return;
    setBusy(true); setActionError("");
    try { await api.createQuiz(courseId, { title: title.trim(), description: null }); setTitle(""); reload(); }
    catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to create quiz."); }
    finally { setBusy(false); }
  };
  return (
    <div className={page}>
      <h1 className="text-3xl font-bold">Quizzes</h1>
      <form onSubmit={add} className="mt-6 flex gap-2">
        <input aria-label="Quiz title" required className="min-w-0 w-full rounded-lg border px-3 py-2" placeholder="Quiz title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <button disabled={busy || !title.trim()} className={button}>{busy ? "Saving…" : "Create quiz"}</button>
      </form>
      <div className="mt-6">
        {actionError && <p role="alert" className="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">{actionError}</p>}
        <State loading={loading} error={error} empty={data?.length === 0} />
        <QuizReviewQueue courseId={courseId} />
        {data?.map((quiz: Quiz) => (
          <QuizCard key={quiz.id} courseId={courseId} quiz={quiz} onDelete={reload} />
        ))}
      </div>
    </div>
  );
}

function QuizCard({ courseId, quiz, onDelete }: { courseId: string; quiz: Quiz; onDelete: () => void }) {
  const [questions, setQuestions] = useState(false);
  const [text, setText] = useState("");
  const [questionType, setQuestionType] = useState<"multiple_choice" | "yes_no" | "written">("yes_no");
  const [correctYes, setCorrectYes] = useState(true);
  const [points, setPoints] = useState(1);
  const { data, error, loading, reload } = useData(() => api.getQuestions(courseId, quiz.id));
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");
  const add = async () => {
    if (!text.trim() || !Number.isInteger(points) || points < 1) return;
    if (busy) return;
    setBusy(true); setActionError("");
    try { await api.createQuestion(courseId, quiz.id, { text: text.trim(), question_type: questionType, correct_yes: correctYes, points, order_index: Math.max(-1, ...(data ?? []).map((item) => item.order_index)) + 1 }); setText(""); reload(); }
    catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to add question."); }
    finally { setBusy(false); }
  };
  return (
    <article className="mt-3 rounded-xl border bg-white p-4">
      <div className="flex justify-between">
        <div>
          <h2 className="font-semibold">{quiz.title}</h2>
          <p className="text-sm text-slate-500">{quiz.description ?? "No description"}</p>
        </div>
        <div className="flex gap-3">
          <button className="text-sm text-red-700" onClick={() => setQuestions((v) => !v)}>
            {questions ? "Close" : "Questions"}
          </button>
          <button disabled={busy} className="text-sm text-red-700 disabled:opacity-50" onClick={async () => {
            if (busy || !confirm("Delete this quiz, its questions and all student submissions? This cannot be undone.")) return;
            setBusy(true); setActionError("");
            try { await api.deleteQuiz(courseId, quiz.id); onDelete(); }
            catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to delete quiz."); }
            finally { setBusy(false); }
          }}>
            Delete
          </button>
        </div>
      </div>
      {actionError && <p role="alert" className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">{actionError}</p>}
      {questions && (
        <div className="mt-4 border-t pt-3">
          <div className="mb-3 flex flex-wrap items-end gap-3">
            <label>Question type<select className="ml-2 rounded border p-2" value={questionType} onChange={(event) => setQuestionType(event.target.value as typeof questionType)}><option value="yes_no">Yes / No - automatic grading</option><option value="written">Written answer - teacher review</option><option value="multiple_choice">Multiple choice - automatic grading</option></select></label>
            {questionType === "yes_no" && <label>Correct answer<select className="ml-2 rounded border p-2" value={String(correctYes)} onChange={(event) => setCorrectYes(event.target.value === "true")}><option value="true">Yes</option><option value="false">No</option></select></label>}
          <label>Points<input type="number" min={1} step={1} className="ml-2 w-24 rounded border p-2" value={points} onChange={(event) => setPoints(Number(event.target.value))} /></label>
          </div>
          <div className="flex gap-2">
            <input aria-label="Question text" className="min-w-0 w-full rounded border px-2 py-1" placeholder="Question text" value={text} onChange={(e) => setText(e.target.value)} />
            <button disabled={busy || loading || !!error || !text.trim() || !Number.isInteger(points) || points < 1} className="rounded border px-2 text-sm disabled:opacity-50" onClick={add}>Add</button>
          </div>
          <State loading={loading} error={error} empty={data?.length === 0} />
          {data?.map((question) => (
            <div key={question.id} className="mt-4 rounded-lg border p-3 text-sm">
              <p className="font-medium">{question.text} <span className="text-slate-500">({question.points} pts)</span></p>
              {question.question_type === "written" ? <p className="mt-2 text-slate-600">Written answer. Students type their response; review it below after submission.</p> : question.question_type === "yes_no" ? <YesNoKey courseId={courseId} quizId={quiz.id} questionId={question.id} /> : <QuestionAnswers courseId={courseId} quizId={quiz.id} questionId={question.id} />}
            </div>
          ))}
        </div>
      )}
    </article>
  );
}

function QuestionAnswers({ courseId, quizId, questionId }: { courseId: string; quizId: string; questionId: string }) {
  const { data, loading, error, reload } = useData(() => api.getAnswers(courseId, quizId, questionId));
  const [text, setText] = useState("");
  const [correct, setCorrect] = useState(false);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");
  const add = async (event: React.FormEvent) => {
    event.preventDefault();
    if (busy || !text.trim()) return;
    setBusy(true); setActionError("");
    try { await api.createAnswer(courseId, quizId, questionId, { text: text.trim(), is_correct: correct }); setText(""); setCorrect(false); reload(); }
    catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to add answer."); }
    finally { setBusy(false); }
  };
  return <div className="mt-3 space-y-3">
    <State loading={loading} error={error} />
    {data?.map((answer) => <div key={answer.id} className="flex items-center justify-between gap-3 rounded bg-slate-50 p-2"><span>{answer.text}{answer.is_correct && <span className="ml-2 font-semibold text-emerald-700">Correct</span>}</span><button disabled={busy} className="text-red-700 disabled:opacity-50" onClick={async () => {
      if (busy || !confirm("Delete this answer option?")) return;
      setBusy(true); setActionError("");
      try { await api.deleteAnswer(courseId, quizId, questionId, answer.id); reload(); }
      catch (reason) { setActionError(reason instanceof Error ? reason.message : "Unable to delete answer."); }
      finally { setBusy(false); }
    }}>Delete</button></div>)}
    {!loading && !error && ((data?.length ?? 0) < 2 || !data?.some((answer) => answer.is_correct)) && <p className="text-amber-700">Add at least two options and mark the correct answer before learners take this quiz.</p>}
    <form onSubmit={add} className="flex flex-wrap items-center gap-2">
      <label className="min-w-0 flex-1">Answer option<input required className="mt-1 w-full rounded border px-2 py-1" value={text} onChange={(event) => setText(event.target.value)} /></label>
      <label className="flex items-center gap-2"><input type="checkbox" checked={correct} onChange={(event) => setCorrect(event.target.checked)} />Correct answer</label>
      <button disabled={busy || loading || !!error || !text.trim()} className="rounded border px-3 py-2 disabled:opacity-50">Add option</button>
    </form>
    {actionError && <p role="alert" className="rounded bg-red-50 p-2 text-red-700">{actionError}</p>}
  </div>;
}

export function StudentsView({ courseId }: { courseId: string }) {
  const { data, error, loading } = useData(() => api.getEnrolledStudents(courseId));
  return (
    <div className={page}>
      <h1 className="text-3xl font-bold">Students</h1>
      <div className="mt-6 overflow-x-auto rounded-xl border bg-white">
        <State loading={loading} error={error} empty={data?.length === 0} />
        {data && (
          <table className="min-w-full text-left text-sm">
            <thead className="border-b bg-slate-50 text-slate-500">
              <tr>
                <th className="p-4">Student</th>
                <th className="p-4">Email</th>
                <th className="p-4">Status</th>
                <th className="p-4">Enrolled</th>
              </tr>
            </thead>
            <tbody>
              {data.map((student: EnrolledStudent) => (
                <tr className="border-b" key={student.id}>
                  <td className="p-4 font-medium">{student.first_name} {student.last_name}</td>
                  <td className="p-4">{student.email}</td>
                  <td className="p-4">{student.status}</td>
                  <td className="p-4">{new Date(student.enrolled_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export function AnalyticsView({ courseId }: { courseId: string }) {
  const { data, error, loading } = useData(() => api.getCourseAnalytics(courseId));
  const labels: [keyof CourseAnalytics, string, string][] = [
    ["total_students", "Total students", ""],
    ["completed_students", "Completed students", ""],
    ["completion_rate", "Completion rate", "%"],
    ["average_quiz_score", "Average quiz score", "%"],
    ["total_lessons", "Total lessons", ""],
    ["completed_lessons", "Completed lessons", ""],
    ["average_progress", "Average progress", "%"],
  ];
  return (
    <div className={page}>
      <h1 className="text-3xl font-bold">Course analytics</h1>
      <State loading={loading} error={error} />
      {data && (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {labels.map(([key, label, suffix]) => (
            <Info key={key} label={label} value={`${data[key]}${suffix}`} />
          ))}
        </div>
      )}
    </div>
  );
}

export function CertificatesView({ courseId }: { courseId: string }) {
  const { data, error, loading } = useData(() => api.getCourseCertificates(courseId));
  return (
    <div className={page}>
      <h1 className="text-3xl font-bold">Certificates</h1>
      <div className="mt-6 rounded-xl border bg-white">
        <State loading={loading} error={error} empty={data?.length === 0} />
        {data?.map((cert) => (
          <div key={cert.id} className="flex flex-wrap justify-between gap-3 border-b p-4">
            <div>
              <p className="font-medium">{cert.course_title}</p>
              <p className="text-sm text-slate-500">Issued {new Date(cert.issued_at).toLocaleDateString()}</p>
            </div>
            {cert.certificate_url ? (
              <a className="text-sm text-red-700 underline" href={cert.certificate_url}>
                Open certificate
              </a>
            ) : (
              <span className="text-sm text-slate-500">Not available</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  );
}


function YesNoKey({ courseId, quizId, questionId }: { courseId: string; quizId: string; questionId: string }) {
  const { data, loading, error } = useData(() => api.getAnswers(courseId, quizId, questionId));
  return <div className="mt-2"><State loading={loading} error={error} /><p>Yes / No ? correct answer: {data?.find((answer) => answer.is_correct)?.text ?? "Loading..."}</p></div>;
}

function QuizReviewQueue({ courseId }: { courseId: string }) {
  const { data, loading, error, reload } = useData(() => api.getQuizSubmissions(courseId));
  return <section className="space-y-4 rounded-xl border bg-white p-5">
    <div className="flex items-center justify-between gap-3"><h2 className="text-xl font-semibold">Student submissions</h2><button className="rounded border px-3 py-2" onClick={reload}>Refresh submissions</button></div>
    <p className="text-sm text-slate-600">Grade every written answer before publishing the final score. Automatic answers are already corrected.</p>
    <State loading={loading} error={error} />
    {!loading && !error && !data?.length && <p>No submissions yet.</p>}
    {data?.map((submission) => <SubmissionReview key={submission.attempt_id} courseId={courseId} submission={submission} onSaved={reload} />)}
  </section>;
}

function SubmissionReview({ courseId, submission, onSaved }: { courseId: string; submission: import("@/types/learning").QuizSubmissionReview; onSaved: () => void }) {
  const [marks, setMarks] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const written = submission.responses.filter((row) => row.question_type === "written");
  const ready = written.every((row) => marks[row.question_id]?.trim() && Number.isFinite(Number(marks[row.question_id])) && Number(marks[row.question_id]) >= 0 && Number(marks[row.question_id]) <= row.points);
  return <details className="rounded-lg border p-4">
    <summary className="cursor-pointer font-semibold">{submission.student_name} / {submission.quiz_title} / {submission.status === "pending_review" ? "Awaiting review" : `Graded: ${submission.percentage?.toFixed(1)}%`}</summary>
    <form className="mt-4 space-y-4" onSubmit={async (event) => {
      event.preventDefault(); if (busy || !ready) return; setBusy(true); setError("");
      try { await api.reviewQuizSubmission(courseId, submission.attempt_id, written.map((row) => ({ question_id: row.question_id, points_awarded: Number(marks[row.question_id]), feedback: feedback[row.question_id] ?? "" }))); onSaved(); }
      catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to publish grades. Your entries are preserved."); }
      finally { setBusy(false); }
    }}>
      {submission.responses.map((row) => <div key={row.question_id} className="space-y-2 rounded bg-slate-50 p-3">
        <p className="font-medium">{row.question_text}</p><p className="whitespace-pre-wrap">Student answer: {row.text_answer ?? row.selected_answer}</p>
        {row.question_type === "written" && submission.status === "pending_review" ? <>
          <label className="block">Points (0 to {row.points})<input required disabled={busy} type="number" min={0} max={row.points} step="0.25" className="ml-2 w-24 rounded border p-2" value={marks[row.question_id] ?? ""} onChange={(event) => setMarks((values) => ({ ...values, [row.question_id]: event.target.value }))} /></label>
          <label className="block">Feedback (optional)<textarea disabled={busy} maxLength={5000} rows={3} className="mt-1 w-full rounded border p-2" value={feedback[row.question_id] ?? ""} onChange={(event) => setFeedback((values) => ({ ...values, [row.question_id]: event.target.value }))} /></label>
        </> : <><p>{row.points_awarded} / {row.points} points{row.correct_answer && ` - Correct answer: ${row.correct_answer}`}</p>{row.feedback && <p className="whitespace-pre-wrap">Feedback: {row.feedback}</p>}</>}
      </div>)}
      {error && <p role="alert" className="text-red-700">{error}</p>}
      {submission.status === "pending_review" && <button disabled={busy || !ready} className={button}>{busy ? "Publishing..." : "Publish final grade"}</button>}
    </form>
  </details>;
}
