"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";

// ─── Test user catalog ───────────────────────────────────────────────────────

interface TestUser {
  email: string;
  role: string;
  division?: string;
}

interface UserGroup {
  label: string;
  description: string;
  color: string;
  users: TestUser[];
}

const USER_GROUPS: UserGroup[] = [
  {
    label: "Ejecutores",
    description: "Formulan, revisan y ejecutan IPRs",
    color: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    users: [
      { email: "analista.dipir@goreos.cl", role: "ANALISTA", division: "DIPIR" },
      { email: "analista.diplade@goreos.cl", role: "ANALISTA", division: "DIPLADE" },
      { email: "rtf.daf@goreos.cl", role: "RTF", division: "DAF" },
      { email: "juridico@goreos.cl", role: "ASESOR_JURIDICO" },
      { email: "profesional.dit@goreos.cl", role: "ANALISTA", division: "DIT" },
      { email: "profesional.dideso@goreos.cl", role: "ANALISTA", division: "DIDESO" },
    ],
  },
  {
    label: "Supervisores",
    description: "Jefaturas de divisiones, departamentos y unidades",
    color: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    users: [
      { email: "jefe.daf@goreos.cl", role: "JEFE_DIVISION", division: "DAF" },
      { email: "jefe.dideso@goreos.cl", role: "JEFE_DIVISION", division: "DIDESO" },
      { email: "jefe.difoi@goreos.cl", role: "JEFE_DIVISION", division: "DIFOI" },
      { email: "jefe.dipir@goreos.cl", role: "JEFE_DIVISION", division: "DIPIR" },
      { email: "jefe.diplade@goreos.cl", role: "JEFE_DIVISION", division: "DIPLADE" },
      { email: "jefe.dit@goreos.cl", role: "JEFE_DIVISION", division: "DIT" },
      { email: "jefe.finanzas@goreos.cl", role: "JEFE_DEPARTAMENTO", division: "DAF" },
      { email: "jefe.ucr@goreos.cl", role: "JEFE_UNIDAD", division: "DAF" },
    ],
  },
  {
    label: "Estrategas",
    description: "Gobernanza, fiscalización y estrategia regional",
    color: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    users: [
      { email: "gobernador@goreos.cl", role: "GOBERNADOR" },
      { email: "regional@goreos.cl", role: "ADMIN_REGIONAL" },
      { email: "secretario.core@goreos.cl", role: "SECRETARIO_EJECUTIVO" },
      { email: "consejero1@goreos.cl", role: "CONSEJERO_REGIONAL" },
      { email: "consejero2@goreos.cl", role: "CONSEJERO_REGIONAL" },
    ],
  },
  {
    label: "DGI",
    description: "Control de gestión, procesos y transformación digital",
    color: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
    users: [
      { email: "jefe.dgi@goreos.cl", role: "JEFE_DGI" },
      { email: "control.gestion@goreos.cl", role: "ESP_CONTROL_GESTION" },
      { email: "procesos@goreos.cl", role: "ESP_PROCESOS" },
      { email: "td@goreos.cl", role: "ESP_TD" },
    ],
  },
  {
    label: "Sistema",
    description: "Administración de plataforma",
    color: "bg-rose-500/20 text-rose-300 border-rose-500/30",
    users: [
      { email: "admin@goreos.cl", role: "ADMIN_SISTEMA" },
    ],
  },
];

// ─── Readable role labels ────────────────────────────────────────────────────

const ROLE_LABELS: Record<string, string> = {
  ANALISTA: "Analista",
  RTF: "RTF",
  ASESOR_JURIDICO: "Asesor Jurídico",
  JEFE_DIVISION: "Jefe de División",
  JEFE_DEPARTAMENTO: "Jefe de Departamento",
  JEFE_UNIDAD: "Jefe de Unidad",
  GOBERNADOR: "Gobernador",
  ADMIN_REGIONAL: "Administrador Regional",
  SECRETARIO_EJECUTIVO: "Secretario Ejecutivo",
  CONSEJERO_REGIONAL: "Consejero Regional",
  JEFE_DGI: "Jefe DGI",
  ESP_CONTROL_GESTION: "Esp. Control de Gestión",
  ESP_PROCESOS: "Esp. Procesos",
  ESP_TD: "Esp. Transformación Digital",
  ADMIN_SISTEMA: "Administrador del Sistema",
};

// ─── API base ────────────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Component ───────────────────────────────────────────────────────────────

export default function DevLoginPage() {
  const [loadingEmail, setLoadingEmail] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleLogin(email: string) {
    setLoadingEmail(email);
    setError(null);

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", "admin123");

      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Credenciales inválidas");
      }

      const data = await res.json();
      localStorage.setItem("goreos_token", data.access_token);
      localStorage.setItem("goreos_user", JSON.stringify(data.user));
      localStorage.setItem("goreos_dev_mode", "true");
      // Clear sidebar nav state so defaultOpen applies fresh for new role
      Object.keys(localStorage)
        .filter((k) => k.startsWith("goreos_nav_"))
        .forEach((k) => localStorage.removeItem(k));
      window.location.href = "/dashboard";
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error al iniciar sesión";
      setError(message);
      setLoadingEmail(null);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Dev mode banner */}
      <div className="bg-amber-500/90 text-amber-950 text-center py-2.5 px-4 text-sm font-semibold tracking-wide">
        Modo Desarrollo — Seleccione usuario para entrar
      </div>

      {/* Header */}
      <div className="text-center pt-8 pb-6 px-4">
        <h1 className="text-2xl font-bold text-white tracking-tight">
          GORE_OS — Dev Login
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          24 usuarios de prueba con acceso inmediato
        </p>
      </div>

      {/* Error banner */}
      {error && (
        <div className="max-w-5xl mx-auto px-4 mb-4">
          <div className="rounded-lg bg-red-500/20 border border-red-400/30 px-4 py-2.5 text-sm text-red-300 text-center">
            {error}
          </div>
        </div>
      )}

      {/* User groups */}
      <div className="max-w-5xl mx-auto px-4 pb-12 space-y-8">
        {USER_GROUPS.map((group) => (
          <section key={group.label}>
            {/* Group header */}
            <div className="mb-3">
              <h2 className="text-lg font-semibold text-white">{group.label}</h2>
              <p className="text-xs text-slate-500">{group.description}</p>
            </div>

            {/* User cards grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2.5">
              {group.users.map((user) => {
                const isLoading = loadingEmail === user.email;
                return (
                  <button
                    key={user.email}
                    onClick={() => handleLogin(user.email)}
                    disabled={loadingEmail !== null}
                    className={`
                      relative text-left rounded-lg border px-3.5 py-3 transition-all
                      ${group.color}
                      hover:scale-[1.02] hover:brightness-125
                      disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                      focus:outline-none focus:ring-2 focus:ring-amber-400/50
                    `}
                  >
                    {isLoading && (
                      <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-black/40">
                        <Loader2 className="size-5 animate-spin text-white" />
                      </div>
                    )}
                    <div className="font-medium text-sm">
                      {ROLE_LABELS[user.role] || user.role}
                    </div>
                    <div className="text-xs opacity-70 mt-0.5">
                      {user.email}
                    </div>
                    <div className="text-xs opacity-50 mt-0.5">
                      {user.division || "Sin división"}
                    </div>
                  </button>
                );
              })}
            </div>
          </section>
        ))}
      </div>

      {/* Footer */}
      <div className="text-center pb-6 text-xs text-slate-600">
        Todas las contraseñas: admin123 — Solo para desarrollo
      </div>
    </div>
  );
}
