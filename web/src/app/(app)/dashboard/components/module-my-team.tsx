"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { MiDivisionResponse } from "@/types";

export function ModuleMyTeam() {
  const router = useRouter();
  const [data, setData] = useState<MiDivisionResponse | null>(null);

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

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Mi Equipo</h3>
        <button
          onClick={() => router.push("/compromisos")}
          className="text-xs text-indigo-600 hover:underline dark:text-indigo-400"
        >
          Ver todos
        </button>
      </div>
      <div className="space-y-1.5">
        {data.team.slice(0, 5).map((m) => {
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
      {data.team.length > 5 && (
        <p className="text-xs text-muted-foreground mt-2 text-center">
          +{data.team.length - 5} más
        </p>
      )}
    </div>
  );
}
