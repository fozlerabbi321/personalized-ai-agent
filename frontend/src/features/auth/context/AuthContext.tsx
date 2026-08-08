"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { authService } from "../services/authService";
import { User } from "../types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const savedToken = localStorage.getItem("access_token");
    if (savedToken) {
      setToken(savedToken);
      authService
        .getMe(savedToken)
        .then(setUser)
        .catch(() => {
          localStorage.removeItem("access_token");
          setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const data = await authService.login(email, password);
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);
    const me = await authService.getMe(data.access_token);
    setUser(me);
  };

  const register = async (email: string, password: string) => {
    const data = await authService.register(email, password);
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);
    const me = await authService.getMe(data.access_token);
    setUser(me);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
