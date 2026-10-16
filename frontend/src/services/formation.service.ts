import type { FormationPage } from "@/types/formation";
import { apiRequest } from "@/services/api-client";

export async function getFormations(page: number, limit: number, filters: { search?: string; category?: string; level?: string; language?: string } = {}): Promise<FormationPage> {
  const query = new URLSearchParams({ page: String(page), limit: String(limit) });
  Object.entries(filters).forEach(([key, value]) => { if (value) query.set(key, value); });
  return apiRequest<FormationPage>(`/public/courses?${query}`);
}
