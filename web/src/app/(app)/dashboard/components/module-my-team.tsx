"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { Badge } from "@/components/ui/badge";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { MiDivisionResponse, CompromisoListItem, TeamMemberLoad } from "@/types";

const INITIAL_SHOW = 5;
const VENCIDOS_SHOW = 5;

type TeamSort = "vencidos" | "total" | "name";

function sortTeam(team: TeamMemberLoad[], sort: TeamSort): TeamMemberLoad[] {
  return [...team].sort((a, b) => {
    if (sort === "vencidos") return b.vencidos - a.vencidos;
    if (sort === "total") return b.total - a.total;
    return a.name.localeCompare(b.name);
  });
}

export function ModuleMyTeam() {
  const router = useRouter();
  const [data, setData] = useState<MiDivisionResponse | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [teamSort, setTeamSort] = useState<TeamSort>("vencidos");
  const [showAllVencidos, setShowAllVencidos] = useState(false);

  useEffect(() => {
    api.get<MiDivisionResponse>("/api/dashboard/mi-division")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-4 w-20 bg-muted animate-pulse rounded mb-3" />
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-10 w-full bg-muted animate-pulse rounded mb-2" />
        ))}
      </div>
    );
  }

  const maxLoad = Math.max(...data.team.map(m => m.total), 1);
  const sorted = sortTeam(data.team, teamSort);
  const visibleTeam = expanded ? sorted : sorted.slice(0, INITIAL_SHOW);
  const hasMore = data.team.length > INITIAL_SHOW;

  const vencidos = data.commitments ?? [];
  const visibleVencidos = showAllVencidos ? vencidos : vencidos.slice(0, VENCIDOS_SHOW);

  return (
    <div className="space-y-4 animate-in fade-in duration-200">
      {/* ── Team workload ────────────────────────────────── */}
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold">Carga por Persona</h3>
          <div className="flex items-center gap-2">
            <div className="flex gap-0.5">
              {(["vencidos", "total", "name"] as const).map((key) => (
                <button
                  key={key}
                  className={cn(
                    "px-2 py-0.5 rounded text-[10px] font-medium transition-colors",
                    teamSort === key
                      ? "bg-foreground text-background"
                      : "text-muted-foreground hover:bg-muted"
                  )}
                  onClick={() => setTeamSort(key)}
                >
                  {key === "vencidos" ? "Vencidos" : key === "total" ? "Total" : "Nombre"}
                </button>
              ))}
            </div>
            <button
              onClick={() => router.push("/compromisos")}
              className="text-xs text-indigo-600 hover:underline dark:text-indigo-400"
            >
              Ver todos
            </button>
          </div>
        </div>
        <div className="space-y-1.5">
          {visibleTeam.map((m) => {
            const hasOverdue = m.vencidos > 0;
            const activos = m.pendientes + m.en_progreso;
            const loadPct = Math.round((m.total / maxLoad) * 100);
            const initials = m.name
              .split(" ")
              .map(w => w[0])
              .slice(0, 2)
              .join("")
              .toUpperCase();

            return (
              <div
                key={m.user_id}
                onClick={() => router.push(`/compromisos?responsible_id=${m.user_id}`)}
                className={cn(
                  "flex items-center gap-2.5 p-2 rounded-md cursor-pointer transition-colors text-xs",
                  hasOverdue
                    ? "bg-red-50 hover:bg-red-100 dark:bg-red-950/20 dark:hover:bg-red-950/40"
                    : "hover:bg-muted/50"
                )}
              >
                <div className={cn(
                  "size-7 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0",
                  hasOverdue
                    ? "bg-red-200 text-red-700 dark:bg-red-900 dark:text-red-300"
                    : activos > 0
                      ? "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300"
                      : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                )}>
                  {initials}
                </div>

                <span className="flex-1 truncate font-medium">{m.name}</span>

                <div className="flex items-center gap-2 shrink-0">
                  {hasOverdue && (
                    <span className="px-1.5 py-0.5 rounded bg-red-600 text-white text-[10px] font-bold">
                      {m.vencidos}
                    </span>
                  )}
                  <span className="text-muted-foreground">{activos} activos</span>
                  <div className="hidden sm:flex items-center gap-1.5">
                    <Badge variant="outline" className="text-[10px] h-4 px-1">
                      {m.pendientes} pend.
                    </Badge>
                    <Badge variant="secondary" className="text-[10px] h-4 px-1">
                      {m.en_progreso} prog.
                    </Badge>
                    <Badge className="text-[10px] h-4 px-1 bg-green-100 text-green-800 hover:bg-green-100">
                      {m.completados} comp.
                    </Badge>
                  </div>
                </div>

                <div className="w-14 h-1.5 rounded-full bg-muted overflow-hidden shrink-0">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all",
                      hasOverdue ? "bg-red-500" : loadPct > 70 ? "bg-amber-400" : "bg-green-400"
                    )}
                    style={{ width: `${loadPct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
        {hasMore && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center justify-center gap-1 w-full mt-2 text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
          >
            {expanded ? (
              <>Mostrar menos <ChevronUp className="size-3" /></>
            ) : (
              <>+{data.team.length - INITIAL_SHOW} más <ChevronDown className="size-3" /></>
            )}
          </button>
        )}
      </div>

      {/* ── Overdue commitments ──────────────────────────── */}
      {vencidos.length > 0 && (
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">
              Compromisos Vencidos
              <Badge variant="destructive" className="ml-2 text-[10px]">
                {vencidos.length}
              </Badge>
            </h3>
            <button
              onClick={() => router.push("/compromisos?state=PENDIENTE")}
              className="text-xs text-indigo-600 hover:underline dark:text-indigo-400"
            >
              Gestionar
            </button>
          </div>
          <div className="divide-y">
            {visibleVencidos.map((c: CompromisoListItem) => (
              <div
                key={c.id}
                onClick={() => c.ipr_id ? router.push(`/ipr/${c.ipr_id}?tab=compromisos`) : undefined}
                className="flex items-center gap-3 py-2 text-xs cursor-pointer hover:bg-muted/50 rounded px-1 transition-colors"
              >
                <TemporalIndicator daysRemaining={c.days_remaining} state={c.state} />
                <span className="flex-1 truncate font-medium">{c.description}</span>
                <span className="text-muted-foreground truncate max-w-[120px] hidden sm:inline">
                  {c.responsible_name}
                </span>
                <StatusBadge status={c.state} size="sm" />
              </div>
            ))}
          </div>
          {vencidos.length > VENCIDOS_SHOW && (
            <button
              onClick={() => setShowAllVencidos(!showAllVencidos)}
              className="flex items-center justify-center gap-1 w-full mt-2 text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
            >
              {showAllVencidos ? (
                <>Mostrar menos <ChevronUp className="size-3" /></>
              ) : (
                <>+{vencidos.length - VENCIDOS_SHOW} más <ChevronDown className="size-3" /></>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
