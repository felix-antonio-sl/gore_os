"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";
import { ArrowLeft, Check, Circle } from "lucide-react";
import { formatDate } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { DGI_ROLES } from "@/types";
import type { DGIInitiative, DMAICDetail, DMAICGateResult } from "@/types";

const DMAIC_PHASES = ["DEFINE", "MEASURE", "ANALYZE", "IMPROVE", "VERIFY"] as const;

const PHASE_LABELS: Record<string, string> = {
  DEFINE: "Definir",
  MEASURE: "Medir",
  ANALYZE: "Analizar",
  IMPROVE: "Mejorar",
  VERIFY: "Verificar",
};

const PHASE_COLORS: Record<string, string> = {
  DEFINE: "bg-blue-500",
  MEASURE: "bg-purple-500",
  ANALYZE: "bg-amber-500",
  IMPROVE: "bg-orange-500",
  VERIFY: "bg-green-500",
};

const PHASE_BADGE_COLORS: Record<string, string> = {
  DEFINE: "bg-blue-50 text-blue-700 border-blue-200",
  MEASURE: "bg-purple-50 text-purple-700 border-purple-200",
  ANALYZE: "bg-amber-50 text-amber-700 border-amber-200",
  IMPROVE: "bg-orange-50 text-orange-700 border-orange-200",
  VERIFY: "bg-green-50 text-green-700 border-green-200",
};

const STATUS_COLORS: Record<string, string> = {
  BACKLOG: "bg-slate-50 text-slate-700 border-slate-200",
  EN_CURSO: "bg-blue-50 text-blue-700 border-blue-200",
  REVISION: "bg-amber-50 text-amber-700 border-amber-200",
  COMPLETADO: "bg-green-50 text-green-700 border-green-200",
};

// DMAIC phase fields configuration
const PHASE_FIELDS: Record<string, { key: string; label: string }[]> = {
  define: [
    { key: "problem", label: "Problema" },
    { key: "scope", label: "Alcance" },
    { key: "objectives", label: "Objetivos" },
    { key: "stakeholders", label: "Partes Interesadas" },
    { key: "sponsor", label: "Sponsor" },
  ],
  measure: [
    { key: "baseline_summary", label: "Resumen Línea Base" },
    { key: "measurement_plan", label: "Plan de Medición" },
    { key: "data_sources", label: "Fuentes de Datos" },
  ],
  analyze: [
    { key: "root_causes", label: "Causas Raíz" },
    { key: "analysis_method", label: "Método de Análisis" },
    { key: "prioritized_causes", label: "Causas Priorizadas" },
  ],
  improve: [
    { key: "solution_design", label: "Diseño de Solución" },
    { key: "pilot_plan", label: "Plan Piloto" },
    { key: "pilot_result", label: "Resultado del Piloto" },
    { key: "risk_mitigation", label: "Mitigación de Riesgos" },
  ],
  verify: [
    { key: "verification_plan", label: "Plan de Verificación" },
    { key: "verification_criteria", label: "Criterios de Verificación" },
    { key: "handoff_to", label: "Transferencia a" },
    { key: "lessons_learned", label: "Lecciones Aprendidas" },
  ],
};

function isPhaseEditable(phaseCode: string, currentPhase: string | null): boolean {
  if (!currentPhase) return phaseCode === "DEFINE";
  const currentIdx = DMAIC_PHASES.indexOf(currentPhase as typeof DMAIC_PHASES[number]);
  const phaseIdx = DMAIC_PHASES.indexOf(phaseCode as typeof DMAIC_PHASES[number]);
  if (currentIdx === -1) return phaseCode === "DEFINE";
  return phaseIdx <= currentIdx;
}

