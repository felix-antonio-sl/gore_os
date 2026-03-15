"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { ChevronDown, ChevronRight, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/empty-state";
import type { MiDivisionResponse, CompromisoListItem, PaginatedResponse } from "@/types";

interface Props {
  onItemClick: (item: CompromisoListItem) => void;
  refreshKey: number;
  onRefresh: () => void;
}

const DONE = new Set(["VERIFICADO", "CANCELADO"]);

export function CompromisosTeamView({ onItemClick, refreshKey, onRefresh }: Props) {
  const [data, setData] = useState<MiDivisionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedUser, setExpandedUser] = useState<string | null>(null);
  const [userItems, setUserItems] = useState<CompromisoListItem[]>([]);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [verifying, setVerifying] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .get<MiDivisionResponse>("/api/dashboard/mi-division")
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [refreshKey]);

  const fetchUserItems = async (userId: string) => {
    setItemsLoading(true);
    try {
      const r = await api.get<PaginatedResponse<CompromisoListItem>>(
        `/api/compromisos?responsible_id=${userId}&page_size=50`
      );
      setUserItems(r.items.filter((i) => !DONE.has(i.state)));
    } catch {
      setUserItems([]);
    } finally {
      setItemsLoading(false);
    }
  };

  const expand = (userId: string) => {
    if (expandedUser === userId) {
      setExpandedUser(null);
      return;
    }
    setExpandedUser(userId);
    fetchUserItems(userId);
  };

  const verify = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setVerifying(id);
    try {
      await api.post(`/api/compromisos/${id}/verificar`, {});
      onRefresh();
      if (expandedUser) fetchUserItems(expandedUser);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al verificar");
    } finally {
      setVerifying(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-12 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data || data.team.length === 0) {
    return <EmptyState title="Sin equipo" description="No hay compromisos activos en tu división." />;
  }

  const maxLoad = Math.max(...data.team.map((m) => m.total), 1);

  return (
    <div className="space-y-4">
      {/* KPIs */}
      {data.kpis.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {data.kpis.map((k) => (
            <div key={k.label} className="rounded-lg border bg-card px-4 py-3">
              <p
                className={cn(
                  "text-2xl font-bold tabular-nums",
                  k.color === "red" && "text-red-600",
                  k.color === "amber" && "text-amber-600",
                  k.color === "blue" && "text-blue-600",
                  k.color === "green" && "text-green-600"
                )}
              >
                {k.value}
              </p>
              <p className="text-xs text-muted-foreground">{k.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Team */}
      <div className="space-y-2">
        {data.team.map((m) => {
          const hasOverdue = m.vencidos > 0;
          const activos = m.pendientes + m.en_progreso;
          const loadPct = Math.round((m.total / maxLoad) * 100);
          const isExpanded = expandedUser === m.user_id;
          const initials = m.name
            .split(" ")
            .map((w) => w[0])
            .slice(0, 2)
            .join("")
            .toUpperCase();

          return (
            <div key={m.user_id} className="rounded-lg border bg-card overflow-hidden">
              <button
                onClick={() => expand(m.user_id)}
                className={cn(
                  "w-full flex items-center gap-3 px-4 py-3 transition-colors text-left",
                  hasOverdue
                    ? "bg-red-50/50 hover:bg-red-50 dark:bg-red-950/10"
                    : "hover:bg-muted/50"
                )}
              >
                {isExpanded ? (
                  <ChevronDown className="size-4 text-muted-foreground shrink-0" />
                ) : (
                  <ChevronRight className="size-4 text-muted-foreground shrink-0" />
                )}
                <div
                  className={cn(
                    "size-8 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0",
                    hasOverdue
                      ? "bg-red-200 text-red-700 dark:bg-red-900 dark:text-red-300"
                      : activos > 0
                        ? "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300"
                        : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                  )}
                >
                  {initials}
                </div>
                <span className="flex-1 text-sm font-medium truncate">{m.name}</span>
                <div className="flex items-center gap-2 shrink-0">
                  {hasOverdue && (
                    <span className="px-1.5 py-0.5 rounded bg-red-600 text-white text-[10px] font-bold tabular-nums">
                      {m.vencidos}
                    </span>
                  )}
                  {m.completados > 0 && (
                    <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 text-[10px] font-bold tabular-nums dark:bg-blue-900 dark:text-blue-300">
                      {m.completados} por verificar
                    </span>
                  )}
                  <span className="text-xs text-muted-foreground tabular-nums">
                    {activos} activos
                  </span>
                </div>
                <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden shrink-0">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all",
                      hasOverdue ? "bg-red-500" : loadPct > 70 ? "bg-amber-400" : "bg-green-400"
                    )}
                    style={{ width: `${loadPct}%` }}
                  />
                </div>
              </button>
              {isExpanded && (
                <div className="border-t">
                  {itemsLoading ? (
                    <div className="px-4 py-3 space-y-2">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="h-8 rounded bg-muted animate-pulse" />
                      ))}
                    </div>
                  ) : userItems.length === 0 ? (
                    <p className="px-4 py-3 text-sm text-muted-foreground">
                      Sin compromisos activos
                    </p>
                  ) : (
                    <div className="divide-y">
                      {userItems.map((item) => {
                        const dr = item.days_remaining;
                        const isOverdue = dr != null && dr < 0;
                        return (
                          <div
                            key={item.id}
                            onClick={() => onItemClick(item)}
                            className={cn(
                              "flex items-center gap-3 px-4 pl-16 py-2.5 cursor-pointer transition-colors",
                              isOverdue
                                ? "bg-red-50/30 hover:bg-red-50/60 dark:bg-red-950/10"
                                : "hover:bg-muted/30"
                            )}
                          >
                            <span
                              className={cn(
                                "size-1.5 rounded-full shrink-0",
                                isOverdue ? "bg-red-500" : dr === 0 ? "bg-amber-500" : "bg-gray-300"
                              )}
                            />
                            <span className="flex-1 text-sm truncate">{item.description}</span>
                            {item.ipr_codigo_bip && (
                              <span className="text-xs font-mono text-muted-foreground shrink-0">
                                {item.ipr_codigo_bip}
                              </span>
                            )}
                            <StatusBadge status={item.state} size="sm" />
                            {dr != null && (
                              <span
                                className={cn(
                                  "text-xs tabular-nums shrink-0",
                                  isOverdue ? "text-red-600 font-medium" : "text-muted-foreground"
                                )}
                              >
                                {dr === 0 ? "hoy" : `${dr}d`}
                              </span>
                            )}
                            {item.state === "COMPLETADO" && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2 shrink-0 text-green-600 hover:text-green-700 hover:bg-green-50"
                                onClick={(e) => verify(item.id, e)}
                                disabled={verifying === item.id}
                              >
                                <CheckCircle2 className="size-4" />
                              </Button>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
