"use client";

import React from "react";
import { Message } from "../types";
import { Avatar } from "@/shared/components/ui/Avatar";
import { WidgetRenderer } from "@/features/widgets/WidgetRenderer";
import { cn } from "@/shared/lib/cn";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isHuman = message.role === "human";

  return (
    <div
      className={cn(
        "flex w-full gap-3 py-4 px-2 sm:px-4 rounded-2xl transition-colors",
        isHuman ? "flex-row-reverse" : "flex-row"
      )}
    >
      <Avatar role={message.role} className="mt-0.5" />

      <div
        className={cn(
          "flex flex-col max-w-[85%] sm:max-w-[75%]",
          isHuman ? "items-end" : "items-start"
        )}
      >
        <div
          className={cn(
            "px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap break-words shadow-sm",
            isHuman
              ? "bg-indigo-600 text-white rounded-tr-none shadow-indigo-600/20"
              : "glass-card text-gray-100 rounded-tl-none border border-gray-800"
          )}
        >
          {message.content ? (
            <span>{message.content}</span>
          ) : message.isStreaming ? (
            <span className="inline-flex items-center gap-1.5 text-gray-400 font-medium text-xs">
              <span className="h-2 w-2 rounded-full bg-indigo-500 animate-ping" />
              Aria is thinking...
            </span>
          ) : (
            <span className="text-gray-500 italic">No content</span>
          )}

          {message.isStreaming && message.content && (
            <span className="inline-block w-2 h-4 ml-1 bg-indigo-400 animate-pulse rounded-sm vertical-middle" />
          )}
        </div>

        {/* SDUI Dynamic Widget rendering */}
        {message.widget_json && (
          <div className="w-full mt-2">
            <WidgetRenderer widget={message.widget_json} />
          </div>
        )}
      </div>
    </div>
  );
}
