export interface AuthenticatedUser {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: "student" | "instructor" | "admin";
  instructor_status: "PENDING" | "ACTIVE" | "REJECTED";
}

export type UserRole = "student" | "instructor" | "admin";
export type InstructorStatus = "PENDING" | "ACTIVE" | "REJECTED";

export interface InstructorResponse {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: "student" | "instructor" | "admin";
  instructor_status: "PENDING" | "ACTIVE" | "REJECTED";
}

