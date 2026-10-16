const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(message: string, readonly status: number) { super(message); }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("token");
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  const result: unknown = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("token");
      // Clear invalid session data and redirect unauthenticated users to login.
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    const detail = result && typeof result === "object" && "detail" in result ? (result as { detail?: unknown }).detail : undefined;
    throw new ApiError(typeof detail === "string" ? detail : response.status === 401 ? "Your session has expired. Please sign in again." : "We could not complete that request.", response.status);
  }
  return result as T;
}

export function apiUrl(path: string): string { return `${API_URL}${path}`; }
