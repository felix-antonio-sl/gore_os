"use client";

import { IprPhaseStepper } from "./ipr-phase-stepper";
import { IprTransitionPanel } from "./ipr-transition-panel";
import { IprHistorySection } from "./ipr-history-section";
import { TrackCard } from "./track-card";
import { Badge } from "@/components/ui/badge";
import { UserCheck } from "lucide-react";
import { formatDate, formatCurrency } from "@/lib/format";
import type { IprDetail } from "./ipr-constants";
import type { IprTransition, TrackInfo, HistoryEntry } from "@/types";

interface TabResumenProps {
  ipr: IprDetail;
  transitions: IprTransition[] | null;
  transLoading: boolean;
  trackInfo: TrackInfo | null;
  history: HistoryEntry[];
  canTransition: boolean;
  selectedTransition: string;
  onSelectTransition: (v: string) => void;
  onTransition: () => void;
  transSubmitting: boolean;
  transError: string | null;
}

export function TabResumen({
  ipr, transitions, transLoading, trackInfo, history,
  canTransition, selectedTransition, onSelectTransition,
  onTransition, transSubmitting, transError,
}: TabResumenProps) {
  return (
    <div className="space-y-4">
      {ipr.current_actor && ipr.current_actor.role_label && (
        <div className="flex items-center gap-3 rounded-lg border bg-card p-3">
          <div className="flex items-center justify-center size-8 rounded-full bg-indigo-100 text-indigo-600 shrink-0">
            <UserCheck className="size-4" />
          </div>
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground">Le toca a</p>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline" className="font-medium text-xs">
                {ipr.current_actor.role_label}
              </Badge>
              <span className="text-sm text-muted-foreground">— {ipr.current_actor.action}</span>
            </div>
          </div>
        </div>
      )}

      {ipr.mcd_phase && (
        <IprPhaseStepper
          currentPhase={ipr.mcd_phase}
          currentPhaseLabel={ipr.mcd_phase_label}
          phaseEnteredAt={ipr.phase_entered_at}
        />
      )}

      {canTransition && (
        <IprTransitionPanel
          transitions={transitions ?? []}
          loading={transLoading}
          selectedTransition={selectedTransition}
          onSelectTransition={onSelectTransition}
          submitting={transSubmitting}
          onTransition={onTransition}
          error={transError}
          currentPhase={ipr.mcd_phase}
        />
      )}

      {trackInfo && trackInfo.mechanism && (
        <TrackCard track={trackInfo} />
      )}

      {history.length > 0 && <IprHistorySection history={history} />}

      <div className="rounded-xl border bg-card p-4">
        <h3 className="text-sm font-medium mb-3">Información General</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
          {ipr.description && (
            <div className="col-span-full">
              <span className="text-muted-foreground text-xs">Descripción</span>
              <p className="mt-0.5">{ipr.description}</p>
            </div>
          )}
          {ipr.total_budget != null && ipr.total_budget > 0 && (
            <div>
              <span className="text-muted-foreground text-xs">Presupuesto total</span>
              <p className="font-medium tabular-nums">{formatCurrency(ipr.total_budget)}</p>
            </div>
          )}
          {ipr.investment_sector && (
            <div>
              <span className="text-muted-foreground text-xs">Sector</span>
              <p>{ipr.investment_sector}</p>
            </div>
          )}
          {ipr.funding_source && (
            <div>
              <span className="text-muted-foreground text-xs">Fuente</span>
              <p>{ipr.fund_category_label || ipr.funding_source}</p>
            </div>
          )}
          {ipr.start_date && (
            <div>
              <span className="text-muted-foreground text-xs">Inicio</span>
              <p>{formatDate(ipr.start_date)}</p>
            </div>
          )}
          {ipr.end_date && (
            <div>
              <span className="text-muted-foreground text-xs">Término</span>
              <p>{formatDate(ipr.end_date)}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
