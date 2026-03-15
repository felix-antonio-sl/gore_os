"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { MisCompromisosResponse } from "@/types";

export function ModuleMyProgress() {
  const router = useRouter();
  const [data, setData] = useState<MisCompromisosResponse | null>(null);

  useEffect(() => {
    api.get<MisCompromisosResponse>("/api/dashboard/mis-compromisos")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-4 w-24 bg-muted animate-pulse rounded mb-3" />
        <div className="h-1.5 w-full bg-muted animate-pulse rounded-full mb-3" />
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-8 bg-muted animate-pulse rounded" />
          ))}
        </div>
      </div>
    );
  }

  const total = data.kpis.reduce((sum, k) => sum + k.value, 0);
  const completados = data.kpis.find(k => k.label.toLowerCase().includes("completad"))?.value ?? 0;
  const pct = total > 0 ? Math.round((completados / total) * 100) : 0;

  const allItems = data.groups.flatMap(g => g.items);
  const maxVisible = 6;
  const visible = allItems.slice(0, maxVisible);
  const remaining = allItems.length - maxVisible;

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">Mi Trabajo</h3>
        <span className="text-xs text-muted-foreground tabular-nums">{completados}/{total}</span>
      </div>

      <div className="h-1.5 rounded-full bg-muted mb-3">
        <div
          className="h-full rounded-full bg-green-500 transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>

      {visible.length > 0 ? (
        <div className="space-y-1">
          {visible.map((item) => {
            const dr = item.days_remaining ?? 999;
            const isOverdue = dr < 0;
            const isToday = dr === 0;
            const isUrgent = dr > 0 && dr <= 7;

            return (
              <div
                key={item.id}
                onClick={() => {
                  if (item.ipr_id) router.push(`/ipr/${item.ipr_id}?tab=compromisos`);
                  else router.push("/compromisos");
                }}
                className={cn(
                  "flex items-center gap-2 px-2 py-1.5 rounded-md text-xs cursor-pointer transition-colors",
                  isOverdue && "bg-red-50 hover:bg-red-100 dark:bg-red-950/30 dark:hover:bg-red-950/50",
                  isToday && "bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/30",
                  isUrgent && "hover:bg-amber-50 dark:hover:bg-amber-950/20",
                  !isOverdue && !isToday && !isUrgent && "hover:bg-muted/50"
                )}
              >
                <span className={cn(
                  "size-1.5 rounded-full shrink-0",
                  isOverdue ? "bg-red-500" : isToday ? "bg-amber-500" : isUrgent ? "bg-blue-400" : "bg-gray-300"
                )} />
                <span className={cn(
                  "flex-1 truncate",
                  isOverdue ? "font-medium text-foreground" : "text-muted-foreground"
                )}>
                  {item.description}
                </span>
                <span className={cn(
                  "tabular-nums shrink-0 font-medium",
                  isOverdue ? "text-red-600" : isToday ? "text-amber-600" : isUrgent ? "text-blue-600" : "text-muted-foreground"
                )}>
                  {isOverdue ? `${dr}d` : isToday ? "hoy" : `${dr}d`}
                </span>
              </div>
            );
          })}
          {remaining > 0 && (
            <button
              onClick={() => router.push("/compromisos")}
              className="w-full text-xs text-muted-foreground hover:text-foreground py-1 text-center"
            >
              +{remaining} más
            </button>
          )}
        </div>
      ) : (
        <p className="text-xs text-muted-foreground py-2">Sin compromisos pendientes.</p>
      )}
    </div>
  );
}
