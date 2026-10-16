import type { Product, ProductCourse } from "@/types/product";
import { apiRequest } from "@/services/api-client";

async function productFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  return apiRequest<T>(path, init);
}

const json = <T>(method: string, body?: T): RequestInit => ({ method, body: body === undefined ? undefined : JSON.stringify(body) });

export const getInstructorProducts = () => productFetch<Product[]>("/instructor/products");
export const getProduct = (id: string) => productFetch<Product>(`/instructor/products/${id}`);
export const getProductCourses = (productId: string) => productFetch<ProductCourse[]>(`/instructor/products/${productId}/courses`);
export const createProductCourse = (productId: string, data: Partial<ProductCourse>) => productFetch<ProductCourse>(`/instructor/products/${productId}/courses`, json("POST", data));
