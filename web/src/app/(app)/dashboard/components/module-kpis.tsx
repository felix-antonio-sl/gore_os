"use client";

import type { KPICardData } from "@/types";

const KPI_COLOR_MAP: Record<string, string> = {
  red: "border-l-red-500",
  orange: "border-l-orange-500",
  amber: "border-l-amber-500",
  green: "border-l-green-500",
  blue: "border-l-blue-500",
  gray: "border-l-slate-400",
};

interface ModuleKpisProps {
  kpis: KPICardData[];
  semaforo?: Array<{ dimension: string; label: string; signal: string }>;
}

export function ModuleKpis({ kpis, semaforo }: ModuleKpisProps) {
  if (kpis.length === 0 && (!semaforo || semaforo.length === 0)) return null;

  return (
    <div className="space-y-3 animate-in fade-in duration-200">
      {kpis.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {kpis.map((k) => (
            <div
              key={k.label}
              className={`rounded-lg border border-l-4 bg-card p-3 ${KPI_COLOR_MAP[k.color] ?? "border-l-slate-400"}`}
            >
              <p className="text-lg font-bold tabular-nums">{k.value.toLocaleString("es-CL")}</p>
              <p className="text-xs text-muted-foreground">{k.sublabel || k.label}</p>
            </div>
          ))}
        </div>
      )}
      {semaforo && semaforo.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {semaforo.map((s) => {
            const dotColor = s.signal === "VERDE" ? "bg-green-500" : s.signal === "AMARILLO" ? "bg-amber-500" : "bg-red-500";
            return (
              <div key={s.dimension} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className={`size-2 rounded-full ${dotColor}`} />
                {s.label}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
