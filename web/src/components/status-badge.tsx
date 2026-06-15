"use client";

import { CheckIcon, XIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "default";
}

/**
 * Static map of full Tailwind class strings per tone — light + dark.
 * Must stay literal (no `bg-${color}-50` interpolation) so the Tailwind JIT
 * actually emits the classes. Each tone targets AA contrast in both themes:
 * dark text on a light tint (light mode) / light text on a deep tint (dark mode).
 */
const TONES: Record<string, string> = {
  gray:    "border-gray-300 bg-gray-50 text-gray-700 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300",
  slate:   "border-slate-300 bg-slate-50 text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300",
  blue:    "border-blue-300 bg-blue-50 text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-300",
  cyan:    "border-cyan-300 bg-cyan-50 text-cyan-700 dark:border-cyan-800 dark:bg-cyan-950 dark:text-cyan-300",
  indigo:  "border-indigo-300 bg-indigo-50 text-indigo-700 dark:border-indigo-800 dark:bg-indigo-950 dark:text-indigo-300",
  purple:  "border-purple-300 bg-purple-50 text-purple-700 dark:border-purple-800 dark:bg-purple-950 dark:text-purple-300",
  violet:  "border-violet-300 bg-violet-50 text-violet-700 dark:border-violet-800 dark:bg-violet-950 dark:text-violet-300",
  green:   "border-green-300 bg-green-50 text-green-700 dark:border-green-800 dark:bg-green-950 dark:text-green-300",
  emerald: "border-emerald-300 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  teal:    "border-teal-300 bg-teal-50 text-teal-700 dark:border-teal-800 dark:bg-teal-950 dark:text-teal-300",
  lime:    "border-lime-300 bg-lime-50 text-lime-800 dark:border-lime-800 dark:bg-lime-950 dark:text-lime-300",
  amber:   "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300",
  orange:  "border-orange-300 bg-orange-50 text-orange-700 dark:border-orange-800 dark:bg-orange-950 dark:text-orange-300",
  red:     "border-red-300 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300",
};

/** Resolve a tone name to its full class string (falls back to neutral gray). */
export function tone(color: string): string {
  return TONES[color] ?? TONES.gray;
}

type Config = { label: string; color: keyof typeof TONES };

// Acto administrativo states — 7-step FSM
const ACTO_STATE_CONFIG: Record<string, Config> = {
  BORRADOR: { label: "Borrador", color: "gray" },
  VISADO: { label: "Visado", color: "violet" },
  FIRMADO: { label: "Firmado", color: "green" },
  ENVIADO_CGR: { label: "Enviado a CGR", color: "green" },
  OBSERVADO: { label: "Observado por CGR", color: "amber" },
  TOMADO_RAZON: { label: "Toma de Razón", color: "emerald" },
  RECHAZADO_CGR: { label: "Rechazado CGR", color: "red" },
};

// IPR states — color by phase. Evaluation-result codes use the human glosa
// from the backend `_EVAL_LABELS` (no raw RS/FI/OT acronyms in the UI).
const IPR_STATE_CONFIG: Record<string, Config> = {
  // F0
  INGRESADO: { label: "Ingresado", color: "slate" },
  // F1
  EN_REVISION: { label: "En Revisión", color: "blue" },
  PRE_ADMISIBLE: { label: "Pre-Admisible", color: "blue" },
  ADMISIBLE: { label: "Admisible", color: "blue" },
  INADMISIBLE: { label: "Inadmisible", color: "red" },
  // F2 — evaluation results (glosa, not codes)
  EN_EVALUACION: { label: "En Evaluación", color: "cyan" },
  RS: { label: "Rec. Satisfactoria", color: "cyan" },
  FI: { label: "Favorable c/ Indicaciones", color: "cyan" },
  FC: { label: "Favorable Condicionado", color: "cyan" },
  OT: { label: "Observado Técnicamente", color: "amber" },
  AD: { label: "Aprobado Directo", color: "cyan" },
  RF: { label: "Rec. Favorable", color: "cyan" },
  ITF: { label: "Informe Técnico Favorable", color: "cyan" },
  AT: { label: "Aprobado Técnicamente", color: "cyan" },
  // F3
  CDP_EMITIDO: { label: "CDP Emitido", color: "purple" },
  // F4
  EN_FORMALIZACION: { label: "En Formalización", color: "green" },
  FORMALIZADO: { label: "Formalizado", color: "green" },
  EN_LICITACION: { label: "En Licitación", color: "green" },
  ADJUDICADO: { label: "Adjudicado", color: "green" },
  CONTRATO_FIRMADO: { label: "Contrato Firmado", color: "green" },
  EN_EJECUCION: { label: "En Ejecución", color: "emerald" },
  EN_OBRA: { label: "En Obra", color: "emerald" },
  RECEPCION_PROVISORIA: { label: "Recepción Provisoria", color: "teal" },
  RECEPCION_DEFINITIVA: { label: "Recepción Definitiva", color: "teal" },
  SUSPENDIDO: { label: "Suspendido", color: "amber" },
  // F5
  EN_RENDICION: { label: "En Rendición", color: "gray" },
  RENDICION_APROBADA: { label: "Rendición Aprobada", color: "gray" },
  EN_CIERRE_ADMINISTRATIVO: { label: "En Cierre Administrativo", color: "gray" },
  CERRADO: { label: "Cerrado", color: "gray" },
  // Terminales cross-cutting
  ANULADO: { label: "Anulado", color: "red" },
  TERMINADO_ANTICIPADAMENTE: { label: "Terminado Anticipadamente", color: "orange" },
};

