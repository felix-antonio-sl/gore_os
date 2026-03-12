import { Badge } from "@/components/ui/badge";
import { CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { MCD_PHASES, mcdPhaseColors } from "./ipr-constants";

interface IprPhaseStepperProps {
  currentPhase: string;
  currentPhaseLabel?: string;
}

export function IprPhaseStepper({ currentPhase, currentPhaseLabel }: IprPhaseStepperProps) {
  const currentIdx = MCD_PHASES.findIndex(p => p.code === currentPhase);

  return (
    <div className="rounded-xl border bg-card p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-muted-foreground">Ciclo de Vida MCD</h3>
        <Badge variant="outline" className={cn("text-xs", mcdPhaseColors[currentPhase])}>
          {currentPhase} — {currentPhaseLabel}
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
                  "text-[10px] mt-1 text-center leading-tight",
                  isActive ? "font-semibold text-foreground" : "text-muted-foreground",
                )}>
                  {phase.label}
                </span>
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
