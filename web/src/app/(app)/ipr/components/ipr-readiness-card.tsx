"use client";

import { useState } from "react";
import { CheckCircle2, Circle, ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { IprReadiness } from "@/types";

interface IprReadinessCardProps {
  readiness: IprReadiness;
  currentPhase?: string;
}

export function IprReadinessCard({ readiness, currentPhase }: IprReadinessCardProps) {
  const isEarlyPhase = ["F0", "F1", "F2"].includes(currentPhase ?? "");
  const [expanded, setExpanded] = useState(isEarlyPhase);

  const filledCount = readiness.satellites.filter(s => s.count > 0).length;
  const totalCount = readiness.satellites.length;

  return (
    <div className="rounded-xl border bg-card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 text-left"
      >
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium">Preparacion</h3>
          <span className="text-xs text-muted-foreground">
            {filledCount}/{totalCount} satelites
          </span>
        </div>
        {expanded ? (
          <ChevronDown className="size-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="size-4 text-muted-foreground" />
        )}
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          <div className="grid grid-cols-3 gap-2">
            {readiness.satellites.map((sat) => (
              <div key={sat.name} className="flex items-center gap-1.5 text-xs">
                {sat.count > 0 ? (
                  <CheckCircle2 className="size-3.5 text-green-600 shrink-0" />
                ) : (
                  <Circle className="size-3.5 text-muted-foreground shrink-0" />
                )}
                <span className={sat.count > 0 ? "text-foreground" : "text-muted-foreground"}>
                  {sat.label}
                </span>
                <span className="text-muted-foreground tabular-nums ml-auto">
                  {sat.count}
                </span>
              </div>
            ))}
          </div>

          {readiness.next_transitions.length > 0 && (
            <div className="pt-2 border-t space-y-1.5">
              <p className="text-[11px] font-medium text-muted-foreground">Proximas transiciones</p>
              {readiness.next_transitions.map((t) => (
                <div key={t.code} className="flex items-center gap-2 text-xs">
                  <span className="font-medium">{t.label}</span>
                  {t.gates_total > 0 && (
                    <span className={cn(
                      "text-[10px] tabular-nums",
                      t.gates_met === t.gates_total ? "text-green-600" : "text-amber-600",
                    )}>
                      {t.gates_met}/{t.gates_total} gates
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
