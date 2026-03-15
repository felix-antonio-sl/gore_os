"use client";

import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import type { KPICardData, DivisionBreakdown } from "@/types";

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
  divisions?: DivisionBreakdown[];
}

export function ModuleKpis({ kpis, semaforo, divisions }: ModuleKpisProps) {
  const router = useRouter();

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

      {/* Division breakdown for executives */}
      {divisions && divisions.length > 0 && (
        <div className="border-t pt-2 mt-1">
          <div className="flex items-center justify-between mb-1.5">
            <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Por división</p>
            <button
              onClick={() => router.push("/ipr/cartera")}
              className="text-[10px] text-indigo-600 hover:underline dark:text-indigo-400"
            >
              Cartera Divisional
            </button>
          </div>
          <div className="space-y-0.5">
            {divisions.slice(0, 6).map((d) => {
              const hasIssues = d.vencidos > 0;
              return (
                <div
                  key={d.division_name}
                  onClick={() => router.push(`/ipr?division=${encodeURIComponent(d.division_name)}`)}
                  className="flex items-center gap-2 text-xs cursor-pointer hover:bg-muted/50 rounded px-1 py-1"
                >
                  <span className={cn(
                    "size-1.5 rounded-full",
                    hasIssues ? "bg-red-500" : d.problemas_abiertos > 3 ? "bg-amber-500" : "bg-green-500"
                  )} />
                  <span className="flex-1 truncate">{d.division_name}</span>
                  {d.vencidos > 0 && (
                    <span className="text-red-600 font-medium tabular-nums">{d.vencidos} vencidos</span>
                  )}
                  <span className="text-muted-foreground tabular-nums">{d.total_compromisos} comp.</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
