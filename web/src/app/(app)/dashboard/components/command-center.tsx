"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDateLong } from "@/lib/format";
import { AttentionStrip } from "./attention-strip";
import { ModuleMyProgress } from "./module-my-progress";
import { ModuleMyTeam } from "./module-my-team";
import { ModuleDgiTeam } from "./module-dgi-team";
import { ModuleKpis } from "./module-kpis";
import { ModuleJuridico } from "./module-juridico";
import type { ActionItemsResponse, RoleCode, KPICardData, DashboardExecutivoResponse, DivisionBreakdown } from "@/types";

// Role → module mapping
const PROGRESS_ROLES: RoleCode[] = ["ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO"];
const TEAM_ROLES: RoleCode[] = ["JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"];
const DGI_TEAM_ROLES: RoleCode[] = ["JEFE_DGI"];
const INDICATOR_ROLES: RoleCode[] = ["ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD"];
const PANORAMA_ROLES: RoleCode[] = [
  "ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA", "SECRETARIO_EJECUTIVO", "CONSEJERO_REGIONAL",
];

export function CommandCenter() {
  const { user } = useAuth();
  const [actionData, setActionData] = useState<ActionItemsResponse | null>(null);
  const [kpis, setKpis] = useState<KPICardData[]>([]);
  const [semaforo, setSemaforo] = useState<Array<{ dimension: string; label: string; signal: string }>>([]);
  const [divisions, setDivisions] = useState<DivisionBreakdown[]>([]);
  const [loading, setLoading] = useState(true);

  const role = user?.role_code;

  useEffect(() => {
    // Fetch action items (universal)
    api.get<ActionItemsResponse>("/api/dashboard/action-items")
      .then(setActionData)
      .catch(() => setActionData(null))
      .finally(() => setLoading(false));
  }, []);

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
        .catch(() => {});
    } else if (TEAM_ROLES.includes(role)) {
      api.get<{ kpis: KPICardData[] }>("/api/dashboard/mi-division")
        .then((d) => setKpis(d.kpis))
        .catch(() => {});
    } else if (PROGRESS_ROLES.includes(role)) {
      api.get<{ kpis: KPICardData[] }>("/api/dashboard/mis-compromisos")
        .then((d) => setKpis(d.kpis))
        .catch(() => {});
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
      {/* 1. Contextual greeting */}
      <div>
        <h1 className="text-2xl font-bold">
          Buenos días, {actionData?.greeting_name ?? "usuario"}
        </h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          {formatDateLong(new Date().toISOString())} — {actionData?.summary ?? "Cargando..."}
        </p>
      </div>

      {/* 2. Attention strip */}
      {actionData && <AttentionStrip items={actionData.items} />}

      {/* 3. Conditional module */}
      {role && PROGRESS_ROLES.includes(role) && <ModuleMyProgress />}
      {role && TEAM_ROLES.includes(role) && <ModuleMyTeam />}
      {role && DGI_TEAM_ROLES.includes(role) && <ModuleDgiTeam />}
      {role === "ASESOR_JURIDICO" && <ModuleJuridico />}
      {/* INDICATOR_ROLES and PANORAMA_ROLES get KPIs below — no separate module */}

      {/* 4. Compact KPIs + semáforo */}
      <ModuleKpis kpis={kpis} semaforo={semaforo} divisions={divisions} />
    </div>
  );
}
