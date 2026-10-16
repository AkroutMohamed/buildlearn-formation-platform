import type { Answer, Course, CourseAnalytics, CourseDetail, CourseInput, Certificate, Lesson, LessonInput, Module, ModuleInput, Question, QuestionInput, Quiz, QuizInput, Resource, StudentProgress, StudentQuizResult, EnrolledStudent, RecordedVideo, LiveSession } from "@/types/instructor";
import { apiRequest, ApiError } from "@/services/api-client";

async function instructorFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  return apiRequest<T>(path, init);
}

const json = <T>(method: string, body?: T): RequestInit => ({ method, body: body === undefined ? undefined : JSON.stringify(body) });
export const getInstructorCourses = () => instructorFetch<Course[]>("/instructor/courses");
export const getCourse = (id: string) => instructorFetch<CourseDetail>(`/instructor/courses/${id}`);
export const updateCourse = (id: string, data: Partial<CourseInput>) => instructorFetch<Course>(`/instructor/courses/${id}`, json("PUT", data));
export const deleteCourse = (id: string) => instructorFetch<{ message: string }>(`/instructor/courses/${id}`, json("DELETE"));
export const setCoursePublished = (id: string, published: boolean) => instructorFetch<Course>(`/instructor/courses/${id}/${published ? "publish" : "unpublish"}`, json("PATCH"));
export const getModules = (id: string) => instructorFetch<Module[]>(`/instructor/courses/${id}/modules`);
export const createModule = (id: string, data: ModuleInput) => instructorFetch<Module>(`/instructor/courses/${id}/modules`, json("POST", data));
export const updateModule = (courseId: string, id: string, data: Partial<ModuleInput>) => instructorFetch<Module>(`/instructor/courses/${courseId}/modules/${id}`, json("PUT", data));
export const deleteModule = (courseId: string, id: string) => instructorFetch<{ message: string }>(`/instructor/courses/${courseId}/modules/${id}`, json("DELETE"));
export const getLessons = (courseId: string, moduleId: string) => instructorFetch<Lesson[]>(`/instructor/courses/${courseId}/modules/${moduleId}/lessons`);
export const createLesson = (courseId: string, moduleId: string, data: LessonInput) => instructorFetch<Lesson>(`/instructor/courses/${courseId}/modules/${moduleId}/lessons`, json("POST", data));
export const updateLesson = (courseId: string, moduleId: string, id: string, data: Partial<LessonInput>) => instructorFetch<Lesson>(`/instructor/courses/${courseId}/modules/${moduleId}/lessons/${id}`, json("PUT", data));
export const deleteLesson = (courseId: string, moduleId: string, id: string) => instructorFetch<{ message: string }>(`/instructor/courses/${courseId}/modules/${moduleId}/lessons/${id}`, json("DELETE"));
export const getResources = (courseId: string, lessonId: string) => instructorFetch<Resource[]>(`/instructor/courses/${courseId}/lessons/${lessonId}/resources`);
export const uploadResource = (courseId: string, lessonId: string, form: FormData) => instructorFetch<Resource>(`/instructor/courses/${courseId}/lessons/${lessonId}/resources`, { method: "POST", body: form });
export const deleteResource = (courseId: string, lessonId: string, id: string) => instructorFetch<{ message: string }>(`/instructor/courses/${courseId}/lessons/${lessonId}/resources/${id}`, json("DELETE"));
export const getVideo = async (courseId: string, lessonId: string) => {
  try { return await instructorFetch<RecordedVideo>(`/instructor/courses/${courseId}/lessons/${lessonId}/video`); }
  catch (error) { if (error instanceof ApiError && error.status === 404 && error.message === "Recorded video not found") return null; throw error; }
};
export const uploadVideo = (courseId: string, lessonId: string, form: FormData) => instructorFetch<RecordedVideo>(`/instructor/courses/${courseId}/lessons/${lessonId}/video/upload`, { method: "POST", body: form });
export const appendVideo = (courseId: string, lessonId: string, form: FormData) => instructorFetch<Resource>(`/instructor/courses/${courseId}/lessons/${lessonId}/videos/upload`, { method: "POST", body: form });
export const createVideo = (courseId: string, lessonId: string, data: Partial<RecordedVideo>) => instructorFetch<RecordedVideo>(`/instructor/courses/${courseId}/lessons/${lessonId}/video`, json("POST", data));
export const updateVideo = (courseId: string, lessonId: string, data: Partial<RecordedVideo>) => instructorFetch<RecordedVideo>(`/instructor/courses/${courseId}/lessons/${lessonId}/video`, json("PUT", data));
export const deleteVideo = (courseId: string, lessonId: string) => instructorFetch<{ message: string }>(`/instructor/courses/${courseId}/lessons/${lessonId}/video`, json("DELETE"));
export const getLiveSessions = (courseId: string, lessonId: string) => instructorFetch<LiveSession[]>(`/instructor/courses/${courseId}/lessons/${lessonId}/live-sessions`);
export const createLiveSession = (courseId: string, lessonId: string, data: Partial<LiveSession>) => instructorFetch<LiveSession>(`/instructor/courses/${courseId}/lessons/${lessonId}/live-sessions`, json("POST", data));
export const updateLiveSession = (courseId: string, sessionId: string, data: Partial<LiveSession>) => instructorFetch<LiveSession>(`/instructor/courses/${courseId}/live-sessions/${sessionId}`, json("PUT", data));
export const deleteLiveSession = (courseId: string, sessionId: string) => instructorFetch<{ message: string }>(`/instructor/courses/${courseId}/live-sessions/${sessionId}`, json("DELETE"));
export const getQuizzes = (id: string) => instructorFetch<Quiz[]>(`/instructor/courses/${id}/quizzes`);
export const createQuiz = (id: string, data: QuizInput) => instructorFetch<Quiz>(`/instructor/courses/${id}/quizzes`, json("POST", data));
export const updateQuiz = (courseId: string, id: string, data: Partial<QuizInput>) => instructorFetch<Quiz>(`/instructor/courses/${courseId}/quizzes/${id}`, json("PUT", data));
export const deleteQuiz = (courseId: string, id: string) => instructorFetch<{ message: string }>(`/instructor/courses/${courseId}/quizzes/${id}`, json("DELETE"));
export const getQuestions = (courseId: string, quizId: string) => instructorFetch<Question[]>(`/instructor/courses/${courseId}/quizzes/${quizId}/questions`);
export const createQuestion = (courseId: string, quizId: string, data: QuestionInput) => instructorFetch<Question>(`/instructor/courses/${courseId}/quizzes/${quizId}/questions`, json("POST", data));
export const updateQuestion = (courseId: string, quizId: string, id: string, data: Partial<QuestionInput>) => instructorFetch<Question>(`/instructor/courses/${courseId}/quizzes/${quizId}/questions/${id}`, json("PUT", data));
export const deleteQuestion = (courseId: string, quizId: string, id: string) => instructorFetch<{ message: string }>(`/instructor/courses/${courseId}/quizzes/${quizId}/questions/${id}`, json("DELETE"));
export const getAnswers = (courseId: string, quizId: string, questionId: string) => instructorFetch<Answer[]>(`/instructor/courses/${courseId}/quizzes/${quizId}/questions/${questionId}/answers`);
export const createAnswer = (courseId: string, quizId: string, questionId: string, data: Pick<Answer, "text" | "is_correct">) => instructorFetch<Answer>(`/instructor/courses/${courseId}/quizzes/${quizId}/questions/${questionId}/answers`, json("POST", data));
export const deleteAnswer = (courseId: string, quizId: string, questionId: string, id: string) => instructorFetch<{ message: string }>(`/instructor/courses/${courseId}/quizzes/${quizId}/questions/${questionId}/answers/${id}`, json("DELETE"));
export const getEnrolledStudents = (courseId: string) => instructorFetch<EnrolledStudent[]>(`/instructor/courses/${courseId}/students`);
export const getStudentProgress = (courseId: string, studentId: string) => instructorFetch<StudentProgress>(`/instructor/courses/${courseId}/students/${studentId}/progress`);
export const getStudentQuizResults = (courseId: string, studentId: string) => instructorFetch<StudentQuizResult[]>(`/instructor/courses/${courseId}/students/${studentId}/quiz-results`);
export const getCourseAnalytics = (courseId: string) => instructorFetch<CourseAnalytics>(`/instructor/courses/${courseId}/analytics`);
export const getCourseCertificates = (courseId: string) => instructorFetch<Certificate[]>(`/instructor/courses/${courseId}/certificates`);

export const getQuizSubmissions = (courseId: string) => instructorFetch<import("@/types/learning").QuizSubmissionReview[]>(`/instructor/courses/${courseId}/quiz-submissions`);
export const reviewQuizSubmission = (courseId: string, attemptId: string, grades: { question_id: string; points_awarded: number; feedback: string }[]) => instructorFetch<import("@/types/learning").QuizResult>(`/instructor/courses/${courseId}/quiz-submissions/${attemptId}/review`, json("POST", { grades }));
