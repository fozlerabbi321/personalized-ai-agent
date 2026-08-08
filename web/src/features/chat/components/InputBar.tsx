"use client";

import React, { useState, KeyboardEvent } from "react";
import { Send, Sparkles } from "lucide-react";
import { cn } from "@/shared/lib/cn";

interface InputBarProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function InputBar({ onSend, disabled }: InputBarProps) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text);
      setText("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-4 border-t border-gray-800/80 bg-gray-950/60 backdrop-blur-md sticky bottom-0 z-10">
      <div className="max-w-4xl mx-auto flex items-center gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Ask Athena anything... (e.g. BTC price, market analysis)"
            className="w-full pl-4 pr-12 py-3 bg-gray-900/90 text-gray-100 text-sm rounded-2xl border border-gray-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder-gray-500 shadow-inner"
          />

          <button
            onClick={handleSend}
            disabled={disabled || !text.trim()}
            className={cn(
              "absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-xl text-white transition-all duration-200",
              text.trim() && !disabled
                ? "bg-indigo-600 hover:bg-indigo-500 shadow-md shadow-indigo-600/30 scale-100"
                : "bg-gray-800 text-gray-500 cursor-not-allowed scale-95"
            )}
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
      <p className="text-[10px] text-center text-gray-500 mt-2 flex items-center justify-center gap-1">
        <Sparkles className="h-3 w-3 text-indigo-400" />
        Athena streams dynamic Server-Driven UI (SDUI) widgets based on your query intent.
      </p>
    </div>
  );
}
