"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface DgiTeamData {
  team_status?: Array<{ name: string; role: string; activity: string }>;
}

export function ModuleDgiTeam() {
  const [data, setData] = useState<DgiTeamData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<DgiTeamData>("/api/dgi/cockpit")
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  // Real loading — skeleton only while the request is in flight.
  if (loading) {
    return (
      <div className="rounded-lg border bg-card p-4" aria-busy="true">
        <div className="h-4 w-24 bg-muted animate-pulse rounded mb-3" />
        <div className="h-16 bg-muted animate-pulse rounded" />
      </div>
    );
  }

  const team = data?.team_status ?? [];

  // Resolved but no team data — an honest empty state, not an eternal skeleton.
  if (team.length === 0) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <h3 className="text-sm font-semibold mb-1">Equipo DGI</h3>
        <p className="text-sm text-muted-foreground">Sin actividad del equipo por ahora.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <h3 className="text-sm font-semibold mb-3">Equipo DGI</h3>
      <div className="grid gap-2">
        {team.map((m) => (
          <div key={m.name} className="flex items-center justify-between text-sm">
            <span className="truncate max-w-[180px]">{m.name}</span>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="text-muted-foreground">{m.role}</span>
              <span>{m.activity}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
