"use client";

import { useAuth } from "@/features/auth/context/AuthContext";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { ChatWindow } from "@/features/chat/components/ChatWindow";
import { Spinner } from "@/shared/components/ui/Spinner";

export default function HomePage() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#090d16] text-gray-300 gap-3 text-sm font-medium">
        <Spinner className="h-6 w-6 text-indigo-500" />
        <span>Initializing Athena AI...</span>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen w-screen items-center justify-center p-4 bg-[#090d16] relative overflow-hidden">
        {/* Glow ambient background graphics */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

        <LoginForm />
      </div>
    );
  }

  return <ChatWindow />;
}
