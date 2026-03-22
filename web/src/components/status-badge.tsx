"use client";

import { CheckIcon, XIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "default";
}

// Acto administrativo states — 7-step FSM (violet accent)
const ACTO_STATE_CONFIG: Record<string, { label: string; className: string }> = {
  BORRADOR: { label: "Borrador", className: "border-gray-400 text-gray-700 bg-gray-50" },
  VISADO: { label: "Visado", className: "border-violet-400 text-violet-700 bg-violet-50" },
  FIRMADO: { label: "Firmado", className: "border-green-400 text-green-700 bg-green-50" },
  ENVIADO_CGR: { label: "Enviado a CGR", className: "border-green-500 text-green-800 bg-green-50" },
  OBSERVADO: { label: "Observado por CGR", className: "border-amber-500 text-amber-800 bg-amber-50" },
  TOMADO_RAZON: { label: "Toma de Razón", className: "border-emerald-500 text-emerald-800 bg-emerald-50" },
  RECHAZADO_CGR: { label: "Rechazado CGR", className: "border-red-500 text-red-700 bg-red-50" },
};

// IPR states — color by phase (F0=slate, F1=blue, F2=cyan, F3=purple, F4=green, F5=gray)
const IPR_STATE_CONFIG: Record<string, { label: string; className: string }> = {
  // F0
  INGRESADO: { label: "Ingresado", className: "border-slate-400 text-slate-700 bg-slate-50" },
  // F1
  EN_REVISION: { label: "En Revisión", className: "border-blue-400 text-blue-700 bg-blue-50" },
  PRE_ADMISIBLE: { label: "Pre-Admisible", className: "border-blue-400 text-blue-700 bg-blue-50" },
  ADMISIBLE: { label: "Admisible", className: "border-blue-500 text-blue-800 bg-blue-50" },
  INADMISIBLE: { label: "Inadmisible", className: "border-red-400 text-red-700 bg-red-50" },
  // F2
  EN_EVALUACION: { label: "En Evaluación", className: "border-cyan-400 text-cyan-700 bg-cyan-50" },
  RS: { label: "RS", className: "border-cyan-500 text-cyan-800 bg-cyan-50" },
  FI: { label: "FI", className: "border-cyan-500 text-cyan-800 bg-cyan-50" },
  FC: { label: "FC", className: "border-cyan-500 text-cyan-800 bg-cyan-50" },
  OT: { label: "OT", className: "border-cyan-500 text-cyan-800 bg-cyan-50" },
  AD: { label: "AD", className: "border-cyan-500 text-cyan-800 bg-cyan-50" },
  RF: { label: "RF", className: "border-cyan-500 text-cyan-800 bg-cyan-50" },
  ITF: { label: "ITF", className: "border-cyan-400 text-cyan-700 bg-cyan-50" },
  AT: { label: "AT", className: "border-cyan-400 text-cyan-700 bg-cyan-50" },
  // F3
  CDP_EMITIDO: { label: "CDP Emitido", className: "border-purple-400 text-purple-700 bg-purple-50" },
  // F4
  EN_FORMALIZACION: { label: "En Formalización", className: "border-green-400 text-green-700 bg-green-50" },
  FORMALIZADO: { label: "Formalizado", className: "border-green-500 text-green-800 bg-green-50" },
  EN_LICITACION: { label: "En Licitación", className: "border-green-400 text-green-700 bg-green-50" },
  ADJUDICADO: { label: "Adjudicado", className: "border-green-500 text-green-800 bg-green-50" },
  CONTRATO_FIRMADO: { label: "Contrato Firmado", className: "border-green-600 text-green-800 bg-green-50" },
  EN_EJECUCION: { label: "En Ejecución", className: "border-emerald-500 text-emerald-800 bg-emerald-50" },
  EN_OBRA: { label: "En Obra", className: "border-emerald-500 text-emerald-800 bg-emerald-50" },
  RECEPCION_PROVISORIA: { label: "Recepción Provisoria", className: "border-teal-400 text-teal-700 bg-teal-50" },
  RECEPCION_DEFINITIVA: { label: "Recepción Definitiva", className: "border-teal-500 text-teal-800 bg-teal-50" },
  SUSPENDIDO: { label: "Suspendido", className: "border-amber-500 text-amber-800 bg-amber-50" },
  // F5
  EN_RENDICION: { label: "En Rendición", className: "border-gray-400 text-gray-700 bg-gray-50" },
  RENDICION_APROBADA: { label: "Rendición Aprobada", className: "border-gray-500 text-gray-800 bg-gray-50" },
  EN_CIERRE_ADMINISTRATIVO: { label: "En Cierre Administrativo", className: "border-gray-500 text-gray-800 bg-gray-50" },
  CERRADO: { label: "Cerrado", className: "border-gray-600 text-gray-900 bg-gray-100" },
  // Terminales cross-cutting
  ANULADO: { label: "Anulado", className: "border-red-500 text-red-700 bg-red-50" },
  TERMINADO_ANTICIPADAMENTE: { label: "Terminado Anticipadamente", className: "border-orange-500 text-orange-800 bg-orange-50" },
};

