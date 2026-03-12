"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { MiDivisionResponse } from "@/types";

export function ModuleMyTeam() {
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
          <div key={i} className="h-5 w-full bg-muted animate-pulse rounded mb-2" />
        ))}
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <h3 className="text-sm font-semibold mb-3">Mi Equipo</h3>
      <div className="grid gap-2">
        {data.team.slice(0, 5).map((m) => (
          <div key={m.user_id} className="flex items-center justify-between text-sm">
            <span className="truncate max-w-[180px]">{m.name}</span>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              {m.vencidos > 0 && (
                <span className="text-red-600 font-medium">{m.vencidos} vencidos</span>
              )}
              <span>{m.pendientes + m.en_progreso} activos</span>
            </div>
          </div>
        ))}
      </div>
      {data.team.length > 5 && (
        <p className="text-xs text-muted-foreground mt-2">+{data.team.length - 5} más</p>
      )}
    </div>
  );
}
