"use client";

import { useCallback, useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/features/auth/context/AuthContext";
import { sessionService } from "@/features/sessions/services/sessionService";
import { SESSION_QUERY_KEY } from "@/features/sessions/hooks/useSessions";
import { chatService } from "../services/chatService";
import { Message } from "../types";

export function useChat(initialSessionId?: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load existing session messages if sessionId is given
  const loadMessages = useCallback(
    async (targetSessionId: string) => {
      if (!token) return;
      setIsLoadingMessages(true);
      setError(null);
      try {
        const data = await sessionService.getSessionMessages(targetSessionId);
        const mapped: Message[] = data.messages.map((m) => {
          let parsedWidget = m.widget_json;
          if (typeof parsedWidget === "string") {
            try {
              parsedWidget = JSON.parse(parsedWidget);
            } catch {
              parsedWidget = null;
            }
          }
          return {
            id: m.message_id,
            role: m.role,
            content: m.content,
            widget_json: parsedWidget as Record<string, unknown> | undefined,
            timestamp: m.created_at,
          };
        });
        setMessages(mapped);
        setSessionId(targetSessionId);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to load session messages";
        setError(msg);
      } finally {
        setIsLoadingMessages(false);
      }
    },
    [token]
  );

  useEffect(() => {
    if (initialSessionId) {
      loadMessages(initialSessionId);
    } else {
      setMessages([]);
      setSessionId(null);
    }
  }, [initialSessionId, loadMessages]);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!token || !text.trim() || isStreaming) return;

      const currentSessionId = sessionId || crypto.randomUUID();
      if (!sessionId) {
        setSessionId(currentSessionId);
      }

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "human",
        content: text,
        timestamp: new Date().toISOString(),
      };

      const assistantMessageId = crypto.randomUUID();
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        isStreaming: true,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setIsStreaming(true);
      setError(null);

      await chatService.streamChat(text, currentSessionId, token, {
        onToken: (chunk) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        onWidget: (widgetJson) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, widget_json: widgetJson }
                : msg
            )
          );
        },
        onDone: (finalSessionId) => {
          setSessionId(finalSessionId);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, isStreaming: false }
                : msg
            )
          );
          setIsStreaming(false);
          // ✅ FIX RACE CONDITION: Invalidate sessions cache only AFTER SSE stream completes
          queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEY });
        },
        onError: (errMessage) => {
          setError(errMessage);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    isStreaming: false,
                    content: msg.content || "⚠️ Error generating response.",
                  }
                : msg
            )
          );
          setIsStreaming(false);
        },
      });
    },
    [token, sessionId, isStreaming, queryClient]
  );

  const startNewChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, []);

  return {
    messages,
    sessionId,
    isStreaming,
    isLoadingMessages,
    error,
    sendMessage,
    startNewChat,
    loadMessages,
  };
}
