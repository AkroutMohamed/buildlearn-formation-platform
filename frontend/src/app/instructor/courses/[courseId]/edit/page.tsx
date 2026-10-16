"use client";
import { useEffect, useState } from "react";
import CourseForm from "@/components/instructor/CourseForm";
import { getCourse } from "@/services/instructor";
import type { Course } from "@/types/instructor";
export default function EditCoursePage({ params }: { params: Promise<{ courseId: string }> }) { const [course, setCourse] = useState<Course | null>(null); const [error, setError] = useState(""); useEffect(() => { params.then(({ courseId }) => getCourse(courseId).then(setCourse).catch(e => setError(e instanceof Error ? e.message : "Unable to load course."))); }, [params]); return <div className="mx-auto max-w-4xl p-5 md:p-8"><h1 className="text-3xl font-bold">Edit course</h1><div className="mt-6">{error ? <p className="rounded bg-red-50 p-4 text-red-700">{error}</p> : course ? <CourseForm course={course} /> : <p>Loading course…</p>}</div></div>; }
