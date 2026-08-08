"use client";

import React from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/features/auth/context/AuthContext";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { ChatWindow } from "@/features/chat/components/ChatWindow";
import { Spinner } from "@/shared/components/ui/Spinner";

export default function SessionChatPage() {
  const params = useParams();
  const sessionId = Array.isArray(params?.sessionId)
    ? params.sessionId[0]
    : (params?.sessionId as string);

  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#090d16] text-gray-300 gap-3 text-sm">
        <Spinner className="h-6 w-6 text-indigo-500" />
        <span>Loading session...</span>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen w-screen items-center justify-center p-4 bg-[#090d16]">
        <LoginForm />
      </div>
    );
  }

  return <ChatWindow initialSessionId={sessionId} />;
}
