export interface AnalyticsPoint {
  label: string;
  value: number;
}

export interface AnalyticsSummary {
  totalStudents: number;
  activeStudents: number;
  completionRate: number;
  averageScore: number;
}

export interface CourseAnalytics {
  courseId: string | number;
  enrollment: AnalyticsPoint[];
  completion: AnalyticsPoint[];
  summary: AnalyticsSummary;
}