"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, ShieldCheck, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import type { IprReadiness } from "@/types";

interface IprReadinessCardProps {
  readiness: IprReadiness;
  currentPhase?: string;
}

export function IprReadinessCard({ readiness, currentPhase }: IprReadinessCardProps) {
  const isEarlyPhase = ["F0", "F1", "F2"].includes(currentPhase ?? "");
  const [expanded, setExpanded] = useState(isEarlyPhase);

  const filled = readiness.satellites.filter((s) => s.count > 0);
  const empty = readiness.satellites.filter((s) => s.count === 0);
  const filledCount = filled.length;
  const totalCount = readiness.satellites.length;
  const pct = Math.round((filledCount / totalCount) * 100);

  const gatedTransitions = readiness.next_transitions.filter((t) => t.gates_total > 0);

  return (
    <div className="rounded-xl border bg-card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-4 text-left"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <h3 className="text-sm font-medium">Satélites IPR</h3>
            <span className="text-xs text-muted-foreground tabular-nums">
              {filledCount} de {totalCount}
            </span>
          </div>
          {/* Progress bar */}
          <div className="h-1.5 rounded-full bg-muted overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all duration-500",
                pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-amber-500" : "bg-muted-foreground/40"
              )}
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
        {expanded ? (
          <ChevronDown className="size-4 text-muted-foreground shrink-0" />
        ) : (
          <ChevronRight className="size-4 text-muted-foreground shrink-0" />
        )}
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          {/* Satellite pills — filled first (green), then empty (dashed) */}
          <div className="flex flex-wrap gap-1.5">
            {filled.map((sat) => (
              <span
                key={sat.name}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800"
              >
                {sat.label}
                <span className="bg-green-600 text-white rounded-full px-1 min-w-[18px] text-center text-[10px] leading-[16px] dark:bg-green-500">
                  {sat.count}
                </span>
              </span>
            ))}
            {empty.map((sat) => (
              <span
                key={sat.name}
                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs text-muted-foreground border border-dashed border-muted-foreground/25"
              >
                {sat.label}
              </span>
            ))}
          </div>

          {/* Phase-crossing transitions with gate progress */}
          {gatedTransitions.length > 0 && (
            <div className="pt-2 border-t space-y-1.5">
              <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
                Gates próxima fase
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
