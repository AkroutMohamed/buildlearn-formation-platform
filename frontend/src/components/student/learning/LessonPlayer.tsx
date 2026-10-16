"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { studentLearning } from "@/services/student-learning.service";
import { apiUrl } from "@/services/api-client";
import type { CourseDetails, LessonDetails } from "@/types/learning";
export default function LessonPlayer({ lessonId }: { lessonId: string }) {
  const [lesson, setLesson] = useState<LessonDetails | null>(null);
  const [course, setCourse] = useState<CourseDetails | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");

  useEffect(() => {
    studentLearning.lesson(lessonId).then(async (item) => {
      setLesson(item);
      setCourse(await studentLearning.course(item.course_id));
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to load this lesson."));
  }, [lessonId]);

  if (error) {
    return (
      <div className="rounded-xl border bg-white p-8 text-center">
        <p>{error}</p>
        <Link href="/student/my-courses" className="mt-4 inline-block text-red-700 underline">
          Back to my courses
        </Link>
      </div>
    );
  }

  if (!lesson || !course) {
    return (
      <div className="grid animate-pulse gap-6 lg:grid-cols-[280px_1fr]">
        <div className="h-96 rounded-xl bg-slate-200" />
        <div className="h-96 rounded-xl bg-slate-200" />
      </div>
    );
  }

  const videos = [
    ...(lesson.video ? [lesson.video] : []),
    ...lesson.resources.filter((resource) => resource.resource_type?.startsWith("video/")).map((resource) => ({ id: resource.id, title: resource.title, description: resource.description, video_url: resource.url, thumbnail_url: null })),
  ];
  const resources = lesson.resources.filter((resource) => !resource.resource_type?.startsWith("video/"));
  const lessons = course.modules.flatMap((module) => module.lessons);
  const index = lessons.findIndex((item) => item.id === lessonId);
  const previous = lessons[index - 1];
  const next = lessons[index + 1];

  async function complete() {
    setBusy(true);
    setActionError("");
    try {
      const result = await studentLearning.completeLesson(lessonId);
      setLesson((current) => (current ? { ...current, is_completed: result.is_completed } : current));
      setCourse((current) =>
        current
          ? {
              ...current,
              completion_percentage: result.course_completion_percentage,
              completed_lessons: result.course_completed_lessons,
              modules: current.modules.map((module) => ({
                ...module,
                lessons: module.lessons.map((item) => (item.id === lessonId ? { ...item, is_completed: true } : item)),
              })),
            }
          : current,
      );
    } catch (reason) {
      setActionError(reason instanceof Error ? reason.message : "Unable to complete lesson. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  const statusLabel = (s: string) => {
    if (s === "LIVE") return "🔴 Live";
    if (s === "UPCOMING") return "🕒 Upcoming";
    if (s === "COMPLETED") return "✅ Completed";
    if (s === "CANCELLED") return "❌ Cancelled";
    return s;
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
      <aside className="rounded-xl border bg-white p-4 lg:sticky lg:top-24 lg:h-fit">
        <Link href={`/student/courses/${course.id}`} className="text-sm font-semibold text-red-700">
          {course.title}
        </Link>
        <p className="mt-3 text-sm text-slate-600">Progress: {course.completion_percentage}%</p>
        <div className="mt-2 h-2 rounded-full bg-slate-100">
          <div className="h-full rounded-full bg-red-600" style={{ width: `${course.completion_percentage}%` }} />
        </div>
        <div className="mt-5 space-y-3">
          {course.modules.map((module) => (
            <div key={module.id}>
              <p className="text-xs font-bold uppercase text-slate-500">{module.title}</p>
              {module.lessons.map((item) => (
                <Link
                  key={item.id}
                  href={`/student/lessons/${item.id}`}
                  className={`mt-1 block rounded px-2 py-1.5 text-sm ${
                    item.id === lessonId ? "bg-red-50 text-red-700" : "text-slate-600"
                  }`}
                >
                  {item.is_completed ? "✓" : "○"} {item.title}
                </Link>
              ))}
            </div>
          ))}
        </div>
      </aside>

      <main className="rounded-xl border bg-white p-6 lg:p-8">
        <p className="text-sm font-medium text-red-700">
          Lesson {index + 1} of {lessons.length} · {lesson.duration_minutes} min
        </p>
        <h1 className="mt-2 text-3xl font-bold">{lesson.title}</h1>
        <div className="mt-6 whitespace-pre-wrap text-slate-700">{lesson.content}</div>

        {videos.length > 0 && (
          <section className="mt-8 border-t pt-6">
            <h2 className="font-semibold">🎥 Recorded Video</h2>
            {videos.map((video) => <div key={video.id} className="mt-4">
            <div className="mt-3 aspect-video rounded-xl border bg-slate-900">
              <video controls className="h-full w-full rounded-xl" src={video.video_url.startsWith("/uploads/") ? apiUrl(video.video_url) : video.video_url} poster={video.thumbnail_url || undefined}>
                <track kind="captions" />
              </video>
            </div>
            <p className="mt-2 text-sm text-slate-600">{video.title}</p>
            {video.description && <p className="text-sm text-slate-500">{video.description}</p>}
            </div>)}
          </section>
        )}

        {lesson.live_sessions.length > 0 && (
          <section className="mt-8 border-t pt-6">
            <h2 className="font-semibold">🔴 Live Sessions</h2>
            <div className="mt-3 space-y-3">
              {lesson.live_sessions.map((session) => (
                <div key={session.id} className="rounded-xl border p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className="font-medium">{session.title}</h3>
                    <span className="rounded-full border px-2.5 py-0.5 text-xs font-medium">
                      {statusLabel(session.status)}
                    </span>
                  </div>
                  {session.description && <p className="mt-1 text-sm text-slate-500">{session.description}</p>}
                  <p className="mt-2 text-xs text-slate-400">
                    {new Date(session.scheduled_start).toLocaleString()} — {new Date(session.scheduled_end).toLocaleString()}
                  </p>
                  {session.meeting_url && (session.status === "LIVE" || session.status === "UPCOMING") && (
                    <a
                      href={session.meeting_url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-3 inline-block rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white"
                    >
                      Join Session
                    </a>
                  )}
                  {session.recording_url && (
                    <a
                      href={session.recording_url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 ml-2 inline-block rounded-lg border px-4 py-2 text-sm font-semibold text-red-700"
                    >
                      Watch Recording
                    </a>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {resources.length > 0 && (
          <section className="mt-8 border-t pt-6">
            <h2 className="font-semibold">Resources</h2>
            {resources.map((resource) => (
              <a
                key={resource.id}
                href={resource.url.startsWith("/uploads/") ? apiUrl(resource.url) : resource.url}
                target="_blank"
                rel="noreferrer"
                className="mt-2 block rounded-lg border p-3 text-sm text-red-700"
              >
                {resource.title}
              </a>
            ))}
          </section>
        )}

        {actionError && <p role="alert" className="mt-6 rounded-lg bg-red-50 p-3 text-sm text-red-700">{actionError}</p>}
        <div className="mt-8 flex flex-wrap justify-between gap-3 border-t pt-6">
          <Link
            aria-disabled={!previous}
            tabIndex={previous ? undefined : -1}
            href={previous ? `/student/lessons/${previous.id}` : "#"}
            className={`rounded-lg border px-4 py-2 ${!previous ? "pointer-events-none opacity-40" : ""}`}
          >
            ← Previous
          </Link>
          {!lesson.is_completed ? (
            <button
              disabled={busy}
              onClick={() => void complete()}
              className="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white disabled:opacity-60"
            >
              {busy ? "Saving progress…" : "Mark complete"}
            </button>
          ) : (
            <span className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-semibold text-emerald-700">
              Completed
            </span>
          )}
          <Link
            aria-disabled={!next}
            tabIndex={next ? undefined : -1}
            href={next ? `/student/lessons/${next.id}` : "#"}
            className={`rounded-lg border px-4 py-2 ${!next ? "pointer-events-none opacity-40" : ""}`}
          >
            Next →
          </Link>
        </div>
      </main>
    </div>
  );
}
