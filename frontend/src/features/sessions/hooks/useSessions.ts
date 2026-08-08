"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/features/auth/context/AuthContext";
import { sessionService } from "../services/sessionService";
import { Session } from "../types";

export function useSessions() {
  const { token } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await sessionService.getSessions(token);
      setSessions(data.sessions);
    } catch (err: any) {
      setError(err.message || "Failed to load chat history");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const deleteSession = async (sessionId: string) => {
    if (!token) return;
    try {
      await sessionService.deleteSession(sessionId, token);
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    sessions,
    isLoading,
    error,
    refreshSessions: fetchSessions,
    deleteSession,
  };
}
