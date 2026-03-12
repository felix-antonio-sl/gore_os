"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface DgiTeamData {
  team_status?: Array<{ name: string; role: string; activity: string }>;
}

export function ModuleDgiTeam() {
  const [data, setData] = useState<DgiTeamData | null>(null);

  useEffect(() => {
    api.get<DgiTeamData>("/api/dgi/cockpit")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data?.team_status) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-4 w-24 bg-muted animate-pulse rounded mb-3" />
        <div className="h-16 bg-muted animate-pulse rounded" />
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <h3 className="text-sm font-semibold mb-3">Equipo DGI</h3>
      <div className="grid gap-2">
        {data.team_status.map((m) => (
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
