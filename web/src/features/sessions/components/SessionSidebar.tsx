"use client";

import React from "react";
import { Plus, Sparkles, LogOut, User as UserIcon } from "lucide-react";
import { SessionItem } from "./SessionItem";
import { Session } from "../types";
import { Button } from "@/shared/components/ui/Button";
import { Spinner } from "@/shared/components/ui/Spinner";
import { useAuth } from "@/features/auth/context/AuthContext";

interface SessionSidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  isLoading: boolean;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
}

export function SessionSidebar({
  sessions,
  activeSessionId,
  isLoading,
  onSelectSession,
  onNewChat,
  onDeleteSession,
}: SessionSidebarProps) {
  const { user, logout } = useAuth();

  return (
    <aside className="w-72 shrink-0 glass-panel border-r border-gray-800/80 flex flex-col h-full select-none">
      {/* Header / Brand */}
      <div className="p-4 border-b border-gray-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h1 className="text-xs font-bold text-white tracking-wide">Aria AI</h1>
            <p className="text-[10px] text-gray-400 font-medium">Personalized Agent</p>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <Button
          onClick={onNewChat}
          variant="primary"
          className="w-full justify-start text-xs font-semibold py-2.5 shadow-indigo-600/20"
        >
          <Plus className="h-4 w-4" />
          <span>New Chat</span>
        </Button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <div className="px-2 pb-2 text-[10px] font-bold uppercase tracking-wider text-gray-500">
          History
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-8 text-gray-500 gap-2 text-xs">
            <Spinner className="h-4 w-4" />
            <span>Loading threads...</span>
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-8 text-xs text-gray-500 px-2">
            No previous chats yet. Start a new conversation!
          </div>
        ) : (
          sessions.map((session) => (
            <SessionItem
              key={session.session_id}
              session={session}
              isActive={activeSessionId === session.session_id}
              onSelect={onSelectSession}
              onDelete={onDeleteSession}
            />
          ))
        )}
      </div>

      {/* User Profile / Logout Footer */}
      {user && (
        <div className="p-3 border-t border-gray-800/80 bg-gray-900/40">
          <div className="flex items-center justify-between gap-2 p-2 rounded-xl bg-gray-800/40 border border-gray-800">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="h-7 w-7 rounded-lg bg-gray-700 flex items-center justify-center text-gray-300 text-xs font-bold shrink-0">
                <UserIcon className="h-3.5 w-3.5" />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium text-gray-200 truncate">{user.email}</p>
                <p className="text-[9px] text-emerald-400 font-medium">Logged in</p>
              </div>
            </div>

            <button
              onClick={logout}
              className="text-gray-400 hover:text-rose-400 transition-colors p-1.5 rounded-lg hover:bg-gray-800"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </aside>
  );
}
