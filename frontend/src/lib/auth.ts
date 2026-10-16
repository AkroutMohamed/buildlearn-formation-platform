import type { UserRole } from "@/types/user";

interface JwtPayload {
  role?: unknown;
  exp?: unknown;
}

function decodeBase64Url(value: string): string {
  const base64 = value.replace(/-/g, "+").replace(/_/g, "/");
  return decodeURIComponent(
    atob(base64)
      .split("")
      .map((character) => `%${character.charCodeAt(0).toString(16).padStart(2, "0")}`)
      .join(""),
  );
}

export function getTokenRole(token: string): UserRole | null {
  try {
    const payloadPart = token.split(".")[1];
    if (!payloadPart) return null;
    const payload = JSON.parse(decodeBase64Url(payloadPart)) as JwtPayload;
    if (typeof payload.exp === "number" && payload.exp * 1000 <= Date.now()) return null;
    return payload.role === "student" || payload.role === "instructor" || payload.role === "admin" ? payload.role : null;
  } catch {
    return null;
  }
}

export function getStoredRole(): UserRole | null {
  if (typeof window === "undefined") return null;
  const token = localStorage.getItem("token");
  const role = token ? getTokenRole(token) : null;
  if (!role && token) localStorage.removeItem("token");
  return role;
}

export function getDashboardPath(role: UserRole): string {
  return `/${role}/dashboard`;
}

export function logout(navigate?: (path: string) => void): void {
  localStorage.removeItem("token");
  if (typeof window === "undefined") return;
  if (navigate) {
    navigate("/login");
  } else {
    window.location.assign("/login");
  }
}
