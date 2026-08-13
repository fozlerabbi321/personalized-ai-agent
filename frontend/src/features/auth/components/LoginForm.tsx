"use client";

import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Button } from "@/shared/components/ui/Button";
import { Input } from "@/shared/components/ui/Input";
import { Sparkles, Lock, Mail } from "lucide-react";

export function LoginForm() {
  const { login, register } = useAuth();
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (isRegistering) {
        await register(email, password);
      } else {
        await login(email, password);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Authentication failed";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 glass-panel rounded-3xl border border-indigo-500/20 shadow-2xl shadow-indigo-950/50">
      <div className="flex flex-col items-center text-center mb-8">
        <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 mb-3">
          <Sparkles className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          {isRegistering ? "Create Account" : "Welcome Back"}
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          {isRegistering
            ? "Register to start chatting with Lumen AI"
            : "Login to access your AI sessions & SDUI widgets"}
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium text-center">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-xs font-semibold text-gray-300 block mb-1.5 flex items-center gap-1.5">
            <Mail className="h-3.5 w-3.5 text-indigo-400" />
            Email Address
          </label>
          <Input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="alice@example.com"
          />
        </div>

        <div>
          <label className="text-xs font-semibold text-gray-300 block mb-1.5 flex items-center gap-1.5">
            <Lock className="h-3.5 w-3.5 text-indigo-400" />
            Password
          </label>
          <Input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />
        </div>

        <Button
          type="submit"
          isLoading={isLoading}
          variant="primary"
          className="w-full py-3 mt-2 text-sm font-semibold shadow-indigo-600/30"
        >
          {isRegistering ? "Sign Up" : "Sign In"}
        </Button>
      </form>

      <div className="mt-6 pt-4 border-t border-gray-800/80 text-center">
        <p className="text-xs text-gray-400">
          {isRegistering ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            onClick={() => {
              setIsRegistering(!isRegistering);
              setError(null);
            }}
            className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-4 ml-1"
          >
            {isRegistering ? "Sign In" : "Sign Up"}
          </button>
        </p>
      </div>

      {/* Demo Credentials hint */}
      <div className="mt-6 p-3 rounded-xl bg-gray-900/60 border border-gray-800 text-[11px] text-gray-400">
        <span className="font-bold text-gray-300 block mb-0.5">🌱 Test Credentials (Seeder):</span>
        <span>Email: <code className="text-indigo-300">alice@example.com</code> | Pass: <code className="text-indigo-300">Password123!</code></span>
      </div>
    </div>
  );
}