export function StatusBadge({ status, size = "default" }: StatusBadgeProps) {
  const sizeClass = size === "sm" ? "text-[10px] px-1.5 py-0" : "";

  // Check IPR states first (most common use case)
  const iprConfig = IPR_STATE_CONFIG[status];
  if (iprConfig) {
    return (
      <Badge variant="outline" className={cn(iprConfig.className, sizeClass)}>
        {iprConfig.label}
      </Badge>
    );
  }

  // Acto administrativo states
  const actoConfig = ACTO_STATE_CONFIG[status];
  if (actoConfig) {
    return (
      <Badge variant="outline" className={cn(actoConfig.className, sizeClass)}>
        {actoConfig.label}
      </Badge>
    );
  }

  switch (status) {
    case "PENDIENTE":
      return (
        <Badge variant="outline" className={cn("border-gray-400 text-gray-800", sizeClass)}>
          Pendiente
        </Badge>
      );
    case "EN_PROGRESO":
      return (
        <Badge variant="default" className={cn("bg-blue-600", sizeClass)}>
          En Progreso
        </Badge>
      );
    case "COMPLETADO":
      return (
        <Badge variant="default" className={cn("bg-amber-500", sizeClass)}>
          Completado
        </Badge>
      );
    case "VERIFICADO":
      return (
        <Badge variant="default" className={cn("bg-green-600", sizeClass)}>
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
        <Badge variant="outline" className={cn("border-red-500 text-red-600", sizeClass)}>
          Abierto
        </Badge>
      );
    case "EN_GESTION":
      return (
        <Badge variant="default" className={cn("bg-blue-600", sizeClass)}>
          En Gestión
        </Badge>
      );
    case "RESUELTO":
      return (
        <Badge variant="default" className={cn("bg-green-600", sizeClass)}>
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
        <Badge variant="outline" className={cn("border-amber-400 text-amber-700 bg-amber-50", sizeClass)}>
          En Revisión RTF
        </Badge>
      );
    case "VISADA_RTF":
      return (
        <Badge variant="outline" className={cn("border-blue-400 text-blue-700 bg-blue-50", sizeClass)}>
          Visada RTF
        </Badge>
      );
    case "EN_REVISION_UCR":
      return (
        <Badge variant="outline" className={cn("border-indigo-400 text-indigo-700 bg-indigo-50", sizeClass)}>
          En Revisión UCR
        </Badge>
      );
    case "OBSERVADA":
      return (
        <Badge variant="outline" className={cn("border-orange-400 text-orange-700 bg-orange-50", sizeClass)}>
          Observada
        </Badge>
      );
    case "APROBADA":
      return (
        <Badge variant="default" className={cn("bg-green-600", sizeClass)}>
          <CheckIcon className="size-3" />
          Aprobada
        </Badge>
      );
    case "APROBADA_PARCIALMENTE":
      return (
        <Badge variant="outline" className={cn("border-lime-500 text-lime-800 bg-lime-50", sizeClass)}>
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
