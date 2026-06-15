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
import { ArrowLeft } from "lucide-react";
import { formatDate } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { DGI_ROLES } from "@/types";
import type { BottleneckDetail } from "@/types";

const BOTTLENECK_FSM: Record<string, string[]> = {
  DETECTADO: ["VERIFICADO"],
  VERIFICADO: ["ANALIZADO"],
  ANALIZADO: ["PROPUESTO"],
  PROPUESTO: ["IMPLEMENTADO"],
  IMPLEMENTADO: ["CERRADO"],
};

const STATUS_LABELS: Record<string, string> = {
  DETECTADO: "Detectado",
  VERIFICADO: "Verificado",
  ANALIZADO: "Analizado",
  PROPUESTO: "Propuesto",
  IMPLEMENTADO: "Implementado",
  CERRADO: "Cerrado",
};

const STATUS_COLORS: Record<string, string> = {
  DETECTADO: "bg-slate-50 text-slate-700 border-slate-200",
  VERIFICADO: "bg-blue-50 text-blue-700 border-blue-200",
  ANALIZADO: "bg-cyan-50 text-cyan-700 border-cyan-200",
  PROPUESTO: "bg-amber-50 text-amber-700 border-amber-200",
  IMPLEMENTADO: "bg-green-50 text-green-700 border-green-200",
  CERRADO: "bg-gray-50 text-gray-500 border-gray-200",
};

const DETECTION_TYPE_COLORS: Record<string, string> = {
  ACUMULACION: "bg-purple-50 text-purple-700 border-purple-200",
  CICLO_TIEMPO: "bg-blue-50 text-blue-700 border-blue-200",
  PRESUPUESTO: "bg-amber-50 text-amber-700 border-amber-200",
};

const DETECTION_TYPE_LABELS: Record<string, string> = {
  ACUMULACION: "Acumulación",
  CICLO_TIEMPO: "Ciclo Tiempo",
  PRESUPUESTO: "Presupuesto",
};

const PHASE_ORDER = ["DETECTADO", "VERIFICADO", "ANALIZADO", "PROPUESTO", "IMPLEMENTADO", "CERRADO"];

const INVESTIGATION_FIELDS: { key: keyof BottleneckDetail; label: string; phase: string }[] = [
  { key: "problem", label: "Problema Detectado", phase: "DETECTADO" },
  { key: "verification", label: "Verificación", phase: "VERIFICADO" },
  { key: "root_cause_analysis", label: "Análisis de Causa Raíz", phase: "ANALIZADO" },
  { key: "proposal", label: "Propuesta de Solución", phase: "PROPUESTO" },
  { key: "communication", label: "Comunicación", phase: "IMPLEMENTADO" },
  { key: "follow_up", label: "Seguimiento", phase: "CERRADO" },
];

const isFieldEditable = (fieldPhase: string, currentStatus: string) => {
  if (currentStatus === "CERRADO") return false;
  return PHASE_ORDER.indexOf(currentStatus) >= PHASE_ORDER.indexOf(fieldPhase);
};

