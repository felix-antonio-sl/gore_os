// =============================================================================
// packages/ui/src/atoms/StatusBadge.tsx — Status indicator badges
// =============================================================================

import * as React from "react";
import { cn } from "../lib/utils";

export type StatusType = 
  | "PENDIENTE" 
  | "EN_PROGRESO" 
  | "COMPLETADO" 
  | "VERIFICADO" 
  | "CANCELADO"
  | "ABIERTO"
  | "EN_GESTION"
  | "RESUELTO"
  | "CERRADO_SIN_RESOLVER";

const statusStyles: Record<StatusType, string> = {
  PENDIENTE: "bg-yellow-100 text-yellow-800 border-yellow-300",
  EN_PROGRESO: "bg-blue-100 text-blue-800 border-blue-300",
  COMPLETADO: "bg-green-100 text-green-800 border-green-300",
  VERIFICADO: "bg-emerald-100 text-emerald-800 border-emerald-300",
  CANCELADO: "bg-gray-100 text-gray-800 border-gray-300",
  ABIERTO: "bg-red-100 text-red-800 border-red-300",
  EN_GESTION: "bg-orange-100 text-orange-800 border-orange-300",
  RESUELTO: "bg-green-100 text-green-800 border-green-300",
  CERRADO_SIN_RESOLVER: "bg-gray-100 text-gray-800 border-gray-300",
};

const statusLabels: Record<StatusType, string> = {
  PENDIENTE: "Pendiente",
  EN_PROGRESO: "En Progreso",
  COMPLETADO: "Completado",
  VERIFICADO: "Verificado",
  CANCELADO: "Cancelado",
  ABIERTO: "Abierto",
  EN_GESTION: "En Gestión",
  RESUELTO: "Resuelto",
  CERRADO_SIN_RESOLVER: "Cerrado S/R",
};

export interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
        statusStyles[status] || "bg-gray-100 text-gray-800",
        className
      )}
    >
      {statusLabels[status] || status}
    </span>
  );
}
