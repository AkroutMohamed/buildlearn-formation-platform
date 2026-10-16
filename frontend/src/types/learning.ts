export interface Resource { id: string; title: string; url: string; resource_type: string; description: string | null; }
export interface RecordedVideo { id: string; title: string; description: string | null; video_url: string; duration_seconds: number | null; thumbnail_url: string | null; created_at: string; updated_at: string; }
export interface LiveSession { id: string; title: string; description: string | null; scheduled_start: string; scheduled_end: string; meeting_url: string; status: string; recording_url: string | null; created_at: string; updated_at: string; }
export interface Lesson { id: string; title: string; content: string; duration_minutes: number; order_index: number; is_completed?: boolean; resources: Resource[]; video: RecordedVideo | null; live_sessions: LiveSession[]; }
export interface CourseModule { id: string; title: string; description: string | null; order_index: number; lessons: Lesson[]; }
export interface QuizLink { id: string; title: string; description: string | null; }
export interface CourseDetails {
  id: string; title: string; description: string; thumbnail: string | null; instructor: string;
  category: string; level: string; language: string; duration: number; objectives: string | null;
  is_enrolled: boolean; completion_percentage: number; completed_lessons: number; total_lessons: number;
  modules: CourseModule[]; quizzes: QuizLink[];
}
export interface PublicCourseDetails {
  id: string; title: string; description: string; thumbnail: string | null; instructor: string;
  category: string; level: string; language: string; duration: number; objectives: string | null;
  modules: PublicCourseModule[]; quizzes: QuizLink[];
}
export interface PublicCourseModule {
  id: string; title: string; description: string | null; order_index: number;
  lessons: PublicLessonSummary[];
}
export interface PublicLessonSummary {
  id: string; title: string; order_index: number; duration_minutes: number | null;
}
export interface MyCourse { id: string; title: string; instructor: string; thumbnail: string | null; progress: number; completed_lessons: number; total_lessons: number; status: string; }
export interface LessonDetails { id: string; course_id: string; title: string; content: string; duration_minutes: number; completion_percent: number; is_completed: boolean; resources: Resource[]; video: RecordedVideo | null; live_sessions: LiveSession[]; }
export interface QuizAnswer { id: string; text: string; }
export interface QuizQuestion { id: string; text: string; order_index: number; question_type: "multiple_choice" | "yes_no" | "written"; points: number; answers: QuizAnswer[]; }
export interface QuizDetails { id: string; title: string; description: string | null; questions: QuizQuestion[]; result?: QuizResult | null; }
export interface QuizResponseReview { question_id: string; question_text: string; question_type: string; points: number; points_awarded: number | null; is_correct: boolean | null; selected_answer: string | null; correct_answer: string | null; text_answer: string | null; feedback: string; }
export interface QuizResult { attempt_id?: string; quiz_result_id: string | null; status: "pending_review" | "graded"; score: number | null; percentage: number | null; passed: boolean | null; correct_answers: string[]; wrong_answers: string[]; pending_questions: number; responses: QuizResponseReview[]; }
export interface QuizSubmissionReview extends QuizResult { attempt_id: string; student_name: string; quiz_title: string; submitted_at: string; }
export interface CourseProgress { course_id: string; title: string; percentage: number; completed_lessons: number; remaining_lessons: number; }
export interface Certificate { id: string; course_id: string; course_title: string; issued_at: string; certificate_url: string | null; }
export interface Notification { id: string; title: string; message: string; is_read: boolean; created_at: string; }
export interface StudentDashboard { enrolled_courses: number; completed_courses: number; certificates_count: number; overall_progress: number; }
