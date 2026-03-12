"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { MisCompromisosResponse } from "@/types";

export function ModuleMyProgress() {
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
        <div className="h-2.5 w-full bg-muted animate-pulse rounded-full mb-2" />
        <div className="flex gap-4">
          <div className="h-3 w-16 bg-muted animate-pulse rounded" />
          <div className="h-3 w-16 bg-muted animate-pulse rounded" />
        </div>
      </div>
    );
  }

  const total = data.kpis.reduce((sum, k) => sum + k.value, 0);
  const completados = data.kpis.find(k => k.label.toLowerCase().includes("completad"))?.value ?? 0;
  const pct = total > 0 ? Math.round((completados / total) * 100) : 0;

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <h3 className="text-sm font-semibold mb-3">Mi Progreso</h3>
      <div className="flex items-center gap-3 mb-2">
        <div className="flex-1">
          <div className="h-2.5 w-full rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-gradient-to-r from-green-500 to-amber-500 transition-all duration-500"
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
        <span className="text-sm font-bold tabular-nums">{pct}%</span>
      </div>
      <div className="flex gap-4 text-xs text-muted-foreground">
        {data.kpis.map((k) => (
          <span key={k.label}>
            <span className="font-semibold text-foreground">{k.value}</span> {k.sublabel || k.label}
          </span>
        ))}
      </div>
    </div>
  );
}
