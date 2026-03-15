"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Building2, Clock, Shield, Target, FileCheck } from "lucide-react";
import type { TrackInfo } from "@/types";

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

const productLabels: Record<string, string> = {
  RS: "Rec. Satisfactoria",
  RF: "Rec. Favorable",
  ITF: "Inf. Técnico Favorable",
  FI: "Favorable c/ Indicaciones",
  FC: "Favorable Condicionado",
  OT: "Observado Técnicamente",
  AD: "Aprobado Directo",
  AT: "Aprobado Técnicamente",
  NV: "No Viable",
  IN: "Inadmisible",
};

const thresholdLabels: Record<string, string> = {
  cgr_toma_razon: "Contraloría revisa sobre",
  core_approval: "Aprobación Consejo Regional sobre",
  max_utm: "Monto máximo",
  min_clp: "Monto mínimo",
  licitacion_max_days: "Plazo licitación",
  conservation_exempt_pct: "Exención conservación",
  gasto_admin_max_pct: "Gasto administrativo máx.",
  sisrec_mandatory_utm: "Rendición obligatoria sobre",
  core_direct_assign_pct: "Asignación directa máx.",
  puntaje_min: "Puntaje mínimo requerido",
  cgr_res30_utm: "Contraloría Res. 30 sobre",
  directorio_max_days: "Vigencia directorio máx.",
  pagare_coverage_pct: "Cobertura pagaré mín.",
  pagare_min_months: "Pagaré vigencia mín. (meses)",
  ranking_persistence: "Persistencia ranking",
  fril_max_per_comuna: "Máximo FRIL por comuna",
  fril_tender_days: "Plazo licitación FRIL",
};

const slaLabels: Record<string, string> = {
  admisibilidad: "Admisibilidad",
  ate_first_rate: "Evaluación técnica",
  fi_subsanacion: "Subsanación observaciones",
  rate_max: "Evaluación máxima",
  licitacion: "Licitación",
  feedback_round: "Ronda observaciones",
  consultas: "Consultas",
  ejecucion_max_months: "Ejecución máxima (meses)",
  evaluation_max_days: "Evaluación",
  report_frequency_days: "Informe periódico",
};

interface TrackCardProps {
  track: TrackInfo;
}

export function TrackCard({ track }: TrackCardProps) {
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
            <span>Dictamen requerido</span>
          </div>
          <div className="flex gap-1 flex-wrap">
            {track.favorable_products.map((p) => (
              <Badge key={p} variant="secondary" className={cn("text-[10px] px-1.5 py-0", productColors[p])}>
                {productLabels[p] ?? p}
              </Badge>
            ))}
          </div>
        </div>

        {/* Umbrales */}
        {hasThresholds && (
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Shield className="size-3" />
              <span>Requisitos</span>
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

    </div>
  );
}
