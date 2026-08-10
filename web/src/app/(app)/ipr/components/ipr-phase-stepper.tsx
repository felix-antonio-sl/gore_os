import { Badge } from "@/components/ui/badge";
import { CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { MCD_PHASES, mcdPhaseColors } from "./ipr-constants";
import { useState } from "react";

interface IprPhaseStepperProps {
  currentPhase: string;
  currentPhaseLabel?: string;
  phaseEnteredAt?: string;
}

export function IprPhaseStepper({ currentPhase, currentPhaseLabel, phaseEnteredAt }: IprPhaseStepperProps) {
  const [referenceTime] = useState(Date.now);
  const daysInPhase = phaseEnteredAt ? Math.floor((referenceTime - new Date(phaseEnteredAt).getTime()) / 86400000) : null;
  const currentIdx = MCD_PHASES.findIndex(p => p.code === currentPhase);
  // Keep the badge label consistent with the stepper circle label for this phase.
  const phaseLabel = MCD_PHASES[currentIdx]?.label ?? currentPhaseLabel ?? "";

  return (
    <div className="rounded-xl border bg-card p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-muted-foreground">Ciclo de Vida</h3>
        <Badge variant="outline" className={cn("text-xs", mcdPhaseColors[currentPhase])}>
          {currentPhase} — {phaseLabel}
        </Badge>
      </div>
      <div className="flex items-center gap-0">
        {MCD_PHASES.map((phase, idx) => {
          const isActive = idx === currentIdx;
          const isPast = idx < currentIdx;
          return (
            <div key={phase.code} className="flex items-center flex-1 min-w-0">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={cn(
                    "size-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors",
                    isActive && "bg-primary text-primary-foreground border-primary",
                    isPast && "bg-primary/20 text-primary border-primary/40",
                    !isActive && !isPast && "bg-muted text-muted-foreground border-border",
                  )}
                >
                  {isPast ? <CheckCircle2 className="size-4" /> : phase.code}
                </div>
                <span className={cn(
                  // Hide labels on very small screens to avoid overlap; keep the circle.
                  // The active phase label stays visible so context is never lost.
                  "text-[10px] mt-1 text-center leading-tight max-w-full truncate px-0.5",
                  isActive ? "font-semibold text-foreground" : "text-muted-foreground hidden sm:block",
                )}>
                  {phase.label}
                </span>
                {isActive && daysInPhase !== null && (
                  <span className={cn(
                    "text-[9px] tabular-nums font-medium mt-0.5",
                    daysInPhase <= 30 ? "text-green-600" : daysInPhase <= 90 ? "text-amber-600" : "text-red-600"
                  )}>
                    {daysInPhase}d
                  </span>
                )}
              </div>
              {idx < MCD_PHASES.length - 1 && (
                <div className={cn(
                  "h-0.5 flex-1 min-w-2",
                  idx < currentIdx ? "bg-primary/40" : "bg-border",
                )} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
