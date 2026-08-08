"use client";

import React from "react";
import { useChat } from "../hooks/useChat";
import { useSessions } from "@/features/sessions/hooks/useSessions";
import { SessionSidebar } from "@/features/sessions/components/SessionSidebar";
import { MessageList } from "./MessageList";
import { InputBar } from "./InputBar";
import { Menu } from "lucide-react";

interface ChatWindowProps {
  initialSessionId?: string;
}

export function ChatWindow({ initialSessionId }: ChatWindowProps) {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const {
    messages,
    sessionId,
    isStreaming,
    isLoadingMessages,
    error,
    sendMessage,
    startNewChat,
    loadMessages,
  } = useChat(initialSessionId);

  const {
    sessions,
    isLoading: isLoadingSessions,
    refreshSessions,
    deleteSession,
  } = useSessions();

  const handleSelectSession = (selectedId: string) => {
    loadMessages(selectedId);
  };

  const handleNewChat = () => {
    startNewChat();
  };

  const handleSend = async (text: string) => {
    await sendMessage(text);
    // Refresh sessions list after message finishes
    refreshSessions();
  };

  const handleDeleteSession = async (deletedId: string) => {
    await deleteSession(deletedId);
    if (sessionId === deletedId) {
      startNewChat();
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#090d16] text-gray-100">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "block" : "hidden"
        } md:block h-full shrink-0 transition-all z-20`}
      >
        <SessionSidebar
          sessions={sessions}
          activeSessionId={sessionId}
          isLoading={isLoadingSessions}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
        />
      </div>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full min-w-0 relative">
        {/* Top Navbar */}
        <header className="h-14 border-b border-gray-800/80 px-4 flex items-center justify-between bg-gray-950/40 backdrop-blur-sm shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 md:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div>
              <h2 className="text-sm font-semibold text-white">
                {sessionId ? "Chat Session" : "New Conversation"}
              </h2>
              {sessionId && (
                <p className="text-[10px] text-gray-400 font-mono">
                  ID: {sessionId.slice(0, 8)}...
                </p>
              )}
            </div>
          </div>
        </header>

        {/* Error banner */}
        {error && (
          <div className="mx-4 mt-3 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium flex items-center justify-between">
            <span>{error}</span>
          </div>
        )}

        {/* Message Viewport */}
        <MessageList
          messages={messages}
          isLoadingMessages={isLoadingMessages}
          onSuggestedPrompt={handleSend}
        />

        {/* Input Bar */}
        <InputBar onSend={handleSend} disabled={isStreaming} />
      </main>
    </div>
  );
}
