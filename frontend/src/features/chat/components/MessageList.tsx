"use client";

import React, { useEffect, useRef } from "react";
import { Message } from "../types";
import { MessageBubble } from "./MessageBubble";
import { Sparkles } from "lucide-react";
import { Spinner } from "@/shared/components/ui/Spinner";
import { SUGGESTED_PROMPTS } from "../constants";

interface MessageListProps {
  messages: Message[];
  isLoadingMessages: boolean;
  onSuggestedPrompt?: (text: string) => void;
}

export function MessageList({
  messages,
  isLoadingMessages,
  onSuggestedPrompt,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (isLoadingMessages) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-3 text-gray-400 text-xs">
        <Spinner className="h-6 w-6 text-indigo-500" />
        <span>Fetching message history...</span>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-xl mx-auto">
        <div className="h-14 w-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-xl shadow-indigo-500/20 mb-4 animate-bounce">
          <Sparkles className="h-7 w-7" />
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight mb-2">
          How can Athena help you today?
        </h2>
        <p className="text-xs text-gray-400 leading-relaxed mb-8">
          Ask Bitcoin & crypto questions, analyze live market trends with interactive charts,
          or get personalized trading insights.
        </p>

        {/* Prompt Suggestions */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full">
          {SUGGESTED_PROMPTS.map((item, idx) => {
            const Icon = item.icon;
            return (
              <button
                key={idx}
                onClick={() => onSuggestedPrompt && onSuggestedPrompt(item.prompt)}
                className="flex flex-col items-start p-3.5 rounded-xl glass-card border border-gray-800 hover:border-indigo-500/40 hover:bg-indigo-950/20 transition-all text-left group cursor-pointer"
              >
                <Icon className="h-4 w-4 text-indigo-400 mb-2 group-hover:scale-110 transition-transform" />
                <span className="text-xs font-semibold text-gray-200 mb-1">
                  {item.title}
                </span>
                <span className="text-[11px] text-gray-400 line-clamp-2">
                  &ldquo;{item.prompt}&rdquo;
                </span>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2 max-w-4xl w-full mx-auto">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
