import { ModulesView } from "@/components/instructor/InstructorCourseViews";
export default async function Page({ params }: { params: Promise<{ courseId: string }> }) { const { courseId } = await params; return <ModulesView courseId={courseId} />; }