export default function BottleneckDetailPage() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
  const id = params.id as string;

  const canEdit = user && DGI_ROLES.includes(user.role_code);

  const [detail, setDetail] = useState<BottleneckDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [transitionTarget, setTransitionTarget] = useState("");
  const [transSubmitting, setTransSubmitting] = useState(false);

  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [savingField, setSavingField] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<BottleneckDetail>(`/api/dgi/data/bottlenecks/${id}`)
      .then((data) => {
        setDetail(data);
        setFieldValues({
          problem: data.problem ?? "",
          verification: data.verification ?? "",
          root_cause_analysis: data.root_cause_analysis ?? "",
          proposal: data.proposal ?? "",
          communication: data.communication ?? "",
          follow_up: data.follow_up ?? "",
        });
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [id]);

  const refreshDetail = () => {
    api
      .get<BottleneckDetail>(`/api/dgi/data/bottlenecks/${id}`)
      .then((data) => {
        setDetail(data);
        setFieldValues({
          problem: data.problem ?? "",
          verification: data.verification ?? "",
          root_cause_analysis: data.root_cause_analysis ?? "",
          proposal: data.proposal ?? "",
          communication: data.communication ?? "",
          follow_up: data.follow_up ?? "",
        });
      })
      .catch(() => {});
  };

  const handleTransition = async () => {
    if (!transitionTarget) return;
    setTransSubmitting(true);
    try {
      await api.patch(`/api/dgi/data/bottlenecks/${id}`, { status: transitionTarget });
      refreshDetail();
      setTransitionTarget("");
      toast.success("Estado actualizado");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al transicionar");
    } finally {
      setTransSubmitting(false);
    }
  };

  const handleSaveField = async (fieldKey: string) => {
    setSavingField(fieldKey);
    try {
      await api.patch(`/api/dgi/data/bottlenecks/${id}`, { [fieldKey]: fieldValues[fieldKey] });
      toast.success("Campo guardado");
      refreshDetail();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setSavingField(null);
    }
  };

  const validTransitions = detail ? (BOTTLENECK_FSM[detail.status] ?? []) : [];

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-40 rounded bg-muted animate-pulse" />
        <div className="h-32 rounded-xl bg-muted animate-pulse" />
        <div className="h-48 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="p-6">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="size-4 mr-2" />
          Volver
        </Button>
        <p className="mt-4 text-muted-foreground">{error ?? "Investigación no encontrada."}</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4 max-w-4xl">
      <Breadcrumb items={buildBreadcrumbs(pathname, detail?.code ?? undefined)} />
      <Button variant="ghost" size="sm" onClick={() => router.back()}>
        <ArrowLeft className="size-4 mr-2" />
        Volver a Cuellos de Botella
      </Button>

      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <span className="font-mono text-xs text-muted-foreground">{detail.code ?? "-"}</span>
          <Badge variant="outline" className={`text-xs ${STATUS_COLORS[detail.status] ?? ""}`}>
            {STATUS_LABELS[detail.status] ?? detail.status}
          </Badge>
          <Badge variant="outline" className={`text-xs ${DETECTION_TYPE_COLORS[detail.detection_type] ?? ""}`}>
            {DETECTION_TYPE_LABELS[detail.detection_type] ?? detail.detection_type}
          </Badge>
        </div>
        {detail.division_name && (
          <h1 className="text-xl font-bold">{detail.division_name}</h1>
        )}
        <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {detail.detection_value !== null && (
            <div>
              <span className="text-muted-foreground">Valor: </span>
              <span className="font-mono font-medium">{detail.detection_value.toLocaleString("es-CL")}</span>
            </div>
          )}
          {detail.detection_threshold !== null && (
            <div>
              <span className="text-muted-foreground">Umbral: </span>
              <span className="font-mono font-medium">{detail.detection_threshold.toLocaleString("es-CL")}</span>
            </div>
          )}
          {detail.created_by_name && (
            <div>
              <span className="text-muted-foreground">Creado por: </span>
              <span className="font-medium">{detail.created_by_name}</span>
            </div>
          )}
          <div>
            <span className="text-muted-foreground">Detectado: </span>
            <span className="font-medium">{formatDate(detail.detected_at)}</span>
          </div>
          {detail.closed_at && (
            <div>
              <span className="text-muted-foreground">Cerrado: </span>
              <span className="font-medium">{formatDate(detail.closed_at)}</span>
            </div>
          )}
          <div>
            <span className="text-muted-foreground">Actualizado: </span>
            <span className="font-medium">{formatDate(detail.updated_at)}</span>
          </div>
        </div>
      </div>

      {canEdit && validTransitions.length > 0 && (
        <div className="rounded-xl border bg-card p-4">
          <h3 className="text-sm font-medium mb-3">Avanzar Estado</h3>
          <div className="flex items-end gap-3 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <Select value={transitionTarget} onValueChange={setTransitionTarget}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Seleccionar estado destino..." />
                </SelectTrigger>
                <SelectContent>
                  {validTransitions.map((s) => (
                    <SelectItem key={s} value={s}>
                      {STATUS_LABELS[s] ?? s}
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
              {transSubmitting ? "Avanzando..." : "Avanzar"}
            </Button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {INVESTIGATION_FIELDS.map((field) => {
          const editable = canEdit && isFieldEditable(field.phase, detail.status);
          const saving = savingField === field.key;
          return (
            <div key={field.key} className="rounded-xl border bg-card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium">{field.label}</h3>
                {editable && <Badge variant="outline" className="text-xs">Editable</Badge>}
              </div>
              <textarea
                value={fieldValues[field.key] ?? ""}
                onChange={(e) =>
                  setFieldValues((prev) => ({ ...prev, [field.key]: e.target.value }))
                }
                disabled={!editable}
                className="w-full min-h-[80px] text-sm rounded-md border border-input bg-background px-3 py-2 resize-y disabled:opacity-50"
              />
              {editable && (
                <Button
                  size="sm"
                  onClick={() => handleSaveField(field.key)}
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
