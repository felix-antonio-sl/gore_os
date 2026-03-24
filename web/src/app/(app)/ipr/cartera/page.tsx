"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { DivisionCarteraItem } from "@/types";

const SIGNAL_COLORS = {
  VERDE: "bg-green-500",
  AMARILLO: "bg-amber-500",
  ROJO: "bg-red-500",
} as const;

const PHASE_COLORS: Record<string, string> = {
  F0: "bg-slate-300",
  F1: "bg-blue-400",
  F2: "bg-cyan-400",
  F3: "bg-purple-400",
  F4: "bg-green-400",
  F5: "bg-gray-400",
};

export default function CarteraDivisionPage() {
  const router = useRouter();
  const [data, setData] = useState<DivisionCarteraItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<DivisionCarteraItem[]>("/api/ipr/cartera-por-division")
      .then(setData)
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-48 rounded bg-muted animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-40 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Cartera IPR por Division"
        description="Vista comparativa del portafolio de inversiones por division"
        accentColor="indigo"
      />

      {data.length === 0 ? (
        <EmptyState title="Sin datos de cartera" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.map((d) => (
            <button
              key={d.division_id}
              onClick={() => router.push(`/ipr?division=${d.division_id}`)}
              className="rounded-xl border bg-card p-4 text-left hover:border-primary/40 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-sm">{d.abbreviation || d.division_name}</h3>
                  {d.abbreviation && (
                    <p className="text-[10px] text-muted-foreground">{d.division_name}</p>
                  )}
                </div>
                <div className="flex items-center gap-1.5">
                  <span className={cn("size-3 rounded-full", SIGNAL_COLORS[d.health_signal])} />
                  <span className="text-xs font-medium tabular-nums">{d.total_iprs}</span>
                </div>
              </div>

              {/* Phase distribution bar */}
              <div className="flex h-2 rounded-full overflow-hidden mb-3">
                {Object.entries(d.by_phase).map(([phase, count]) =>
                  count > 0 ? (
                    <div
                      key={phase}
                      className={cn("h-full", PHASE_COLORS[phase])}
                      style={{ width: `${(count / d.total_iprs) * 100}%` }}
                      title={`${phase}: ${count}`}
                    />
                  ) : null
                )}
              </div>

              {/* KPIs */}
              <div className="flex gap-3 text-xs">
                {d.critical_alerts > 0 && (
                  <Badge variant="outline" className="text-red-600 border-red-200 text-[10px]">
                    {d.critical_alerts} criticas
                  </Badge>
                )}
                {d.open_problems > 0 && (
                  <Badge variant="outline" className="text-amber-600 border-amber-200 text-[10px]">
                    {d.open_problems} problemas
                  </Badge>
                )}
                {d.overdue_commitments > 0 && (
                  <Badge variant="outline" className="text-orange-600 border-orange-200 text-[10px]">
                    {d.overdue_commitments} vencidos
                  </Badge>
                )}
              </div>

              {/* Health reasons */}
              <p className="text-[10px] text-muted-foreground mt-2 line-clamp-1">
                {d.health_reasons[0]}
              </p>
            </button>
          ))}
        </div>
      )}

      {/* Phase legend */}
      <div className="flex gap-3 text-[10px] text-muted-foreground pt-2">
        {Object.entries(PHASE_COLORS).map(([phase, color]) => (
          <div key={phase} className="flex items-center gap-1">
            <span className={cn("size-2 rounded-full", color)} />
            {phase}
          </div>
        ))}
      </div>
    </div>
  );
}
