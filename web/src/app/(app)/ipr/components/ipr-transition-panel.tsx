import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronRight, Loader2, ShieldCheck, ShieldX } from "lucide-react";
import { cn } from "@/lib/utils";
import { mcdPhaseColors } from "./ipr-constants";
import type { IprTransition } from "@/types";

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

  const selectedTrans = transitions.find(t => t.id === selectedTransition);

  return (
    <div className="rounded-xl border bg-card p-4">
      <h3 className="text-sm font-medium mb-3">Avanzar Estado</h3>
      <div className="flex items-end gap-3 flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <Select value={selectedTransition} onValueChange={onSelectTransition}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Seleccionar estado destino..." />
            </SelectTrigger>
            <SelectContent>
              {transitions.map((t) => (
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
          disabled={!selectedTransition || submitting}
          onClick={onTransition}
        >
          {submitting && <Loader2 className="size-4 mr-1 animate-spin" />}
          Transicionar
        </Button>
      </div>
      {selectedTrans && selectedTrans.gates.length > 0 && (
        <div className="mt-3 space-y-1">
          <p className="text-xs font-medium text-muted-foreground">
            Gates para {currentPhase} → {selectedTrans.target_phase}:
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
      {error && (
        <p className="text-xs text-red-600 mt-2">{error}</p>
      )}
    </div>
  );
}
