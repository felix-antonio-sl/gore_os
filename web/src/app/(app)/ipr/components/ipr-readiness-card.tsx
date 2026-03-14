"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Circle,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { IprReadiness } from "@/types";

interface IprReadinessCardProps {
  readiness: IprReadiness;
  currentPhase?: string;
}

export function IprReadinessCard({ readiness, currentPhase }: IprReadinessCardProps) {
  const isEarlyPhase = ["F0", "F1", "F2"].includes(currentPhase ?? "");
  const [expanded, setExpanded] = useState(isEarlyPhase);

  const filledCount = readiness.satellites.filter((s) => s.count > 0).length;
  const totalCount = readiness.satellites.length;

  // Only show transitions that have actual gates to evaluate
  const gatedTransitions = readiness.next_transitions.filter((t) => t.gates_total > 0);

  return (
    <div className="rounded-xl border bg-card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 text-left"
      >
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium">Preparación</h3>
          <span className="text-xs text-muted-foreground tabular-nums">
            {filledCount}/{totalCount} satélites
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
          {/* Satellite grid — count inline after label to avoid column bleed */}
          <div className="grid grid-cols-3 gap-x-6 gap-y-1.5">
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
                {sat.count > 0 && (
                  <span className="text-muted-foreground tabular-nums text-[10px]">
                    ({sat.count})
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Phase-crossing transitions with gate progress */}
          {gatedTransitions.length > 0 && (
            <div className="pt-2 border-t space-y-1.5">
              <p className="text-[11px] font-medium text-muted-foreground">
                Gates próxima transición
              </p>
              {gatedTransitions.map((t) => {
                const allMet = t.gates_met === t.gates_total;
                return (
                  <div key={t.code} className="flex items-center gap-2 text-xs">
                    {allMet ? (
                      <ShieldCheck className="size-3.5 text-green-600 shrink-0" />
                    ) : (
                      <ShieldAlert className="size-3.5 text-amber-600 shrink-0" />
                    )}
                    <span className="font-medium">{t.label}</span>
                    <span
                      className={cn(
                        "text-[10px] tabular-nums",
                        allMet ? "text-green-600" : "text-amber-600"
                      )}
                    >
                      {t.gates_met}/{t.gates_total}
                    </span>
                    {t.blocking_gates.length > 0 && (
                      <span className="text-[10px] text-red-600 truncate max-w-48">
                        {t.blocking_gates[0]}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
