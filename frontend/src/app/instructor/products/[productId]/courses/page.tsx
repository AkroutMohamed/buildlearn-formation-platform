import InstructorProductCoursesPageClient from "./InstructorProductCoursesPageClient";

export default async function InstructorProductCoursesPage({
  params,
}: {
  params: Promise<{ productId: string }>;
}) {
  const { productId } = await params;

  return <InstructorProductCoursesPageClient productId={productId} />;
}
