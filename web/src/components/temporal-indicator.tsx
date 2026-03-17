"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { TEMPORAL_STATES, resolveTemporalState } from "@/lib/status-colors";

interface TemporalIndicatorProps {
  daysRemaining: number;
  state: string;
}

export function TemporalIndicator({ daysRemaining, state }: TemporalIndicatorProps) {
  const key = resolveTemporalState(daysRemaining, state);
  const config = TEMPORAL_STATES[key];

  if (config.hidden) return null;

  const label = typeof config.label === "function"
    ? config.label(daysRemaining)
    : config.label;

  if (key === "completed") {
    return (
      <Badge variant="default" className={config.className}>
        {label}
      </Badge>
    );
  }

  if (key === "normal") {
    return <span className={cn("text-xs", config.className)}>{label}</span>;
  }

  return (
    <span className={cn(
      "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
      config.className
    )}>
      {label}
    </span>
  );
}
