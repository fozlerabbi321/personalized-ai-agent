import React from "react";
import { cn } from "@/shared/lib/cn";
import { Bot, User } from "lucide-react";

interface AvatarProps {
  role: "human" | "assistant";
  className?: string;
}

export function Avatar({ role, className }: AvatarProps) {
  const isAssistant = role === "assistant";

  return (
    <div
      className={cn(
        "flex h-9 w-9 shrink-0 select-none items-center justify-center rounded-xl font-semibold shadow-md transition-transform duration-200",
        isAssistant
          ? "bg-gradient-to-br from-indigo-500 via-purple-600 to-indigo-700 text-white shadow-indigo-500/20"
          : "bg-gradient-to-br from-gray-700 to-gray-800 text-gray-200 border border-gray-600/50",
        className
      )}
    >
      {isAssistant ? <Bot className="h-5 w-5" /> : <User className="h-5 w-5" />}
    </div>
  );
}
