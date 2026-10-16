export type ProductStatus = "Draft" | "Published" | "Archived";

export interface Product {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  status: ProductStatus;
  created_at: string;
  updated_at: string;
}

export interface ProductCourse {
  id: string;
  product_id: string | null;
  instructor_id: string;
  title: string;
  description: string;
  objectives: string | null;
  thumbnail: string | null;
  language: string;
  duration: number;
  category: string;
  level: string;
  status: string;
  created_at: string;
  updated_at: string;
}
