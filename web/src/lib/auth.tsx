"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { api } from "./api";
import type { User } from "@/types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = api.getToken();
    if (token) {
      const stored = localStorage.getItem("goreos_user");
      if (stored) {
        try {
          setUser(JSON.parse(stored));
        } catch {
          api.clearToken();
          localStorage.removeItem("goreos_user");
        }
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const data = await api.login(email, password);
    api.setToken(data.access_token);
    localStorage.setItem("goreos_user", JSON.stringify(data.user));
    setUser(data.user);
    router.push("/dashboard");
  };

  const logout = () => {
    api.clearToken();
    localStorage.removeItem("goreos_user");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
