"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { PageGuard } from "@/components/page-guard";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SlaItem {
  name: string;
  sla_days: number | null;
  active: number | null;
  breached: number;
  compliance_pct: number;
  signal: "VERDE" | "AMARILLO" | "ROJO";
}

interface SlaDashboard {
  total_monitored: number;
  total_green: number;
  total_red: number;
  slas: SlaItem[];
}

const SIGNAL_STYLES: Record<string, string> = {
  VERDE: "bg-green-100 text-green-800 border-green-200",
  AMARILLO: "bg-amber-100 text-amber-800 border-amber-200",
  ROJO: "bg-red-100 text-red-800 border-red-200",
};

const SIGNAL_DOT: Record<string, string> = {
  VERDE: "bg-green-500",
  AMARILLO: "bg-amber-500",
  ROJO: "bg-red-500",
};

export default function SlasPage() {
  const [data, setData] = useState<SlaDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<SlaDashboard>("/api/admin/slas/dashboard")
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageGuard allowedRoles={["ADMIN_SISTEMA"]}>
      <div className="p-6 space-y-6">
        <PageHeader
          title="Monitoreo SLA"
          description="12 acuerdos de nivel de servicio monitoreados"
          accentColor="rose"
        />

        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
            ))}
          </div>
        ) : data ? (
          <>
            {/* Summary strip */}
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-lg border bg-card p-3">
                <p className="text-xs text-muted-foreground">SLAs monitoreados</p>
                <p className="text-2xl font-semibold tabular-nums">{data.total_monitored}</p>
              </div>
              <div className="rounded-lg border bg-card p-3">
                <p className="text-xs text-muted-foreground">En cumplimiento</p>
                <p className="text-2xl font-semibold tabular-nums text-green-600">{data.total_green}</p>
              </div>
              <div className="rounded-lg border bg-card p-3">
                <p className="text-xs text-muted-foreground">En incumplimiento</p>
                <p className={cn("text-2xl font-semibold tabular-nums", data.total_red > 0 ? "text-red-600" : "")}>
                  {data.total_red}
                </p>
              </div>
            </div>

            {/* SLA table */}
            <div className="rounded-lg border overflow-hidden">
              <div className="grid grid-cols-[1fr_80px_80px_80px_100px_60px] gap-2 px-4 py-2 bg-muted/40 text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                <span>SLA</span>
                <span className="text-right">Plazo</span>
                <span className="text-right">Activos</span>
                <span className="text-right">Vencidos</span>
                <span className="text-right">Cumplimiento</span>
                <span className="text-center">Estado</span>
              </div>
              <div className="divide-y">
                {data.slas.map((sla, i) => (
                  <div
                    key={i}
                    className="grid grid-cols-[1fr_80px_80px_80px_100px_60px] gap-2 px-4 py-3 items-center"
                  >
                    <span className="text-sm font-medium">{sla.name}</span>
                    <span className="text-xs text-muted-foreground text-right tabular-nums">
                      {sla.sla_days ? `${sla.sla_days}d` : "—"}
                    </span>
                    <span className="text-xs text-right tabular-nums">
                      {sla.active !== null ? sla.active : "—"}
                    </span>
                    <span className={cn(
                      "text-xs text-right tabular-nums font-medium",
                      sla.breached > 0 ? "text-red-600" : ""
                    )}>
                      {sla.breached}
                    </span>
                    <div className="flex items-center justify-end gap-1.5">
                      <div className="h-1.5 w-16 rounded-full bg-muted overflow-hidden">
                        <div
                          className={cn(
                            "h-full rounded-full",
                            sla.signal === "VERDE" ? "bg-green-500" :
                            sla.signal === "AMARILLO" ? "bg-amber-500" : "bg-red-500"
                          )}
                          style={{ width: `${Math.min(sla.compliance_pct, 100)}%` }}
                        />
                      </div>
                      <span className="text-[10px] tabular-nums w-8 text-right">
                        {sla.compliance_pct}%
                      </span>
                    </div>
                    <div className="flex justify-center">
                      <div className={cn("size-2.5 rounded-full", SIGNAL_DOT[sla.signal])} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">No se pudieron cargar los SLAs.</p>
        )}
      </div>
    </PageGuard>
  );
}
