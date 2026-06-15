import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronRight, Info, Loader2, Lock, ShieldCheck, ShieldX } from "lucide-react";
import { cn } from "@/lib/utils";
import { mcdPhaseColors, MCD_PHASES } from "./ipr-constants";
import type { IprTransition } from "@/types";

const phaseLabel = (code?: string | null) =>
  MCD_PHASES.find((p) => p.code === code)?.label ?? code ?? "";

interface IprTransitionPanelProps {
  transitions: IprTransition[];
  loading: boolean;
  selectedTransition: string;
  onSelectTransition: (value: string) => void;
  submitting: boolean;
  onTransition: () => void;
  error: string | null;
  currentPhase?: string;
}

export function IprTransitionPanel({
  transitions,
  loading,
  selectedTransition,
  onSelectTransition,
  submitting,
  onTransition,
  error,
  currentPhase,
}: IprTransitionPanelProps) {
  if (loading) {
    return (
      <div className="rounded-xl border bg-card p-4">
        <div className="h-8 rounded bg-muted animate-pulse" />
      </div>
    );
  }

  if (transitions.length === 0) return null;

  const allowedTransitions = transitions.filter(t => t.allowed);
  const deniedTransitions = transitions.filter(t => !t.allowed);
  const selectedTrans = transitions.find(t => t.id === selectedTransition);
  const isSelectedDenied = selectedTrans && !selectedTrans.allowed;

  // Transitions with gates (phase-crossing) — for quick overview
  const gatedTransitions = allowedTransitions.filter(t => t.gates.length > 0);
  const hasBlockedGates = gatedTransitions.some(t => t.blocked);

  return (
    <div className="rounded-xl border bg-card p-4">
      <h3 className="text-sm font-medium mb-3">Mover a la siguiente etapa</h3>

      {/* Quick gate overview — only when there are phase-crossing transitions */}
      {gatedTransitions.length > 0 && (
        <div className={cn(
          "mb-3 p-2.5 rounded-lg border text-xs",
          hasBlockedGates
            ? "bg-amber-50 border-amber-200 dark:bg-amber-950/30 dark:border-amber-800"
            : "bg-green-50 border-green-200 dark:bg-green-950/30 dark:border-green-800"
        )}>
          <div className="flex flex-wrap gap-x-4 gap-y-1">
            {gatedTransitions.map((t) => {
              const met = t.gates.filter(g => g.met).length;
              const total = t.gates.length;
              const allMet = met === total;
              return (
                <span key={t.id} className="inline-flex items-center gap-1.5">
                  {allMet ? (
                    <ShieldCheck className="size-3.5 text-green-600 shrink-0" />
                  ) : (
                    <ShieldX className="size-3.5 text-red-500 shrink-0" />
                  )}
                  <span className={allMet ? "text-green-700 dark:text-green-300" : "text-red-700 dark:text-red-300"}>
                    {t.label}
                  </span>
                  <span className={cn(
                    "tabular-nums font-medium",
                    allMet ? "text-green-600" : "text-amber-600"
                  )}>
                    {met}/{total}
                  </span>
                </span>
              );
            })}
          </div>
        </div>
      )}

      {allowedTransitions.length === 0 ? (
        <p className="text-xs text-muted-foreground">
          Su rol no tiene permisos para ejecutar transiciones desde este estado.
        </p>
      ) : (
        <div className="flex items-end gap-3 flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <Select value={selectedTransition} onValueChange={onSelectTransition}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Seleccione la acción a realizar..." />
              </SelectTrigger>
              <SelectContent>
                {allowedTransitions.map((t) => (
                  <SelectItem key={t.id} value={t.id} disabled={t.blocked}>
                    <span className="flex items-center gap-2">
                      <span>{t.label}</span>
                      {t.target_phase && (
                        <Badge variant="outline" className={cn("text-[10px] py-0", mcdPhaseColors[t.target_phase] || "")}>
                          {t.target_phase}
                        </Badge>
                      )}
                      {t.phase_change && !t.blocked && (
                        <ChevronRight className="size-3 text-green-600" />
                      )}
                      {t.blocked && (
                        <ShieldX className="size-3 text-red-500" />
                      )}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button
            size="sm"
            disabled={!selectedTransition || submitting || isSelectedDenied}
            onClick={onTransition}
          >
            {submitting && <Loader2 className="size-4 mr-1 animate-spin" />}
            Confirmar avance
          </Button>
        </div>
      )}

      {/* Gate details for selected transition */}
      {selectedTrans && selectedTrans.gates.length > 0 && (
        <div className="mt-3 space-y-1">
          <p className="text-xs font-medium text-muted-foreground">
            Requisitos para pasar de {phaseLabel(currentPhase)} a {phaseLabel(selectedTrans.target_phase)}:
          </p>
          {selectedTrans.gates.map((g) => (
            <div key={g.name} className="flex items-center gap-2 text-xs">
              {g.met ? (
                <ShieldCheck className="size-3.5 text-green-600 shrink-0" />
              ) : (
                <ShieldX className="size-3.5 text-red-500 shrink-0" />
              )}
              <span className={g.met ? "text-muted-foreground" : "text-red-600 font-medium"}>
                {g.detail}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Effects for selected transition */}
      {selectedTrans && selectedTrans.effects && selectedTrans.effects.length > 0 && (
        <div className="mt-3 space-y-1">
          <p className="text-xs font-medium text-blue-600">
            Al transicionar:
          </p>
          {selectedTrans.effects.map((effect, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-blue-700">
              <Info className="size-3.5 shrink-0 mt-0.5" />
              <span>{effect}</span>
            </div>
          ))}
        </div>
      )}

      {/* Show restricted transitions as read-only info */}
      {deniedTransitions.length > 0 && allowedTransitions.length > 0 && (
        <div className="mt-3 pt-3 border-t">
          <p className="text-[11px] text-muted-foreground flex items-center gap-1.5 mb-1">
            <Lock className="size-3 shrink-0" />
            {deniedTransitions.length} {deniedTransitions.length === 1 ? "acción disponible" : "acciones disponibles"} solo para otros roles
          </p>
          <div className="flex flex-wrap gap-1.5">
            {deniedTransitions.map((t) => (
              <Badge key={t.id} variant="outline" className="text-[10px] text-muted-foreground opacity-60">
                {t.label}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {error && (
        <p className="text-xs text-red-600 mt-2">{error}</p>
      )}
    </div>
  );
}
