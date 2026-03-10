"use client";

import { cn } from "@/lib/utils";
import { SIGNAL_BG, SIGNAL_DOT, SIGNAL_TEXT, SIGNAL_LABEL } from "@/lib/status-colors";

interface SemaforoCardProps {
  dimension: string;
  label: string;
  signal: "VERDE" | "AMARILLO" | "ROJO";
  indicatorCount: number;
  onClick?: () => void;
}

export function SemaforoCard({ dimension, label, signal, indicatorCount, onClick }: SemaforoCardProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-2 rounded-lg border-2 px-4 py-3 transition-all",
        SIGNAL_BG[signal],
        onClick && "cursor-pointer hover:shadow-md hover:scale-[1.02]"
      )}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === "Enter" && onClick() : undefined}
    >
      <div className="flex items-center gap-2">
        <span className={cn("inline-block h-3 w-3 rounded-full shrink-0", SIGNAL_DOT[signal])} />
        <span className="text-xs font-mono font-semibold text-muted-foreground uppercase tracking-wide">
          {dimension}
        </span>
      </div>
      <p className="text-sm font-semibold leading-tight">{label}</p>
      <div className="flex items-center justify-between mt-1">
        <span className={cn("text-xs font-medium", SIGNAL_TEXT[signal])}>
          {SIGNAL_LABEL[signal]}
        </span>
        <span className="text-xs text-muted-foreground">
          {indicatorCount} indicador{indicatorCount !== 1 ? "es" : ""}
        </span>
      </div>
    </div>
  );
}
