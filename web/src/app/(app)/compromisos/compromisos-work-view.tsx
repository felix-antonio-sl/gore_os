"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { ChevronDown, ChevronRight, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/empty-state";
import type { PaginatedResponse, CompromisoListItem } from "@/types";

interface IprGroup {
  ipr_id: string | null;
  codigo_bip: string | null;
  name: string | null;
  items: CompromisoListItem[];
  hasUrgent: boolean;
}

interface Props {
  onItemClick: (item: CompromisoListItem) => void;
  refreshKey: number;
  onRefresh: () => void;
}

const DONE = new Set(["VERIFICADO", "CANCELADO"]);

export function CompromisosWorkView({ onItemClick, refreshKey, onRefresh }: Props) {
  const [items, setItems] = useState<CompromisoListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  useEffect(() => {
    setLoading(true);
    api
      .get<PaginatedResponse<CompromisoListItem>>("/api/compromisos?page_size=100")
      .then((r) => setItems(r.items))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [refreshKey]);

  const active = items.filter((i) => !DONE.has(i.state));

  // Build groups
  const groupMap = new Map<string, IprGroup>();
  for (const item of active) {
    const key = item.ipr_id ?? "__general__";
    let g = groupMap.get(key);
    if (!g) {
      g = { ipr_id: item.ipr_id ?? null, codigo_bip: item.ipr_codigo_bip ?? null, name: item.ipr_name ?? null, items: [], hasUrgent: false };
      groupMap.set(key, g);
    }
    g.items.push(item);
    if (item.days_remaining != null && item.days_remaining <= 0) g.hasUrgent = true;
  }
  const groups = Array.from(groupMap.values()).sort((a, b) => {
    if (a.hasUrgent !== b.hasUrgent) return a.hasUrgent ? -1 : 1;
    return b.items.length - a.items.length;
  });

  // Auto-collapse non-urgent on data change
  useEffect(() => {
    const urgentKeys = new Set<string>();
    const allKeys = new Set<string>();
    for (const item of items) {
      if (DONE.has(item.state)) continue;
      const key = item.ipr_id ?? "__general__";
      allKeys.add(key);
      if (item.days_remaining != null && item.days_remaining <= 0) urgentKeys.add(key);
    }
    setCollapsed(new Set([...allKeys].filter((k) => !urgentKeys.has(k))));
  }, [items]);

  const toggle = (key: string) =>
    setCollapsed((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });

  const complete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setCompleting(id);
    try {
      await api.post(`/api/compromisos/${id}/completar`, {});
      onRefresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al completar");
    } finally {
      setCompleting(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-14 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  if (active.length === 0) {
    return <EmptyState title="Sin compromisos pendientes" description="No tienes compromisos activos asignados." />;
  }

  const overdue = active.filter((i) => i.days_remaining != null && i.days_remaining < 0).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 text-sm">
        <span className="font-medium tabular-nums">{active.length} pendientes</span>
        {overdue > 0 && <span className="text-red-600 font-medium tabular-nums">{overdue} vencidos</span>}
      </div>

      <div className="space-y-2">
        {groups.map((g) => {
          const key = g.ipr_id ?? "__general__";
          const isOpen = !collapsed.has(key);
          return (
            <div key={key} className="rounded-lg border bg-card overflow-hidden">
              <button
                onClick={() => toggle(key)}
                className="w-full flex items-center gap-2 px-4 py-3 hover:bg-muted/50 transition-colors text-left"
              >
                {isOpen ? (
                  <ChevronDown className="size-4 text-muted-foreground shrink-0" />
                ) : (
                  <ChevronRight className="size-4 text-muted-foreground shrink-0" />
                )}
                <span className="font-mono text-sm text-muted-foreground">{g.codigo_bip ?? "General"}</span>
                {g.name && (
                  <span className="text-sm truncate text-muted-foreground hidden sm:inline">— {g.name}</span>
                )}
                {g.hasUrgent && <span className="size-2 rounded-full bg-red-500 shrink-0" />}
                <span className="ml-auto text-xs text-muted-foreground tabular-nums shrink-0">
                  {g.items.length}
                </span>
              </button>
              {isOpen && (
                <div className="border-t divide-y">
                  {g.items.map((item) => {
                    const dr = item.days_remaining;
                    const isOverdue = dr != null && dr < 0;
                    const isToday = dr === 0;
                    const canAct = item.state === "PENDIENTE" || item.state === "EN_PROGRESO";
                    return (
                      <div
                        key={item.id}
                        onClick={() => onItemClick(item)}
                        className={cn(
                          "flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-colors",
                          isOverdue
                            ? "bg-red-50/50 hover:bg-red-50 dark:bg-red-950/20"
                            : isToday
                              ? "bg-amber-50/50 hover:bg-amber-50 dark:bg-amber-950/20"
                              : "hover:bg-muted/50"
                        )}
                      >
                        <span
                          className={cn(
                            "size-2 rounded-full shrink-0",
                            isOverdue
                              ? "bg-red-500"
                              : isToday
                                ? "bg-amber-500"
                                : dr != null && dr <= 7
                                  ? "bg-blue-400"
                                  : "bg-gray-300"
                          )}
                        />
                        <span className={cn("flex-1 text-sm truncate", isOverdue && "font-medium")}>
                          {item.description}
                        </span>
                        <StatusBadge status={item.state} size="sm" />
                        {dr != null && (
                          <span
                            className={cn(
                              "text-xs tabular-nums shrink-0 w-10 text-right",
                              isOverdue
                                ? "text-red-600 font-medium"
                                : isToday
                                  ? "text-amber-600"
                                  : "text-muted-foreground"
                            )}
                          >
                            {isToday ? "hoy" : `${dr}d`}
                          </span>
                        )}
                        {canAct && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 px-2 shrink-0"
                            onClick={(e) => complete(item.id, e)}
                            disabled={completing === item.id}
                          >
                            <Check className="size-3.5" />
                          </Button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
