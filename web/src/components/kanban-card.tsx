"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { DGIInitiative } from "@/types";

interface KanbanCardProps {
  initiative: DGIInitiative;
  onMove?: (direction: "left" | "right") => void;
  isFirst?: boolean;
  isLast?: boolean;
}

const dmaicColor: Record<string, string> = {
  DEFINE: "bg-blue-100 text-blue-700 border-blue-300",
  MEASURE: "bg-purple-100 text-purple-700 border-purple-300",
  ANALYZE: "bg-amber-100 text-amber-700 border-amber-300",
  IMPROVE: "bg-orange-100 text-orange-700 border-orange-300",
  CONTROL: "bg-green-100 text-green-700 border-green-300",
};

function getProgressColor(progress: number): string {
  if (progress >= 80) return "bg-green-500";
  if (progress >= 50) return "bg-blue-500";
  if (progress >= 25) return "bg-amber-500";
  return "bg-gray-400";
}

export function KanbanCard({ initiative, onMove, isFirst = false, isLast = false }: KanbanCardProps) {
  const { name, responsible_name, current_day, total_days, progress, dmaic_phase, division_name } = initiative;
  const progressColor = getProgressColor(progress);
  const dmaicClass = dmaic_phase ? (dmaicColor[dmaic_phase] ?? "bg-gray-100 text-gray-700 border-gray-300") : null;

  return (
    <div className="rounded-lg border bg-white shadow-sm p-3 space-y-2 hover:shadow-md transition-shadow">
      {/* Header row */}
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-semibold leading-tight flex-1">{name}</p>
        {dmaicClass && dmaic_phase && (
          <Badge
            variant="outline"
            className={cn("text-[10px] px-1.5 py-0 shrink-0 border", dmaicClass)}
          >
            {dmaic_phase}
          </Badge>
        )}
      </div>

      {/* Meta info */}
      <div className="space-y-0.5">
        {responsible_name && (
          <p className="text-xs text-muted-foreground truncate">
            <span className="font-medium">Resp:</span> {responsible_name}
          </p>
        )}
        {division_name && (
          <p className="text-xs text-muted-foreground truncate">
            <span className="font-medium">Div:</span> {division_name}
          </p>
        )}
      </div>

      {/* Progress bar */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Día {current_day}{total_days ? `/${total_days}` : ""}</span>
          <span className="font-medium">{progress}%</span>
        </div>
        <div className="h-1.5 w-full rounded-full bg-gray-200 overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all duration-500", progressColor)}
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      </div>

      {/* Move buttons */}
      {onMove && (
        <div className="flex gap-1 pt-1">
          {!isFirst && (
            <Button
              size="sm"
              variant="ghost"
              className="h-6 px-2 text-xs text-muted-foreground hover:text-foreground"
              onClick={() => onMove("left")}
            >
              ← Mover
            </Button>
          )}
          {!isLast && (
            <Button
              size="sm"
              variant="ghost"
              className="h-6 px-2 text-xs text-muted-foreground hover:text-foreground ml-auto"
              onClick={() => onMove("right")}
            >
              Mover →
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
