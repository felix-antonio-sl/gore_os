// =============================================================================
// packages/ui/src/atoms/PriorityBadge.tsx — Priority indicator badges
// =============================================================================

import * as React from "react";
import { cn } from "../lib/utils";

export type PriorityType = "BAJA" | "MEDIA" | "ALTA" | "URGENTE";

const priorityStyles: Record<PriorityType, string> = {
  BAJA: "bg-gray-100 text-gray-600",
  MEDIA: "bg-blue-100 text-blue-700",
  ALTA: "bg-orange-100 text-orange-700",
  URGENTE: "bg-red-100 text-red-700 font-bold animate-pulse",
};

const priorityLabels: Record<PriorityType, string> = {
  BAJA: "Baja",
  MEDIA: "Media",
  ALTA: "Alta",
  URGENTE: "¡Urgente!",
};

export interface PriorityBadgeProps {
  priority: PriorityType;
  className?: string;
}

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded px-2 py-0.5 text-xs font-medium",
        priorityStyles[priority] || "bg-gray-100 text-gray-600",
        className
      )}
    >
      {priorityLabels[priority] || priority}
    </span>
  );
}
