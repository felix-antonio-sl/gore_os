"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DrawerPanel } from "@/components/drawer-panel";
import { Plus, CheckCircle2, Clock, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";
import { EmptyState } from "@/components/empty-state";
import type { EvaluationAssignment, CategoryRef } from "@/types";
import { C33CertificationSection } from "./c33-certification-section";

interface TabEvaluacionesProps {
  iprId: string;
  canManage: boolean;
  mechanismCode?: string | null;
}

export function TabEvaluaciones({ iprId, canManage, mechanismCode }: TabEvaluacionesProps) {
  const [evaluaciones, setEvaluaciones] = useState<EvaluationAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [evaluatorTypes, setEvaluatorTypes] = useState<CategoryRef[]>([]);
  const [formTypeId, setFormTypeId] = useState("");
  const [formName, setFormName] = useState("");
  const [formDeadline, setFormDeadline] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Result registration
  const [editingId, setEditingId] = useState<string | null>(null);
  const [resultTypes, setResultTypes] = useState<CategoryRef[]>([]);
  const [resultId, setResultId] = useState("");
  const [resultObs, setResultObs] = useState("");
  const [resultScore, setResultScore] = useState("");
  const [resultSubmitting, setResultSubmitting] = useState(false);

  const loadEvaluaciones = useCallback(() => {
    setLoading(true);
    api
      .get<EvaluationAssignment[]>(`/api/ipr/${iprId}/evaluaciones`)
      .then(setEvaluaciones)
      .catch(() => setEvaluaciones([]))
      .finally(() => setLoading(false));
  }, [iprId]);

  useEffect(() => {
    loadEvaluaciones();
  }, [loadEvaluaciones]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const body: Record<string, unknown> = {};
      if (formTypeId) body.evaluator_type_id = formTypeId;
      if (formName) body.evaluator_name = formName;
      if (formDeadline) body.deadline_at = new Date(formDeadline).toISOString();
      await api.post(`/api/ipr/${iprId}/evaluaciones`, body);
      setShowForm(false);
      setFormTypeId("");
      setFormName("");
      setFormDeadline("");
      loadEvaluaciones();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear evaluación");
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateResult = async (evalId: string) => {
    setResultSubmitting(true);
    try {
      const body: Record<string, unknown> = {};
      if (resultId) body.result_id = resultId;
      if (resultObs) body.observations = resultObs;
      if (resultScore) body.numeric_score = parseFloat(resultScore);
      body.completed_at = new Date().toISOString();
      await api.patch(`/api/ipr/${iprId}/evaluaciones/${evalId}`, body);
      setEditingId(null);
      setResultId("");
      setResultObs("");
      setResultScore("");
      loadEvaluaciones();
    } catch {
      // silently fail
    } finally {
      setResultSubmitting(false);
    }
  };

  const openForm = async () => {
    setShowForm(true);
    if (evaluatorTypes.length === 0) {
      try {
        const types = await api.get<CategoryRef[]>("/api/catalogs/categories/evaluator_type");
        setEvaluatorTypes(types);
      } catch {
        // types unavailable
      }
    }
  };

  const openResultForm = async (evalId: string) => {
    setEditingId(evalId);
    if (resultTypes.length === 0) {
      try {
        const types = await api.get<CategoryRef[]>("/api/catalogs/categories/evaluation_result");
        setResultTypes(types);
      } catch {
        // types unavailable
      }
    }
  };

  return (
    <div>
      {mechanismCode === "C33" && (
        <div className="mb-4">
          <C33CertificationSection iprId={iprId} />
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {evaluaciones.length > 0 ? `${evaluaciones.length} evaluaciones` : ""}
        </p>
        {canManage && (
          <Button size="sm" onClick={openForm}>
            <Plus className="size-4 mr-1" />
            Asignar Evaluación
          </Button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : evaluaciones.length === 0 ? (
        <EmptyState compact title="No hay evaluaciones asignadas para este IPR." />
      ) : (
        <div className="space-y-3">
          {evaluaciones.map((ev) => (
            <div
              key={ev.id}
              className={cn(
                "rounded-lg border p-3",
                ev.completed_at ? "bg-green-50/50" : "bg-amber-50/50"
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {ev.completed_at ? (
                    <CheckCircle2 className="size-4 text-green-600" />
                  ) : (
                    <Clock className="size-4 text-amber-600" />
                  )}
                  <span className="font-medium text-sm">
                    {ev.evaluator_type_label || ev.evaluator_type}
                  </span>
                  {ev.evaluator_org_name && (
                    <span className="text-xs text-muted-foreground">
                      ({ev.evaluator_org_name})
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {ev.result_code && (
                    <Badge
                      variant="secondary"
                      className={cn(
                        "text-xs",
                        ev.result_code === "RS" || ev.result_code === "RF" || ev.result_code === "ITF"
                          ? "bg-green-100 text-green-800"
                          : ev.result_code === "FI" || ev.result_code === "OT"
                            ? "bg-orange-100 text-orange-800"
                            : "bg-red-100 text-red-800"
                      )}
                    >
                      {ev.result_label || ev.result_code}
                    </Badge>
                  )}
                  {!ev.completed_at && canManage && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs h-7"
                      onClick={() => openResultForm(ev.id)}
                    >
                      Registrar Resultado
                    </Button>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-xs text-muted-foreground">
                <div>
                  <span>Asignado: </span>
                  <span className="text-foreground">{formatDate(ev.assigned_at)}</span>
                </div>
                {ev.deadline_at && (
                  <div>
                    <span>Plazo: </span>
                    <span className="text-foreground">{formatDate(ev.deadline_at)}</span>
                  </div>
                )}
                {ev.completed_at && (
                  <div>
                    <span>Completado: </span>
                    <span className="text-foreground">{formatDate(ev.completed_at)}</span>
                  </div>
                )}
              </div>

              {ev.evaluator_name && (
                <p className="text-xs mt-1 text-muted-foreground">
                  Evaluador: {ev.evaluator_name}
                </p>
              )}

              {ev.numeric_score !== null && ev.numeric_score !== undefined && (
                <p className="text-xs mt-1 text-muted-foreground">
                  Puntaje: <span className="font-medium text-foreground">{ev.numeric_score}</span>
                </p>
              )}

              {ev.rank_position != null && (
                <p className="text-xs mt-1 text-muted-foreground">
                  Ranking: <span className="font-medium text-foreground">
                    {ev.rank_position}{ev.rank_total ? ` / ${ev.rank_total}` : ""}
                  </span>
                  {ev.convocatoria_code && (
                    <span className="ml-2 text-muted-foreground">
                      (Conv. {ev.convocatoria_code})
                    </span>
                  )}
                </p>
              )}

              {ev.observations && (
                <p className="text-xs mt-1 italic">{ev.observations}</p>
              )}

              {/* Inline result form */}
              {editingId === ev.id && (
                <div className="mt-3 pt-3 border-t space-y-2">
                  <div className="grid grid-cols-3 gap-2">
                    <Select value={resultId} onValueChange={setResultId}>
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue placeholder="Resultado..." />
                      </SelectTrigger>
                      <SelectContent>
                        {resultTypes.map((rt) => (
                          <SelectItem key={rt.id} value={rt.id} className="text-xs">
                            {rt.code} — {rt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="100"
                      placeholder="Puntaje..."
                      value={resultScore}
                      onChange={(e) => setResultScore(e.target.value)}
                      className="h-8 text-xs"
                    />
                    <Input
                      placeholder="Observaciones..."
                      value={resultObs}
                      onChange={(e) => setResultObs(e.target.value)}
                      className="h-8 text-xs"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      className="h-7 text-xs"
                      onClick={() => handleUpdateResult(ev.id)}
                      disabled={!resultId || resultSubmitting}
                    >
                      {resultSubmitting ? "Guardando..." : "Guardar Resultado"}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 text-xs"
                      onClick={() => setEditingId(null)}
                    >
                      Cancelar
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create evaluation drawer */}
      <DrawerPanel
        open={showForm}
        onClose={() => setShowForm(false)}
        title="Asignar Evaluación"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Tipo de Evaluador</label>
            <Select value={formTypeId} onValueChange={setFormTypeId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar tipo..." />
              </SelectTrigger>
              <SelectContent>
                {evaluatorTypes.map((et) => (
                  <SelectItem key={et.id} value={et.id}>
                    {et.code} — {et.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Dejar vacío para auto-asignar según mecanismo del IPR
            </p>
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Nombre Evaluador (opcional)</label>
            <Input
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="Nombre de la persona evaluadora"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Plazo (opcional)</label>
            <Input
              type="date"
              value={formDeadline}
              onChange={(e) => setFormDeadline(e.target.value)}
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 text-red-600 text-sm">
              <AlertCircle className="size-4" />
              {error}
            </div>
          )}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Creando..." : "Asignar Evaluación"}
          </Button>
        </form>
      </DrawerPanel>
    </div>
  );
}
