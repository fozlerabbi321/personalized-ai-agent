"use client";

import React from "react";
import { MessageSquare, Trash2 } from "lucide-react";
import { Session } from "../types";
import { cn } from "@/shared/lib/cn";

interface SessionItemProps {
  session: Session;
  isActive: boolean;
  onSelect: (sessionId: string) => void;
  onDelete: (sessionId: string) => void;
}

export function SessionItem({
  session,
  isActive,
  onSelect,
  onDelete,
}: SessionItemProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this conversation?")) {
      onDelete(session.session_id);
    }
  };

  return (
    <div
      onClick={() => onSelect(session.session_id)}
      className={cn(
        "group relative flex items-center justify-between gap-3 px-3 py-2.5 rounded-xl cursor-pointer text-xs font-medium transition-all duration-200",
        isActive
          ? "bg-indigo-600/20 text-indigo-200 border border-indigo-500/30 shadow-sm"
          : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/60 border border-transparent"
      )}
    >
      <div className="flex items-center gap-2.5 min-w-0 overflow-hidden">
        <MessageSquare
          className={cn(
            "h-4 w-4 shrink-0 transition-colors",
            isActive ? "text-indigo-400" : "text-gray-500 group-hover:text-gray-400"
          )}
        />
        <span className="truncate">{session.title}</span>
      </div>

      <button
        onClick={handleDelete}
        className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-rose-400 transition-opacity p-1 rounded-md hover:bg-gray-800 shrink-0"
        title="Delete conversation"
      >
        <Trash2 className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
