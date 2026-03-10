"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GoreMark } from "@/components/gore-mark";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login(email, password);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error al iniciar sesión";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
      {/* Background gradient — GORE institutional */}
      <div
        className="absolute inset-0"
        style={{
          background: "linear-gradient(135deg, #196AB0 0%, #031B5F 50%, #1A2658 100%)",
        }}
      />

      {/* Subtle pattern overlay */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      {/* Content */}
      <div className="relative z-10 w-full max-w-sm px-4">
        {/* Logo & brand */}
        <div className="flex flex-col items-center mb-8 animate-in fade-in duration-300 fill-mode-both">
          <GoreMark className="size-16 mb-4 drop-shadow-lg" />
          <h1 className="text-3xl font-bold text-white tracking-tight font-serif">
            GORE_OS
          </h1>
          <p className="text-sm text-white/60 mt-1">
            Sistema Operativo Institucional
          </p>
        </div>

        {/* Login card */}
        <div className="rounded-xl bg-white/[0.07] backdrop-blur-xl border border-white/[0.12] shadow-2xl p-6 animate-in fade-in duration-300 delay-150 fill-mode-both">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-sm font-medium text-white/80">
                Correo electrónico
              </label>
              <Input
                id="email"
                type="email"
                placeholder="usuario@gore.cl"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
                autoComplete="email"
                className="bg-white/10 border-white/15 text-white placeholder:text-white/40 focus:border-white/30 focus:ring-white/20"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="password" className="text-sm font-medium text-white/80">
                Contraseña
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                autoComplete="current-password"
                className="bg-white/10 border-white/15 text-white placeholder:text-white/40 focus:border-white/30 focus:ring-white/20"
              />
            </div>
            {error && (
              <div className="rounded-md bg-red-500/20 border border-red-400/30 px-3 py-2 text-sm text-red-200">
                {error}
              </div>
            )}
            <Button
              type="submit"
              className="w-full bg-white text-[#031B5F] hover:bg-white/90 font-semibold"
              disabled={isLoading}
            >
              {isLoading ? "Ingresando..." : "Ingresar"}
            </Button>
          </form>
        </div>
      </div>

      {/* Footer */}
      <p className="relative z-10 mt-8 text-xs text-white/40 animate-in fade-in duration-300 delay-300 fill-mode-both">
        Gobierno Regional de Ñuble · {new Date().getFullYear()}
      </p>
    </div>
  );
}