export default function InitiativeDMAICPage() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
  const id = params.id as string;

  const canEdit = user && DGI_ROLES.includes(user.role_code);

  const [initiative, setInitiative] = useState<DGIInitiative | null>(null);
  const [dmaic, setDmaic] = useState<DMAICDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Phase transition state
  const [transitionTarget, setTransitionTarget] = useState("");
  const [transSubmitting, setTransSubmitting] = useState(false);

  // Field editing state
  const [fieldValues, setFieldValues] = useState<Record<string, Record<string, string>>>({});
  const [savingPhase, setSavingPhase] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [initiatives, dmaicData] = await Promise.all([
        api.get<DGIInitiative[]>("/api/dgi/initiatives"),
        api.get<DMAICDetail>(`/api/dgi/initiatives/${id}/dmaic`),
      ]);
      const ini = initiatives.find((i) => i.id === id);
      if (!ini) {
        setError("Iniciativa no encontrada");
        return;
      }
      setInitiative(ini);
      setDmaic(dmaicData);

      // Initialize field values from DMAIC phases
      const values: Record<string, Record<string, string>> = {};
      for (const phase of Object.keys(PHASE_FIELDS)) {
        values[phase] = {};
        const phaseData = dmaicData.phases[phase] || {};
        for (const field of PHASE_FIELDS[phase]) {
          values[phase][field.key] = (phaseData[field.key] as string) ?? "";
        }
      }
      setFieldValues(values);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleTransition = async () => {
    if (!transitionTarget) return;
    setTransSubmitting(true);
    try {
      await api.post(`/api/dgi/initiatives/${id}/dmaic/transition`, {
        target_phase: transitionTarget,
      });
      toast.success(`Fase avanzada a ${PHASE_LABELS[transitionTarget] ?? transitionTarget}`);
      setTransitionTarget("");
      await loadData();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al transicionar");
    } finally {
      setTransSubmitting(false);
    }
  };

  const handleSavePhase = async (phase: string) => {
    setSavingPhase(phase);
    try {
      const phaseData = fieldValues[phase] || {};
      // Only send non-empty values
      const payload: Record<string, string> = {};
      for (const [k, v] of Object.entries(phaseData)) {
        if (v.trim()) payload[k] = v.trim();
      }
      await api.patch(`/api/dgi/initiatives/${id}/dmaic/${phase}`, payload);
      toast.success("Guardado correctamente");
      // Refresh dmaic to update gates
      const dmaicData = await api.get<DMAICDetail>(`/api/dgi/initiatives/${id}/dmaic`);
      setDmaic(dmaicData);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setSavingPhase(null);
    }
  };

  // Available transitions: only forward phases
  const availableTransitions = (() => {
    if (!dmaic) return [];
    const current = dmaic.current_phase;
    if (!current) return ["DEFINE"];
    const currentIdx = DMAIC_PHASES.indexOf(current as typeof DMAIC_PHASES[number]);
    if (currentIdx === -1) return ["DEFINE"];
    if (currentIdx >= DMAIC_PHASES.length - 1) return [];
    return [DMAIC_PHASES[currentIdx + 1]];
  })();

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-40 rounded bg-muted animate-pulse" />
        <div className="h-32 rounded-xl bg-muted animate-pulse" />
        <div className="h-48 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (error || !initiative || !dmaic) {
    return (
      <div className="p-6">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="size-4 mr-2" />
          Volver
        </Button>
        <p className="mt-4 text-muted-foreground">{error ?? "Iniciativa no encontrada."}</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4 max-w-4xl animate-in fade-in duration-300">
      <Breadcrumb items={buildBreadcrumbs(pathname, initiative?.code ?? initiative?.name)} />
      {/* Back button */}
      <Button variant="ghost" size="sm" onClick={() => router.push("/tablero")}>
        <ArrowLeft className="size-4 mr-2" />
        Volver al Tablero
      </Button>

      {/* Hero card */}
      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <span className="font-mono text-xs text-muted-foreground">{initiative.code ?? "-"}</span>
          <Badge variant="outline" className={`text-xs ${STATUS_COLORS[initiative.status] ?? ""}`}>
            {initiative.status}
          </Badge>
          {dmaic.current_phase && (
            <Badge variant="outline" className={`text-xs ${PHASE_BADGE_COLORS[dmaic.current_phase] ?? ""}`}>
              {PHASE_LABELS[dmaic.current_phase] ?? dmaic.current_phase}
            </Badge>
          )}
        </div>
        <h1 className="text-xl font-bold">{initiative.name}</h1>
        {initiative.description && (
          <p className="text-sm text-muted-foreground mt-1">{initiative.description}</p>
        )}
        <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {initiative.responsible_name && (
            <div>
              <span className="text-muted-foreground">Responsable: </span>
              <span className="font-medium">{initiative.responsible_name}</span>
            </div>
          )}
          {initiative.division_name && (
            <div>
              <span className="text-muted-foreground">Division: </span>
              <span className="font-medium">{initiative.division_name}</span>
            </div>
          )}
          {initiative.target_date && (
            <div>
              <span className="text-muted-foreground">Objetivo: </span>
              <span className="font-medium">{formatDate(initiative.target_date)}</span>
            </div>
          )}
          <div>
            <span className="text-muted-foreground">Progreso: </span>
            <span className="font-medium">{initiative.progress}%</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3 h-2 w-full rounded-full bg-gray-200 overflow-hidden">
          <div
            className="h-full rounded-full bg-blue-500 transition-all duration-500"
            style={{ width: `${Math.min(initiative.progress, 100)}%` }}
          />
        </div>
      </div>

      {/* DMAIC Stepper */}
      <div className="rounded-xl border bg-card p-4">
        <h3 className="text-sm font-medium mb-4">Fases DMAIC</h3>
        <div className="flex items-center justify-between">
          {DMAIC_PHASES.map((phase, idx) => {
            const currentIdx = dmaic.current_phase
              ? DMAIC_PHASES.indexOf(dmaic.current_phase as typeof DMAIC_PHASES[number])
              : -1;
            const isCompleted = currentIdx >= 0 && idx < currentIdx;
            const isCurrent = idx === currentIdx;
            const gate = dmaic.gates.find((g) => g.phase === phase);

            return (
              <div key={phase} className="flex items-center flex-1">
                <div className="flex flex-col items-center gap-1.5">
                  <div
                    className={`size-8 rounded-full flex items-center justify-center text-xs font-bold ${
                      isCompleted
                        ? `${PHASE_COLORS[phase]} text-white`
                        : isCurrent
                        ? `${PHASE_COLORS[phase]} text-white ring-2 ring-offset-2 ring-${PHASE_COLORS[phase]}`
                        : "bg-gray-200 text-gray-500"
                    }`}
                  >
                    {isCompleted ? (
                      <Check className="size-4" />
                    ) : (
                      phase[0]
                    )}
                  </div>
                  <span className={`text-xs ${isCurrent ? "font-bold" : "text-muted-foreground"}`}>
                    {PHASE_LABELS[phase]}
                  </span>
                  {gate && (
                    <span className={`text-[10px] ${gate.met ? "text-green-600" : "text-amber-600"}`}>
                      {gate.met ? "\u2713" : "\u25CB"}
                    </span>
                  )}
                </div>
                {idx < DMAIC_PHASES.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-2 ${isCompleted ? "bg-blue-400" : "bg-gray-200"}`} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Phase transition */}
      {canEdit && availableTransitions.length > 0 && (
        <div className="rounded-xl border bg-card p-4">
          <h3 className="text-sm font-medium mb-3">Avanzar Fase DMAIC</h3>

          {/* Gate status for current/next phase */}
          <div className="mb-3 space-y-1">
            {dmaic.gates.map((gate) => (
              <div key={gate.phase} className="flex items-center gap-2 text-xs">
                <span className={gate.met ? "text-green-600" : "text-amber-600"}>
                  {gate.met ? "\u2713" : "\u25CB"}
                </span>
                <span className="font-medium">{PHASE_LABELS[gate.phase]}:</span>
                <span className="text-muted-foreground">{gate.detail}</span>
              </div>
            ))}
          </div>

          <div className="flex items-end gap-3 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <Select value={transitionTarget} onValueChange={setTransitionTarget}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Seleccionar fase destino..." />
                </SelectTrigger>
                <SelectContent>
                  {availableTransitions.map((phase) => (
                    <SelectItem key={phase} value={phase}>
                      {PHASE_LABELS[phase] ?? phase}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              size="sm"
              disabled={!transitionTarget || transSubmitting}
              onClick={handleTransition}
            >
              {transSubmitting ? "Avanzando..." : "Avanzar Fase"}
            </Button>
          </div>
        </div>
      )}

      {/* DMAIC Phase Sections */}
      <div className="space-y-3">
        {DMAIC_PHASES.map((phaseCode) => {
          const phaseLower = phaseCode.toLowerCase();
          const fields = PHASE_FIELDS[phaseLower] || [];
          const editable = canEdit && isPhaseEditable(phaseCode, dmaic.current_phase);
          const saving = savingPhase === phaseLower;

          return (
            <div key={phaseCode} className="rounded-xl border bg-card p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`size-6 rounded-full ${PHASE_COLORS[phaseCode]} flex items-center justify-center`}>
                    <span className="text-white text-xs font-bold">{phaseCode[0]}</span>
                  </div>
                  <h3 className="text-sm font-medium">{PHASE_LABELS[phaseCode]}</h3>
                </div>
                {editable && (
                  <Badge variant="outline" className="text-xs">Editable</Badge>
                )}
              </div>

              {fields.map((field) => (
                <div key={field.key} className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">{field.label}</label>
                  <textarea
                    value={fieldValues[phaseLower]?.[field.key] ?? ""}
                    onChange={(e) =>
                      setFieldValues((prev) => ({
                        ...prev,
                        [phaseLower]: { ...prev[phaseLower], [field.key]: e.target.value },
                      }))
                    }
                    disabled={!editable}
                    rows={2}
                    className="w-full text-sm rounded-md border border-input bg-background px-3 py-2 resize-y disabled:opacity-50"
                  />
                </div>
              ))}

              {editable && (
                <Button
                  size="sm"
                  onClick={() => handleSavePhase(phaseLower)}
                  disabled={saving}
                >
                  {saving ? "Guardando..." : "Guardar"}
                </Button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
