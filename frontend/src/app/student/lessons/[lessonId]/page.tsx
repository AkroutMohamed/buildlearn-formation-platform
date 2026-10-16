"use client";
import { useParams } from "next/navigation";
import LessonPlayer from "@/components/student/learning/LessonPlayer";
export default function LessonRoute() { const { lessonId } = useParams<{ lessonId: string }>(); return <LessonPlayer lessonId={lessonId} />; }
