import type { Course } from "@/types/instructor";
import type { InstructorResponse } from "@/types/user";
import type { Product } from "@/types/product";
import { apiRequest } from "@/services/api-client";

export type { InstructorResponse };

export async function getAdminDashboard(): Promise<{ message: string }> {
  return apiRequest<{ message: string }>("/admin/dashboard");
}

export async function getPendingInstructorRequests(): Promise<InstructorResponse[]> {
  return apiRequest<InstructorResponse[]>("/admin/instructor-requests");
}

export async function approveInstructor(userId: string): Promise<InstructorResponse> {
  return apiRequest<InstructorResponse>(`/admin/instructor-requests/${userId}/approve`, {
    method: "POST",
  });
}

export async function rejectInstructor(userId: string): Promise<InstructorResponse> {
  return apiRequest<InstructorResponse>(`/admin/instructor-requests/${userId}/reject`, {
    method: "POST",
  });
}
export async function getInstructors(): Promise<InstructorResponse[]> {
  return apiRequest<InstructorResponse[]>("/admin/instructors");
}

export async function createInstructor(data: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}): Promise<InstructorResponse> {
  return apiRequest<InstructorResponse>("/admin/instructors", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getAdminProducts(): Promise<Product[]> {
  return apiRequest<Product[]>("/admin/products");
}

export async function getAdminProduct(id: string): Promise<Product> {
  return apiRequest<Product>(`/admin/products/${id}`);
}

export async function createAdminProduct(data: {
  name: string;
  description?: string | null;
  category?: string | null;
  status: string;
}): Promise<Product> {
  return apiRequest<Product>("/admin/products", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAdminProduct(id: string, data: Partial<{
  name: string;
  description: string | null;
  category: string | null;
  status: string;
}>): Promise<Product> {
  return apiRequest<Product>(`/admin/products/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteAdminProduct(id: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/admin/products/${id}`, {
    method: "DELETE",
  });
}

export async function publishAdminProduct(id: string): Promise<Product> {
  return apiRequest<Product>(`/admin/products/${id}/publish`, {
    method: "PATCH",
  });
}

export async function unpublishAdminProduct(id: string): Promise<Product> {
  return apiRequest<Product>(`/admin/products/${id}/unpublish`, {
    method: "PATCH",
  });
}

export async function getAdminCourses(): Promise<Course[]> {
  return apiRequest<Course[]>("/admin/courses");
}

export async function getAdminCourse(id: string): Promise<Course> {
  return apiRequest<Course>(`/admin/courses/${id}`);
}

export async function createAdminCourse(data: {
  title: string;
  description: string;
  objectives?: string | null;
  thumbnail?: string | null;
  language?: string;
  duration?: number;
  category: string;
  level: string;
}): Promise<Course> {
  return apiRequest<Course>("/admin/courses", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAdminCourse(id: string, data: Partial<{
  title: string;
  description: string;
  objectives: string | null;
  thumbnail: string | null;
  language: string;
  duration: number;
  category: string;
  level: string;
  status: string;
}>): Promise<Course> {
  return apiRequest<Course>(`/admin/courses/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteAdminCourse(id: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/admin/courses/${id}`, {
    method: "DELETE",
  });
}

export async function publishAdminCourse(id: string): Promise<Course> {
  return apiRequest<Course>(`/admin/courses/${id}/publish`, {
    method: "PATCH",
  });
}

export async function unpublishAdminCourse(id: string): Promise<Course> {
  return apiRequest<Course>(`/admin/courses/${id}/unpublish`, {
    method: "PATCH",
  });
}

export async function getCourseInstructors(courseId: string): Promise<InstructorResponse[]> {
  return apiRequest<InstructorResponse[]>(`/admin/courses/${courseId}/instructors`);
}

export async function assignCourseInstructor(courseId: string, instructorId: string): Promise<InstructorResponse> {
  return apiRequest<InstructorResponse>(`/admin/courses/${courseId}/instructors`, {
    method: "POST",
    body: JSON.stringify({ instructor_id: instructorId }),
  });
}

export async function unassignCourseInstructor(courseId: string, instructorId: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/admin/courses/${courseId}/instructors/${instructorId}`, {
    method: "DELETE",
  });
}

export async function getProductInstructors(productId: string): Promise<InstructorResponse[]> {
  return apiRequest<InstructorResponse[]>(`/admin/products/${productId}/instructors`);
}

export async function assignProductInstructor(productId: string, instructorId: string): Promise<InstructorResponse> {
  return apiRequest<InstructorResponse>(`/admin/products/${productId}/instructors`, {
    method: "POST",
    body: JSON.stringify({ instructor_id: instructorId }),
  });
}

export async function unassignProductInstructor(productId: string, instructorId: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/admin/products/${productId}/instructors/${instructorId}`, {
    method: "DELETE",
  });
}
