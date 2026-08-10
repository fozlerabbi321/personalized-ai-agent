"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/context/AuthContext";
import { sessionService } from "../services/sessionService";
import { Session } from "../types";

export const SESSION_QUERY_KEY = ["sessions"] as const;

export function useSessions() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: SESSION_QUERY_KEY,
    queryFn: () => sessionService.getSessions(),
    enabled: Boolean(token),
    staleTime: 1000 * 30, // 30s stale time
  });

  const deleteMutation = useMutation({
    mutationFn: (sessionId: string) => sessionService.deleteSession(sessionId),
    onSuccess: (_, deletedId) => {
      queryClient.setQueryData<{ sessions: Session[]; total: number }>(
        SESSION_QUERY_KEY,
        (old) => {
          if (!old) return { sessions: [], total: 0 };
          const updated = old.sessions.filter((s) => s.session_id !== deletedId);
          return { sessions: updated, total: updated.length };
        }
      );
    },
  });

  return {
    sessions: data?.sessions || [],
    isLoading,
    error: error instanceof Error ? error.message : null,
    refreshSessions: refetch,
    deleteSession: deleteMutation.mutateAsync,
  };
}
