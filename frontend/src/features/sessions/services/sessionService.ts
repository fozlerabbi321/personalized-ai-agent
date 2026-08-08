import { SessionListResponse, SessionMessagesResponse } from "../types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const sessionService = {
  async getSessions(token: string): Promise<SessionListResponse> {
    const res = await fetch(`${API_URL}/api/sessions`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error("Failed to fetch sessions");
    }

    return res.json();
  },

  async getSessionMessages(
    sessionId: string,
    token: string
  ): Promise<SessionMessagesResponse> {
    const res = await fetch(`${API_URL}/api/sessions/${sessionId}/messages`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error("Failed to fetch session messages");
    }

    return res.json();
  },

  async deleteSession(sessionId: string, token: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/sessions/${sessionId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error("Failed to delete session");
    }
  },
};
