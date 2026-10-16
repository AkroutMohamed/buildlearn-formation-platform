"use client";
import { useParams } from "next/navigation";
import PublicCourseDetailsPage from "@/components/student/learning/PublicCourseDetailsPage";

export default function PublicCourseRoute() {
  const params = useParams<{ id: string }>();
  return <PublicCourseDetailsPage courseId={params.id} />;
}
