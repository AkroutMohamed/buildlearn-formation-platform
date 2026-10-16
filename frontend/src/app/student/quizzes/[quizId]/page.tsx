"use client";
import { useParams } from "next/navigation";
import QuizExperience from "@/components/student/learning/QuizExperience";
export default function QuizRoute() { const { quizId } = useParams<{ quizId: string }>(); return <QuizExperience quizId={quizId} />; }
