import CourseNavigation from "@/components/instructor/CourseNavigation";

export default async function CourseLayout({ children, params }: { children: React.ReactNode; params: Promise<{ courseId: string }> }) {
  const { courseId } = await params;
  return <><CourseNavigation courseId={courseId} />{children}</>;
}
