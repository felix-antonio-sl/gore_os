"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DrawerPanel } from "@/components/drawer-panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, BarChart3 } from "lucide-react";
import { formatDate } from "@/lib/format";
import { EmptyState } from "@/components/empty-state";
import type { CategoryRef } from "@/types";

interface ExpostEvalItem {
  id: string;
  evaluation_date: string;
  evaluator_name: string;
  eval_type_code: string;
  eval_type_label: string;
  impact_score: number | null;
  sustainability_score: number | null;
  efficiency_score: number | null;
  effectiveness_score: number | null;
  rating_code: string | null;
  rating_label: string | null;
  findings: string | null;
  recommendations: string | null;
  lessons_learned: string | null;
  created_at: string;
}

interface TabEvaluacionExpostProps {
  iprId: string;
  canManage: boolean;
}

const RATING_COLORS: Record<string, string> = {
  EXITOSO: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  SATISFACTORIO: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  PARCIAL: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
  INSATISFACTORIO: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
};

function ScoreBar({ label, value }: { label: string; value: number | null }) {
  if (value == null) return null;
  const pct = Math.min(100, Math.max(0, value));
  const color = pct >= 75 ? "bg-green-500" : pct >= 50 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{value.toFixed(1)}</span>
      </div>
      <div className="h-1.5 rounded-full bg-muted">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function TabEvaluacionExpost({ iprId, canManage }: TabEvaluacionExpostProps) {
  const [evals, setEvals] = useState<ExpostEvalItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [evalTypes, setEvalTypes] = useState<CategoryRef[]>([]);
  const [ratings, setRatings] = useState<CategoryRef[]>([]);

  // Form state
  const [evalDate, setEvalDate] = useState("");
  const [typeId, setTypeId] = useState("");
  const [impact, setImpact] = useState("");
  const [sustainability, setSustainability] = useState("");
  const [efficiency, setEfficiency] = useState("");
  const [effectiveness, setEffectiveness] = useState("");
  const [ratingId, setRatingId] = useState("");
  const [findings, setFindings] = useState("");
  const [recommendations, setRecommendations] = useState("");
  const [lessons, setLessons] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadEvals = () => {
    setLoading(true);
    api
      .get<ExpostEvalItem[]>(`/api/ipr/${iprId}/evaluacion-expost`)
      .then(setEvals)
      .catch(() => setEvals(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEvals();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const openForm = () => {
    setEvalDate(new Date().toISOString().split("T")[0]);
    setTypeId("");
    setImpact("");
    setSustainability("");
    setEfficiency("");
    setEffectiveness("");
    setRatingId("");
    setFindings("");
    setRecommendations("");
    setLessons("");
    setError(null);
    setShowForm(true);
    if (evalTypes.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/expost_eval_type").then(setEvalTypes).catch(() => {});
      api.get<CategoryRef[]>("/api/catalogs/categories/expost_rating").then(setRatings).catch(() => {});
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!typeId || !evalDate) {
      setError("Tipo de evaluación y fecha son requeridos.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.post(`/api/ipr/${iprId}/evaluacion-expost`, {
        evaluation_type_id: typeId,
        evaluation_date: evalDate,
        impact_score: impact ? parseFloat(impact) : null,
        sustainability_score: sustainability ? parseFloat(sustainability) : null,
        efficiency_score: efficiency ? parseFloat(efficiency) : null,
        effectiveness_score: effectiveness ? parseFloat(effectiveness) : null,
        overall_rating_id: ratingId || null,
        findings: findings || null,
        recommendations: recommendations || null,
        lessons_learned: lessons || null,
      });
      setShowForm(false);
      loadEvals();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear evaluación");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {evals ? `${evals.length} evaluaciones ex-post` : ""}
        </p>
        {canManage && (
          <Button size="sm" onClick={openForm}>
            <Plus className="size-4 mr-1" />
            Nueva Evaluación
          </Button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-32 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !evals || evals.length === 0 ? (
        <EmptyState compact title="No hay evaluaciones ex-post para este IPR." />
      ) : (
        <div className="space-y-4">
          {evals.map((ev) => (
            <div key={ev.id} className="rounded-md border px-4 py-3 text-sm space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BarChart3 className="size-4 text-muted-foreground" />
                  <span className="font-medium">{ev.eval_type_label}</span>
                  {ev.rating_label && (
                    <Badge variant="secondary" className={RATING_COLORS[ev.rating_code || ""] || ""}>
                      {ev.rating_label}
                    </Badge>
                  )}
                </div>
                <span className="text-xs text-muted-foreground">{formatDate(ev.evaluation_date)}</span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <ScoreBar label="Impacto" value={ev.impact_score} />
                <ScoreBar label="Sostenibilidad" value={ev.sustainability_score} />
                <ScoreBar label="Eficiencia" value={ev.efficiency_score} />
                <ScoreBar label="Eficacia" value={ev.effectiveness_score} />
              </div>

              {ev.findings && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-0.5">Hallazgos</p>
                  <p className="text-xs">{ev.findings}</p>
                </div>
              )}
              {ev.recommendations && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-0.5">Recomendaciones</p>
                  <p className="text-xs">{ev.recommendations}</p>
                </div>
              )}
              {ev.lessons_learned && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-0.5">Lecciones Aprendidas</p>
                  <p className="text-xs">{ev.lessons_learned}</p>
                </div>
              )}
              <p className="text-xs text-muted-foreground">Evaluador: {ev.evaluator_name}</p>
            </div>
          ))}
        </div>
      )}

      <DrawerPanel open={showForm} onClose={() => setShowForm(false)} title="Nueva Evaluación Ex-Post">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo *</label>
              <Select value={typeId} onValueChange={setTypeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione tipo" />
                </SelectTrigger>
                <SelectContent>
                  {evalTypes.map((t) => (
                    <SelectItem key={t.id} value={t.id}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fecha *</label>
              <input type="date" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm" value={evalDate} onChange={(e) => setEvalDate(e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Impacto (0-100)</label>
              <input type="number" min="0" max="100" step="0.1" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm" value={impact} onChange={(e) => setImpact(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Sostenibilidad (0-100)</label>
              <input type="number" min="0" max="100" step="0.1" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm" value={sustainability} onChange={(e) => setSustainability(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Eficiencia (0-100)</label>
              <input type="number" min="0" max="100" step="0.1" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm" value={efficiency} onChange={(e) => setEfficiency(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Eficacia (0-100)</label>
              <input type="number" min="0" max="100" step="0.1" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm" value={effectiveness} onChange={(e) => setEffectiveness(e.target.value)} />
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Calificación General</label>
            <Select value={ratingId} onValueChange={setRatingId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione calificación" />
              </SelectTrigger>
              <SelectContent>
                {ratings.map((r) => (
                  <SelectItem key={r.id} value={r.id}>{r.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Hallazgos</label>
            <textarea className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm" value={findings} onChange={(e) => setFindings(e.target.value)} placeholder="Hallazgos principales..." />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Recomendaciones</label>
            <textarea className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm" value={recommendations} onChange={(e) => setRecommendations(e.target.value)} placeholder="Recomendaciones..." />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Lecciones Aprendidas</label>
            <textarea className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm" value={lessons} onChange={(e) => setLessons(e.target.value)} placeholder="Lecciones aprendidas..." />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Guardando..." : "Crear Evaluación"}
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancelar</Button>
          </div>
        </form>
      </DrawerPanel>
    </div>
  );
}
