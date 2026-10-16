"use client";
import { useEffect, useRef, useState } from "react";
import * as api from "@/services/instructor";
import type { Resource } from "@/types/instructor";

type Item = { id: string; file: File; title: string; status: "ready" | "uploading" | "uploaded" | "failed"; error: string };
const size = (bytes: number) => `${(bytes / 1024 / 1024).toFixed(1)} MB`;

export default function LocalVideoUploads({ courseId, lessonId }: { courseId: string; lessonId: string }) {
  const picker = useRef<HTMLInputElement>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [videos, setVideos] = useState<Resource[]>([]);
  const [busy, setBusy] = useState(false);
  const running = useRef(false);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    api.getResources(courseId, lessonId).then((data) => { if (active) { setVideos(data.filter((item) => item.resource_type?.startsWith("video/"))); setError(""); } }).catch((reason) => { if (active) setError(reason instanceof Error ? reason.message : "Unable to load uploaded videos."); });
    return () => { active = false; };
  }, [courseId, lessonId, attempt]);
  const choose = (files: FileList | null) => {
    if (!files || busy) return;
    const selected = Array.from(files).map((file): Item => {
      const error = !/\.(mp4|webm|ogv)$/i.test(file.name) ? "Use MP4, WebM, or OGV." : !file.size ? "This file is empty." : file.size > 250 * 1024 * 1024 ? "This file exceeds 250 MB." : "";
      return { id: `${file.name}:${file.size}:${file.lastModified}`, file, title: file.name.replace(/\.[^.]+$/, "").slice(0, 200), status: error ? "failed" : "ready", error };
    });
    setItems((current) => [...current, ...selected.filter((item, index) => !current.some((old) => old.id === item.id) && selected.findIndex((other) => other.id === item.id) === index)]);
    if (picker.current) picker.current.value = "";
  };
  const upload = async () => {
    if (running.current) return;
    const pending = items.filter((item) => item.status !== "uploaded" && item.status !== "uploading" && item.title.trim() && /\.(mp4|webm|ogv)$/i.test(item.file.name) && item.file.size > 0 && item.file.size <= 250 * 1024 * 1024);
    running.current = true; setBusy(true);
    for (const item of pending) {
      setItems((current) => current.map((value) => value.id === item.id ? { ...value, status: "uploading", error: "" } : value));
      try {
        const form = new FormData(); form.append("file", item.file); form.append("title", item.title.trim());
        const video = await api.appendVideo(courseId, lessonId, form);
        setVideos((current) => [...current, video]);
        setItems((current) => current.map((value) => value.id === item.id ? { ...value, status: "uploaded" } : value));
      } catch (reason) {
        setItems((current) => current.map((value) => value.id === item.id ? { ...value, status: "failed", error: reason instanceof Error ? reason.message : "Upload failed. Try again." } : value));
      }
    }
    running.current = false; setBusy(false);
  };
  const pending = items.filter((item) => item.status !== "uploaded" && item.title.trim() && /\.(mp4|webm|ogv)$/i.test(item.file.name) && item.file.size > 0 && item.file.size <= 250 * 1024 * 1024).length;
  return <div className="mt-3 space-y-4">
    <div onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); choose(event.dataTransfer.files); }} className="rounded-xl border-2 border-dashed border-red-200 bg-red-50/40 p-6 text-center">
      <p className="font-semibold text-slate-800">Add videos to this lesson</p>
      <p className="mt-1 text-sm text-slate-600">Drag videos here, or choose several files from your computer.</p>
      <input ref={picker} type="file" multiple accept=".mp4,.webm,.ogv,video/mp4,video/webm,video/ogg" className="hidden" onChange={(event) => choose(event.target.files)} aria-label="Choose video files" />
      <button type="button" disabled={busy} onClick={() => picker.current?.click()} className="mt-4 rounded-lg bg-red-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-red-700 disabled:opacity-50">Choose videos</button>
      <p className="mt-3 text-xs text-slate-500">MP4, WebM, OGV · 250 MB per file. Existing videos are kept.</p>
    </div>
    {items.length > 0 && <div className="space-y-3">
      <p role="status" className="text-sm text-slate-600">{items.filter((item) => item.status === "uploaded").length} of {items.length} selected videos uploaded</p>
      {items.map((item) => <div key={item.id} className="rounded-lg border bg-white p-3">
        <div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="break-all text-sm font-medium">{item.file.name}</p><p className="text-xs text-slate-500">{size(item.file.size)} · {item.status === "ready" ? "Ready to upload" : item.status === "uploading" ? "Uploading…" : item.status === "uploaded" ? "Uploaded" : "Needs attention"}</p></div><button type="button" disabled={busy} aria-label={`Remove ${item.file.name} from selection`} onClick={() => setItems((current) => current.filter((value) => value.id !== item.id))} className="shrink-0 rounded border px-2 py-1 text-xs disabled:opacity-50">{item.status === "uploaded" ? "Dismiss" : "Remove"}</button></div>
        {item.status !== "uploaded" && <label className="mt-2 block text-xs font-medium">Video title<input maxLength={200} disabled={busy} value={item.title} onChange={(event) => setItems((current) => current.map((value) => value.id === item.id ? { ...value, title: event.target.value } : value))} className="mt-1 w-full rounded border px-3 py-2 text-sm" /></label>}
        {item.error && <p role="alert" className="mt-2 text-sm text-red-700">{item.error}</p>}
      </div>)}
      <button type="button" disabled={busy || !pending} onClick={() => void upload()} className="rounded-lg bg-red-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{busy ? "Uploading videos…" : `Upload ${pending} video${pending === 1 ? "" : "s"}`}</button>
    </div>}
    {error && <p role="alert" className="text-sm text-red-700">{error} <button onClick={() => setAttempt((value) => value + 1)} className="underline">Retry</button></p>}
    {videos.length > 0 && <div className="space-y-2"><h4 className="text-sm font-semibold">Uploaded videos ({videos.length})</h4>{videos.map((video) => <div key={video.id} className="flex items-center justify-between gap-3 rounded-lg border bg-slate-50 p-3"><p className="text-sm font-medium">{video.title}</p><button type="button" disabled={busy} className="text-sm text-red-700 disabled:opacity-50" onClick={async () => {
      if (running.current || !confirm(`Delete "${video.title}"? This cannot be undone.`)) return;
      running.current = true; setBusy(true);
      try { await api.deleteResource(courseId, lessonId, video.id); setVideos((current) => current.filter((item) => item.id !== video.id)); }
      catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to delete video."); }
      finally { running.current = false; setBusy(false); }
    }}>Delete</button></div>)}</div>}
  </div>;
}
