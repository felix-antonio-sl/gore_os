"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Building2, Clock, Shield, Target, FileCheck, CheckCircle2, XCircle } from "lucide-react";
import type { TrackInfo, TransitionReadiness } from "@/types";

const mechanismBorderColors: Record<string, string> = {
  SNI: "border-l-indigo-500",
  C33: "border-l-violet-500",
  FRIL: "border-l-emerald-500",
  GLOSA06: "border-l-sky-500",
  TRANSFER: "border-l-amber-500",
  SUBV8: "border-l-rose-500",
  FRPD: "border-l-teal-500",
};

const mechanismBgColors: Record<string, string> = {
  SNI: "bg-indigo-100 text-indigo-800",
  C33: "bg-violet-100 text-violet-800",
  FRIL: "bg-emerald-100 text-emerald-800",
  GLOSA06: "bg-sky-100 text-sky-800",
  TRANSFER: "bg-amber-100 text-amber-800",
  SUBV8: "bg-rose-100 text-rose-800",
  FRPD: "bg-teal-100 text-teal-800",
};

const productColors: Record<string, string> = {
  RS: "bg-green-100 text-green-800",
  RF: "bg-blue-100 text-blue-800",
  ITF: "bg-amber-100 text-amber-800",
  FI: "bg-orange-100 text-orange-800",
  OT: "bg-gray-100 text-gray-800",
  FC: "bg-red-100 text-red-800",
  NV: "bg-red-100 text-red-800",
  IN: "bg-red-100 text-red-800",
};

const thresholdLabels: Record<string, string> = {
  cgr_toma_razon: "Toma de razón CGR",
  core_approval: "Aprobación CORE",
  max_utm: "Tope UTM",
  min_clp: "Monto mínimo CLP",
  licitacion_max_days: "Plazo licitación",
  conservation_exempt_pct: "Exención conservación",
  gasto_admin_max_pct: "Gasto admin máx.",
  sisrec_mandatory_utm: "SISREC obligatorio",
  core_direct_assign_pct: "Asignación directa",
  puntaje_min: "Puntaje mínimo",
  cgr_res30_utm: "CGR Res. 30",
};

const slaLabels: Record<string, string> = {
  admisibilidad: "Admisibilidad",
  ate_first_rate: "Primera calificación ATE",
  fi_subsanacion: "Subsanación FI",
  rate_max: "Calificación máx.",
  licitacion: "Licitación",
  feedback_round: "Ronda feedback",
  consultas: "Consultas",
  ejecucion_max_months: "Ejecución máx. (meses)",
};

interface TrackCardProps {
  track: TrackInfo;
  gateResults?: TransitionReadiness[];
}

export function TrackCard({ track, gateResults }: TrackCardProps) {
  if (!track.mechanism) return null;

  const borderColor = mechanismBorderColors[track.mechanism] || "border-l-gray-400";
  const badgeColor = mechanismBgColors[track.mechanism] || "bg-gray-100 text-gray-800";
  const hasThresholds = Object.keys(track.thresholds).length > 0;
  const hasSLAs = Object.keys(track.sla_days).length > 0;
  const hasAttrs = Object.keys(track.mechanism_attrs).length > 0;
  const latestEval = track.evaluations.length > 0 ? track.evaluations[0] : null;

  return (
    <div className={cn("rounded-xl border bg-card border-l-4 p-4", borderColor)}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Badge className={cn("text-xs font-semibold", badgeColor)}>
            {track.mechanism}
          </Badge>
          <span className="text-sm font-medium">{track.mechanism_label}</span>
        </div>
        {latestEval && (
          <Badge
            variant="outline"
            className={cn(
              "text-xs",
              latestEval.completed_at
                ? "border-green-300 text-green-700"
                : "border-amber-300 text-amber-700"
            )}
          >
            {latestEval.completed_at
              ? `Evaluado: ${latestEval.result_code || "—"}`
              : "En evaluación"}
          </Badge>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        {/* Evaluador */}
        <div className="space-y-1">
          <div className="flex items-center gap-1 text-muted-foreground">
            <Building2 className="size-3" />
            <span>Evaluador</span>
          </div>
          <p className="font-medium">{track.evaluator_label || track.evaluator || "—"}</p>
        </div>

        {/* Producto favorable */}
        <div className="space-y-1">
          <div className="flex items-center gap-1 text-muted-foreground">
            <Target className="size-3" />
            <span>Producto F2</span>
          </div>
          <div className="flex gap-1 flex-wrap">
            {track.favorable_products.map((p) => (
              <Badge key={p} variant="secondary" className={cn("text-[10px] px-1.5 py-0", productColors[p])}>
                {p}
              </Badge>
            ))}
          </div>
        </div>

        {/* Umbrales */}
        {hasThresholds && (
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Shield className="size-3" />
              <span>Umbrales</span>
            </div>
            <div className="space-y-0.5">
              {Object.entries(track.thresholds).slice(0, 3).map(([key, val]) => (
                <p key={key}>
                  <span className="text-muted-foreground">{thresholdLabels[key] || key}:</span>{" "}
                  <span className="font-medium">{typeof val === "number" && val >= 1000 ? val.toLocaleString("es-CL") : val}</span>
                </p>
              ))}
            </div>
          </div>
        )}

        {/* SLAs */}
        {hasSLAs && (
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Clock className="size-3" />
              <span>Plazos (días)</span>
            </div>
            <div className="space-y-0.5">
              {Object.entries(track.sla_days).slice(0, 3).map(([key, val]) => (
                <p key={key}>
                  <span className="text-muted-foreground">{slaLabels[key] || key}:</span>{" "}
                  <span className="font-medium">{val}</span>
                </p>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Atributos del mecanismo */}
      {hasAttrs && (
        <div className="mt-3 pt-3 border-t">
          <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1.5">
            <FileCheck className="size-3" />
            <span>Atributos del track</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {Object.entries(track.mechanism_attrs).map(([key, val]) => (
              <Badge key={key} variant="outline" className="text-[10px]">
                {key}: {String(val)}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Gate indicators from readiness */}
      {gateResults && gateResults.length > 0 && (
        <div className="mt-3 pt-3 border-t">
          <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1.5">
            <Shield className="size-3" />
            <span>Gates próxima transición</span>
          </div>
          <div className="space-y-1">
            {gateResults.map((g) => (
              <div key={g.code} className="flex items-center gap-2 text-xs">
                {g.gates_total > 0 ? (
                  g.gates_met === g.gates_total ? (
                    <CheckCircle2 className="size-3.5 text-green-600 shrink-0" />
                  ) : (
                    <XCircle className="size-3.5 text-red-500 shrink-0" />
                  )
                ) : (
                  <CheckCircle2 className="size-3.5 text-muted-foreground shrink-0" />
                )}
                <span className="font-medium">{g.label}</span>
                {g.gates_total > 0 && (
                  <span className="text-[10px] text-muted-foreground tabular-nums">
                    {g.gates_met}/{g.gates_total}
                  </span>
                )}
                {g.blocking_gates.length > 0 && (
                  <span className="text-[10px] text-red-600 truncate">
                    {g.blocking_gates[0]}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
