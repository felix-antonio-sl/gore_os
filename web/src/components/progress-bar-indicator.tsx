"use client";

import { cn } from "@/lib/utils";

interface ProgressBarIndicatorProps {
  label: string;
  value: number;
  target: number;
  unit?: string;
  trend?: "up" | "down" | "flat";
}

function getBarColor(value: number, target: number): string {
  if (target <= 0) return "bg-gray-400";
  const ratio = value / target;
  if (ratio >= 1) return "bg-green-500";
  if (ratio >= 0.9) return "bg-amber-500";
  return "bg-red-500";
}

function getTrendArrow(trend?: "up" | "down" | "flat"): { symbol: string; color: string } {
  switch (trend) {
    case "up":
      return { symbol: "↑", color: "text-green-600" };
    case "down":
      return { symbol: "↓", color: "text-red-600" };
    case "flat":
      return { symbol: "→", color: "text-gray-500" };
    default:
      return { symbol: "–", color: "text-gray-400" };
  }
}

export function ProgressBarIndicator({ label, value, target, unit = "%", trend }: ProgressBarIndicatorProps) {
  const pct = target > 0 ? Math.min((value / target) * 100, 100) : 0;
  const barColor = getBarColor(value, target);
  const trendInfo = getTrendArrow(trend);

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium truncate">{label}</span>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="text-sm font-semibold tabular-nums">
            {value.toFixed(1)}{unit}
          </span>
          <span className="text-xs text-muted-foreground">
            / {target.toFixed(1)}{unit}
          </span>
          <span className={cn("text-base font-bold leading-none", trendInfo.color)}>
            {trendInfo.symbol}
          </span>
        </div>
      </div>
      <div className="relative h-2 w-full rounded-full bg-gray-200 overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-500", barColor)}
          style={{ width: `${pct}%` }}
        />
        {/* Target marker at 100% */}
        <div className="absolute right-0 top-0 h-full w-0.5 bg-gray-500 opacity-40" />
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">
          {pct.toFixed(0)}% de meta
        </span>
        {value >= target && (
          <span className="text-xs font-medium text-green-600">Meta alcanzada</span>
        )}
      </div>
    </div>
  );
}
