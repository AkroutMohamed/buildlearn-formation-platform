"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import { LessonsView } from "@/components/instructor/InstructorCourseViews";
import { getModules } from "@/services/instructor";

export default function Page({ params }: { params: Promise<{ courseId: string }> }) {
  const { courseId } = use(params);
  const [modules, setModules] = useState<{ id: string; title: string }[]>([]);

  useEffect(() => {
    getModules(courseId).then(setModules);
  }, [courseId]);

  const moduleId = modules[0]?.id;
  if (!moduleId) return <div className="p-8">Create a module before adding lessons.</div>;

  return (
    <>
      <div className="mx-auto max-w-6xl px-5 pt-5 md:px-8">
        <Link href={`/instructor/courses/${courseId}/modules`} className="inline-block rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]">
          Modules
        </Link>
      </div>
      <LessonsView courseId={courseId} moduleId={moduleId} />
    </>
  );
}
