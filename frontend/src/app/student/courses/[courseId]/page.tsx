"use client";
import { useParams } from "next/navigation";
import CourseDetailsPage from "@/components/student/learning/CourseDetailsPage";
export default function CourseDetailsRoute() { const { courseId } = useParams<{ courseId: string }>(); return <CourseDetailsPage courseId={courseId} />; }
