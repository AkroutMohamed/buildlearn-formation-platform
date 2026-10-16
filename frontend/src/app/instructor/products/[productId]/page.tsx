import InstructorProductPageClient from "./InstructorProductPageClient";

export default async function InstructorProductPage({
  params,
}: {
  params: Promise<{ productId: string }>;
}) {
  const { productId } = await params;

  return <InstructorProductPageClient productId={productId} />;
}
