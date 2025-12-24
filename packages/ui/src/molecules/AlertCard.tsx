// =============================================================================
// packages/ui/src/molecules/AlertCard.tsx — Alert display card
// =============================================================================

import * as React from "react";
import { cn } from "../lib/utils";
import { Icons } from "../atoms/GoreIcon";

export type AlertLevel = "INFO" | "ATENCION" | "ALTO" | "CRITICO";

const levelStyles: Record<AlertLevel, string> = {
  INFO: "border-l-blue-500 bg-blue-50",
  ATENCION: "border-l-yellow-500 bg-yellow-50",
  ALTO: "border-l-orange-500 bg-orange-50",
  CRITICO: "border-l-red-500 bg-red-50 animate-pulse",
};

const levelIcons: Record<AlertLevel, React.ReactNode> = {
  INFO: <Icons.FileText className="h-5 w-5 text-blue-500" />,
  ATENCION: <Icons.AlertTriangle className="h-5 w-5 text-yellow-500" />,
  ALTO: <Icons.AlertTriangle className="h-5 w-5 text-orange-500" />,
  CRITICO: <Icons.AlertTriangle className="h-5 w-5 text-red-500" />,
};

export interface AlertCardProps {
  nivel: AlertLevel;
  tipo: string;
  mensaje: string;
  generada_en: string;
  activa?: boolean;
  onAttend?: () => void;
  className?: string;
}

export function AlertCard({
  nivel,
  tipo,
  mensaje,
  generada_en,
  activa = true,
  onAttend,
  className,
}: AlertCardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border-l-4 p-4 shadow-sm transition-all",
        levelStyles[nivel] || "border-l-gray-500 bg-gray-50",
        !activa && "opacity-60",
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          {levelIcons[nivel]}
          <div>
            <p className="text-sm font-medium text-gray-900">{tipo.replace(/_/g, " ")}</p>
            <p className="mt-1 text-sm text-gray-600">{mensaje}</p>
            <p className="mt-2 text-xs text-gray-400">
              {new Date(generada_en).toLocaleString("es-CL")}
            </p>
          </div>
        </div>
        {activa && onAttend && (
          <button
            onClick={onAttend}
            className="rounded bg-white px-3 py-1 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-100"
          >
            Atender
          </button>
        )}
      </div>
    </div>
  );
}
