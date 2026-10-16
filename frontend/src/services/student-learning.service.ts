import type { Certificate, CourseDetails, CourseProgress, LessonDetails, MyCourse, Notification, QuizDetails, QuizResult, StudentDashboard, RecordedVideo, LiveSession } from "@/types/learning";
import { apiRequest } from "@/services/api-client";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  return apiRequest<T>(path, init);
}

export const studentLearning = {
  dashboard: () => request<StudentDashboard>("/student/dashboard"),
  course: (id: string) => request<CourseDetails>(`/student/courses/${id}`),
  enroll: (id: string) => request<unknown>(`/student/courses/${id}/enroll`, { method: "POST" }),
  myCourses: () => request<MyCourse[]>("/student/my-courses"),
  lesson: (id: string) => request<LessonDetails>(`/student/lessons/${id}`),
  lessonVideo: (id: string) => request<RecordedVideo>(`/student/lessons/${id}/video`),
  lessonLiveSessions: (id: string) => request<LiveSession[]>(`/student/lessons/${id}/live-sessions`),
  completeLesson: (id: string) => request<{ is_completed: boolean; course_completed_lessons: number; course_completion_percentage: number; certificate_issued: boolean }>(`/student/lessons/${id}/complete`, { method: "POST" }),
  quiz: (id: string) => request<QuizDetails>(`/student/quizzes/${id}`),
  submitQuiz: (id: string, answers: { question_id: string; answer_id?: string; text_answer?: string }[]) => request<QuizResult>(`/student/quizzes/${id}/submit`, { method: "POST", body: JSON.stringify({ answers }) }),
  progress: () => request<CourseProgress[]>("/student/progress"),
  certificates: () => request<Certificate[]>("/student/certificates"),
  notifications: () => request<Notification[]>("/notifications"),
  markNotificationRead: (id: string) => request<Notification>(`/notifications/${id}/read`, { method: "PATCH" }),
  deleteNotification: (id: string) => request<void>(`/notifications/${id}`, { method: "DELETE" }),
};
