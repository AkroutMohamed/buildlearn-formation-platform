export type CourseCategory = "Outillage" | "Ã‰tanchÃ©itÃ©" | "Gypstant";
export type CourseLevel = "Beginner" | "Intermediate" | "Advanced";
export type CourseStatus = "Draft" | "Published" | "Archived";
export interface Course { id: string; instructor_id: string; product_id: string | null; product?: { id: string; name: string; description: string | null; category: string | null; status: string }; title: string; description: string; objectives: string | null; thumbnail: string | null; language: string; duration: number; category: CourseCategory; level: CourseLevel; status: CourseStatus; created_at: string; updated_at: string; }
export interface CourseDetail extends Course { modules: { id: string; title: string; order_index: number; lesson_count: number }[]; }
export type CourseInput = Pick<Course, "title" | "description" | "objectives" | "thumbnail" | "language" | "duration" | "category" | "level">;
export interface Module { id: string; course_id: string; title: string; description: string | null; order_index: number; }
export type ModuleInput = Pick<Module, "title" | "description" | "order_index">;
export interface Lesson { id: string; module_id: string; title: string; content: string | null; duration_minutes: number | null; order_index: number; is_published: boolean; }
export type LessonInput = Pick<Lesson, "title" | "content" | "duration_minutes" | "order_index" | "is_published">;
export interface Resource { id: string; lesson_id: string; title: string; url: string; resource_type: string | null; description: string | null; }
export interface RecordedVideo { id: string; lesson_id: string; title: string; description: string | null; video_url: string; duration_seconds: number | null; thumbnail_url: string | null; created_at: string; updated_at: string; }
export interface LiveSession { id: string; lesson_id: string; title: string; description: string | null; scheduled_start: string; scheduled_end: string; meeting_url: string; status: string; recording_url: string | null; created_at: string; updated_at: string; }
export type LiveSessionStatus = "UPCOMING" | "LIVE" | "COMPLETED" | "CANCELLED";
export interface Quiz { id: string; course_id: string; title: string; description: string | null; }
export type QuizInput = Pick<Quiz, "title" | "description">;
export interface Question { id: string; quiz_id: string; text: string; question_type: string; points: number; order_index: number; }
export type QuestionInput = Pick<Question, "text" | "question_type" | "points" | "order_index"> & { correct_yes?: boolean };
export interface Answer { id: string; question_id: string; text: string; is_correct: boolean; }
export interface EnrolledStudent { id: string; first_name: string; last_name: string; email: string; enrollment_id: string; status: string; enrolled_at: string; }
export interface StudentProgress { student_id: string; course_id: string; completed_lessons: number; total_lessons: number; completion_percent: number; last_updated_at: string | null; }
export interface StudentQuizResult { id: string; quiz_id: string; quiz_title: string; score: number; correct_answers: number; total_questions: number; completed_at: string; }
export interface CourseAnalytics { total_students: number; completed_students: number; completion_rate: number; average_quiz_score: number; total_lessons: number; completed_lessons: number; average_progress: number; }
export interface Certificate { id: string; course_id: string; course_title: string; issued_at: string; certificate_url: string | null; }
