"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/features/auth/context/AuthContext";
import { sessionService } from "@/features/sessions/services/sessionService";
import { chatService } from "../services/chatService";
import { Message } from "../types";

export function useChat(initialSessionId?: string) {
  const { token } = useAuth();
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
        const data = await sessionService.getSessionMessages(targetSessionId, token);
        const mapped: Message[] = data.messages.map((m) => ({
          id: m.message_id,
          role: m.role,
          content: m.content,
          widget_json: m.widget_json,
          timestamp: m.created_at,
        }));
        setMessages(mapped);
        setSessionId(targetSessionId);
      } catch (err: any) {
        setError(err.message || "Failed to load session messages");
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

  const sendMessage = async (text: string) => {
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
      },
      onError: (errMessage) => {
        setError(errMessage);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, isStreaming: false, content: msg.content || "⚠️ Error generating response." }
              : msg
          )
        );
        setIsStreaming(false);
      },
    });
  };

  const startNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  };

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
