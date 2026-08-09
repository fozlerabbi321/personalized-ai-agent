import { apiClient } from "@/shared/lib/apiClient";
import { TokenResponse, User } from "../types";

export const authService = {
  async register(email: string, password: string): Promise<TokenResponse> {
    return apiClient.post<TokenResponse>("/api/auth/register", { email, password }, false);
  },

  async login(email: string, password: string): Promise<TokenResponse> {
    return apiClient.post<TokenResponse>("/api/auth/login", { email, password }, false);
  },

  async getMe(token?: string): Promise<User> {
    // If token passed explicitly (e.g. initial auth setup), use it or let apiClient tokenGetter handle it
    if (token) {
      const res = await fetch(`${apiClient.getBaseUrl()}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        throw new Error("Session expired");
      }
      return res.json();
    }
    return apiClient.get<User>("/api/auth/me", true);
  },
};
