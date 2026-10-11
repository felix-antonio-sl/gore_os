"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ModuleFormulacion } from "./module-formulacion";
import { ModuleMyTeam } from "./module-my-team";
import { ModuleKpis } from "./module-kpis";
import { ModuleJuridico } from "./module-juridico";
import type { RoleCode, KPICardData, DashboardExecutivoResponse, DivisionBreakdown } from "@/types";

// Role → module mapping
const KPI_ROLES: RoleCode[] = ["ANALISTA", "RTF", "ASESOR_JURIDICO"];
const TEAM_ROLES: RoleCode[] = ["JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"];
const PANORAMA_ROLES: RoleCode[] = [
  "ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA", "SECRETARIO_EJECUTIVO", "CONSEJERO_REGIONAL",
];

export function OperationalOverview() {
  const { user } = useAuth();
  const [kpis, setKpis] = useState<KPICardData[]>([]);
  const [semaforo, setSemaforo] = useState<Array<{ dimension: string; label: string; signal: string }>>([]);
  const [divisions, setDivisions] = useState<DivisionBreakdown[]>([]);
  const [loading, setLoading] = useState(true);

  const role = user?.role_code;

  // Fetch KPIs + semáforo for Panorama roles
  useEffect(() => {
    if (!role) return;
    if (PANORAMA_ROLES.includes(role)) {
      api.get<DashboardExecutivoResponse>("/api/dashboard/ejecutivo")
        .then((d) => {
          setKpis(d.kpis);
          setSemaforo(d.semaforo ?? []);
          setDivisions(d.divisions ?? []);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    } else if (TEAM_ROLES.includes(role)) {
      api.get<{ kpis: KPICardData[] }>("/api/dashboard/mi-division")
        .then((d) => setKpis(d.kpis))
        .catch(() => {})
        .finally(() => setLoading(false));
    } else if (KPI_ROLES.includes(role)) {
      api.get<{ kpis: KPICardData[] }>("/api/dashboard/mis-compromisos")
        .then((d) => setKpis(d.kpis))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [role]);

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-64 bg-muted animate-pulse rounded" />
        <div className="h-4 w-48 bg-muted animate-pulse rounded" />
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-28 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
        <div className="h-32 bg-muted animate-pulse rounded-lg" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-bold">Panorama de gestión</h1>
        <p className="text-sm text-muted-foreground">{user?.role_label} · Contexto y herramientas de tu función</p>
      </div>

      {role === "ANALISTA" && <ModuleFormulacion />}
      {role && TEAM_ROLES.includes(role) && <ModuleMyTeam />}
      {role === "ASESOR_JURIDICO" && <ModuleJuridico />}

      {/* 4. Compact KPIs + semáforo */}
      <ModuleKpis kpis={kpis} semaforo={semaforo} divisions={divisions} />
    </div>
  );
}
