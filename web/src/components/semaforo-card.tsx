"use client";

import { cn } from "@/lib/utils";

interface SemaforoCardProps {
  dimension: string;
  label: string;
  signal: "VERDE" | "AMARILLO" | "ROJO";
  indicatorCount: number;
  onClick?: () => void;
}

const signalBg: Record<string, string> = {
  VERDE: "bg-green-100 border-green-500",
  AMARILLO: "bg-amber-100 border-amber-500",
  ROJO: "bg-red-100 border-red-500",
};

const signalDot: Record<string, string> = {
  VERDE: "bg-green-500",
  AMARILLO: "bg-amber-500",
  ROJO: "bg-red-500",
};

const signalText: Record<string, string> = {
  VERDE: "text-green-700",
  AMARILLO: "text-amber-700",
  ROJO: "text-red-700",
};

const signalLabel: Record<string, string> = {
  VERDE: "OK",
  AMARILLO: "Atención",
  ROJO: "Crítico",
};

export function SemaforoCard({ dimension, label, signal, indicatorCount, onClick }: SemaforoCardProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-2 rounded-lg border-2 px-4 py-3 transition-all",
        signalBg[signal],
        onClick && "cursor-pointer hover:shadow-md hover:scale-[1.02]"
      )}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === "Enter" && onClick() : undefined}
    >
      <div className="flex items-center gap-2">
        <span className={cn("inline-block h-3 w-3 rounded-full shrink-0", signalDot[signal])} />
        <span className="text-xs font-mono font-semibold text-muted-foreground uppercase tracking-wide">
          {dimension}
        </span>
      </div>
      <p className="text-sm font-semibold leading-tight">{label}</p>
      <div className="flex items-center justify-between mt-1">
        <span className={cn("text-xs font-medium", signalText[signal])}>
          {signalLabel[signal]}
        </span>
        <span className="text-xs text-muted-foreground">
          {indicatorCount} indicador{indicatorCount !== 1 ? "es" : ""}
        </span>
      </div>
    </div>
  );
}
