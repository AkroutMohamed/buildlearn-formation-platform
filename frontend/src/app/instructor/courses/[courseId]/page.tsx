import { CourseOverview } from "@/components/instructor/InstructorCourseViews";
export default async function CoursePage({ params }: { params: Promise<{ courseId: string }> }) { const { courseId } = await params; return <CourseOverview courseId={courseId} />; }