export function StatusBadge({ status, size = "default" }: StatusBadgeProps) {
  const sizeClass = size === "sm" ? "text-[10px] px-1.5 py-0" : "";

  // IPR states first (most common use case)
  const iprConfig = IPR_STATE_CONFIG[status];
  if (iprConfig) {
    return (
      <Badge variant="outline" className={cn(tone(iprConfig.color), sizeClass)}>
        {iprConfig.label}
      </Badge>
    );
  }

  // Acto administrativo states
  const actoConfig = ACTO_STATE_CONFIG[status];
  if (actoConfig) {
    return (
      <Badge variant="outline" className={cn(tone(actoConfig.color), sizeClass)}>
        {actoConfig.label}
      </Badge>
    );
  }

  switch (status) {
    case "PENDIENTE":
      return (
        <Badge variant="outline" className={cn(tone("gray"), sizeClass)}>
          Pendiente
        </Badge>
      );
    case "EN_PROGRESO":
      return (
        <Badge variant="default" className={cn("bg-blue-600 text-white", sizeClass)}>
          En Progreso
        </Badge>
      );
    case "COMPLETADO":
      return (
        <Badge variant="default" className={cn("bg-amber-500 text-white", sizeClass)}>
          Completado
        </Badge>
      );
    case "VERIFICADO":
      return (
        <Badge variant="default" className={cn("bg-green-600 text-white", sizeClass)}>
          <CheckIcon className="size-3" />
          Verificado
        </Badge>
      );
    case "VENCIDO":
      return (
        <Badge variant="destructive" className={sizeClass}>
          Vencido
        </Badge>
      );
    case "CANCELADO":
      return (
        <Badge variant="secondary" className={cn("line-through", sizeClass)}>
          Cancelado
        </Badge>
      );
    case "ABIERTO":
      return (
        <Badge variant="outline" className={cn(tone("red"), sizeClass)}>
          Abierto
        </Badge>
      );
    case "EN_GESTION":
      return (
        <Badge variant="default" className={cn("bg-blue-600 text-white", sizeClass)}>
          En Gestión
        </Badge>
      );
    case "RESUELTO":
      return (
        <Badge variant="default" className={cn("bg-green-600 text-white", sizeClass)}>
          <CheckIcon className="size-3" />
          Resuelto
        </Badge>
      );
    case "CERRADO_SIN_RESOLVER":
      return (
        <Badge variant="secondary" className={sizeClass}>
          <XIcon className="size-3" />
          Cerrado sin Resolver
        </Badge>
      );
    case "EN_REVISION_RTF":
      return (
        <Badge variant="outline" className={cn(tone("amber"), sizeClass)}>
          En Revisión RTF
        </Badge>
      );
    case "VISADA_RTF":
      return (
        <Badge variant="outline" className={cn(tone("blue"), sizeClass)}>
          Visada RTF
        </Badge>
      );
    case "EN_REVISION_UCR":
      return (
        <Badge variant="outline" className={cn(tone("indigo"), sizeClass)}>
          En Revisión UCR
        </Badge>
      );
    case "OBSERVADA":
      return (
        <Badge variant="outline" className={cn(tone("orange"), sizeClass)}>
          Observada
        </Badge>
      );
    case "APROBADA":
      return (
        <Badge variant="default" className={cn("bg-green-600 text-white", sizeClass)}>
          <CheckIcon className="size-3" />
          Aprobada
        </Badge>
      );
    case "APROBADA_PARCIALMENTE":
      return (
        <Badge variant="outline" className={cn(tone("lime"), sizeClass)}>
          Aprobada Parcialmente
        </Badge>
      );
    case "RECHAZADA":
      return (
        <Badge variant="destructive" className={sizeClass}>
          <XIcon className="size-3" />
          Rechazada
        </Badge>
      );
    default:
      return (
        <Badge variant="secondary" className={sizeClass}>
          {status}
        </Badge>
      );
  }
}
