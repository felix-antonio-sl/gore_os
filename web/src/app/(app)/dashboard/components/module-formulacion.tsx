"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { MisFormulacionesResponse, FormulacionIPR } from "@/types";

const PHASE_LABELS: Record<string, string> = {
  F0: "Formulación",
  F1: "Admisibilidad",
  F2: "Evaluación",
};

const PHASE_COLORS: Record<string, string> = {
  F0: "bg-slate-100 text-slate-700",
  F1: "bg-blue-100 text-blue-700",
  F2: "bg-cyan-100 text-cyan-700",
};

function SatCheck({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span className="inline-flex items-center gap-1 text-[11px]">
      {ok ? (
        <CheckCircle2 className="size-3 text-green-600 shrink-0" />
      ) : (
        <Circle className="size-3 text-muted-foreground shrink-0" />
      )}
      <span className={ok ? "text-foreground" : "text-muted-foreground"}>{label}</span>
    </span>
  );
}

function FormulacionCard({ ipr }: { ipr: FormulacionIPR }) {
  const router = useRouter();
  const daysColor =
    ipr.days_in_phase <= 30 ? "text-green-600" :
    ipr.days_in_phase <= 90 ? "text-amber-600" : "text-red-600";

  return (
    <div
      onClick={() => router.push(`/ipr/${ipr.id}?tab=${ipr.suggested_tab}`)}
      className="rounded-lg border bg-card p-3 cursor-pointer hover:bg-accent/50 transition-colors"
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2 min-w-0">
          <span className="font-mono text-xs text-muted-foreground">{ipr.codigo_bip}</span>
          <span className="text-xs font-medium truncate">{ipr.name}</span>
        </div>
        <span className={cn("text-[10px] tabular-nums shrink-0", daysColor)}>
          {ipr.days_in_phase}d
        </span>
      </div>

      {ipr.phase === "F0" && (
        <div className="flex flex-wrap gap-x-3 gap-y-0.5 mb-1.5">
          <SatCheck ok={ipr.has_mechanism} label="Mecanismo" />
          <SatCheck ok={ipr.partes_count > 0} label={`Partes (${ipr.partes_count})`} />
          <SatCheck ok={ipr.territorio_count > 0} label={`Territorio (${ipr.territorio_count})`} />
          <SatCheck ok={ipr.hitos_count > 0} label={`Hitos (${ipr.hitos_count})`} />
        </div>
      )}
      {ipr.phase === "F1" && ipr.admisibilidad_total > 0 && (
        <div className="mb-1.5">
          <div className="flex items-center gap-2 text-[11px]">
            <span className="text-muted-foreground">Admisibilidad:</span>
            <span className={cn(
              "font-medium tabular-nums",
              ipr.admisibilidad_verified === ipr.admisibilidad_total ? "text-green-600" : "text-amber-600"
            )}>
              {ipr.admisibilidad_verified}/{ipr.admisibilidad_total}
            </span>
          </div>
        </div>
      )}
      {ipr.phase === "F2" && (
        <div className="flex items-center gap-2 text-[11px] mb-1.5">
          <SatCheck ok={ipr.eval_assigned} label="Evaluación asignada" />
          {ipr.eval_result && <SatCheck ok={true} label={ipr.eval_result} />}
        </div>
      )}

      <div className="flex items-center gap-1.5 text-[11px] text-indigo-600 dark:text-indigo-400">
        <ArrowRight className="size-3 shrink-0" />
        <span>{ipr.suggested_action}</span>
      </div>
    </div>
  );
}

export function ModuleFormulacion() {
  const [data, setData] = useState<MisFormulacionesResponse | null>(null);

  useEffect(() => {
    api.get<MisFormulacionesResponse>("/api/ipr/mis-formulaciones")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-4 w-40 bg-muted animate-pulse rounded mb-3" />
        <div className="space-y-2">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-20 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (data.total === 0) {
    return (
      <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
        <h3 className="text-sm font-semibold mb-2">Mis IPRs en Formulación</h3>
        <p className="text-xs text-muted-foreground">Sin IPRs asignadas en formulación.</p>
      </div>
    );
  }

  const phases = ["F0", "F1", "F2"].filter(p => (data.by_phase[p]?.length ?? 0) > 0);

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Mis IPRs en Formulación</h3>
        <span className="text-xs text-muted-foreground tabular-nums">{data.total} activas</span>
      </div>

      <div className="space-y-3">
        {phases.map((phase) => (
          <div key={phase}>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge className={cn("text-[10px] px-1.5 py-0 border-0", PHASE_COLORS[phase])}>
                {phase}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {PHASE_LABELS[phase]}
              </span>
              <span className="text-[10px] text-muted-foreground tabular-nums">
                ({data.by_phase[phase].length})
              </span>
            </div>
            <div className="space-y-1.5">
              {data.by_phase[phase].map((ipr) => (
                <FormulacionCard key={ipr.id} ipr={ipr} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
