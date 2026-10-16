import type { AuthenticatedUser, UserRole } from "@/types/user";
import { apiRequest } from "@/services/api-client";

export async function registerUser(data: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  role: UserRole;
}): Promise<AuthenticatedUser> {
  return apiRequest<AuthenticatedUser>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function loginUser(data: {
  email: string;
  password: string;
}): Promise<{ access_token: string; token_type: string }> {
  const formData = new URLSearchParams();

  formData.append("username", data.email); // IMPORTANT: username, not email
  formData.append("password", data.password);

  return apiRequest<{ access_token: string; token_type: string }>("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });
}

export async function getAuthenticatedUser(): Promise<AuthenticatedUser> {
  if (!localStorage.getItem("token")) throw new Error("No active session.");
  return apiRequest<AuthenticatedUser>("/auth/me");
}
 
