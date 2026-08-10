import { apiClient } from "@/shared/lib/apiClient";
import { SessionListResponse, SessionMessagesResponse } from "../types";

export const sessionService = {
  async getSessions(): Promise<SessionListResponse> {
    return apiClient.get<SessionListResponse>("/api/sessions", true);
  },

  async getSessionMessages(sessionId: string): Promise<SessionMessagesResponse> {
    return apiClient.get<SessionMessagesResponse>(`/api/sessions/${sessionId}/messages`, true);
  },

  async deleteSession(sessionId: string): Promise<void> {
    return apiClient.delete(`/api/sessions/${sessionId}`, true);
  },
};
