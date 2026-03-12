"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { toast } from "sonner";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";
import { ArrowLeft, ShieldAlert } from "lucide-react";
import { formatDate, formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { DGI_ROLES } from "@/types";
import type { RiskDetail } from "@/types";

const STATUS_COLORS: Record<string, string> = {
  IDENTIFICADO: "bg-slate-50 text-slate-700 border-slate-200",
  EN_EVALUACION: "bg-blue-50 text-blue-700 border-blue-200",
  EN_MITIGACION: "bg-amber-50 text-amber-700 border-amber-200",
  MITIGADO: "bg-green-50 text-green-700 border-green-200",
  ACEPTADO: "bg-cyan-50 text-cyan-700 border-cyan-200",
  CERRADO: "bg-gray-50 text-gray-500 border-gray-200",
};

const TYPE_COLORS: Record<string, string> = {
  FINANCIERO: "bg-purple-50 text-purple-700 border-purple-200",
  OPERACIONAL: "bg-blue-50 text-blue-700 border-blue-200",
  LEGAL: "bg-red-50 text-red-700 border-red-200",
  REPUTACIONAL: "bg-amber-50 text-amber-700 border-amber-200",
  TECNICO: "bg-cyan-50 text-cyan-700 border-cyan-200",
};

const PROB_COLORS: Record<string, string> = {
  MUY_BAJA: "bg-green-50 text-green-700",
  BAJA: "bg-emerald-50 text-emerald-700",
  MEDIA: "bg-amber-50 text-amber-700",
  ALTA: "bg-orange-50 text-orange-700",
  MUY_ALTA: "bg-red-50 text-red-700",
};

const FSM_STEPS = ["IDENTIFICADO", "EN_EVALUACION", "EN_MITIGACION", "MITIGADO", "ACEPTADO", "CERRADO"];
const FSM_LABELS: Record<string, string> = {
  IDENTIFICADO: "Identificado",
  EN_EVALUACION: "En Evaluación",
  EN_MITIGACION: "En Mitigación",
  MITIGADO: "Mitigado",
  ACEPTADO: "Aceptado",
  CERRADO: "Cerrado",
};

const TRANSITIONS: Record<string, { target: string; label: string }[]> = {
  IDENTIFICADO: [
    { target: "EN_EVALUACION", label: "Iniciar Evaluación" },
    { target: "ACEPTADO", label: "Aceptar Riesgo" },
  ],
  EN_EVALUACION: [
    { target: "EN_MITIGACION", label: "Iniciar Mitigación" },
    { target: "ACEPTADO", label: "Aceptar" },
    { target: "CERRADO", label: "Cerrar" },
  ],
  EN_MITIGACION: [
    { target: "MITIGADO", label: "Marcar Mitigado" },
    { target: "CERRADO", label: "Cerrar" },
  ],
  MITIGADO: [{ target: "CERRADO", label: "Cerrar" }],
  ACEPTADO: [{ target: "CERRADO", label: "Cerrar" }],
  CERRADO: [],
};

const WRITE_ROLES = [...DGI_ROLES, "ADMIN_REGIONAL", "ADMIN_SISTEMA"];

export default function RiesgoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const canEdit = user && WRITE_ROLES.includes(user.role_code);

  const [risk, setRisk] = useState<RiskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [confirmTransition, setConfirmTransition] = useState<string | null>(null);

  const [mitigationPlan, setMitigationPlan] = useState("");

  const fetchRisk = () => {
    setLoading(true);
    api
      .get<RiskDetail>(`/api/risk/${params.id}`)
      .then((data) => {
        setRisk(data);
        setMitigationPlan(data.mitigation_plan || "");
      })
      .catch(() => toast.error("Error al cargar riesgo"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchRisk();
  }, [params.id]);

  const handleSave = async () => {
    if (!risk) return;
    setSaving(true);
    try {
      const updated = await api.patch<RiskDetail>(`/api/risk/${risk.id}`, {
        mitigation_plan: mitigationPlan !== risk.mitigation_plan ? mitigationPlan : undefined,
      });
      setRisk(updated);
      toast.success("Riesgo actualizado");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleTransition = async (target: string) => {
    if (!risk) return;
    setSaving(true);
    try {
      const updated = await api.patch<RiskDetail>(`/api/risk/${risk.id}`, {
        status_id: target,
      });
      setRisk(updated);
      setConfirmTransition(null);
      toast.success(`Estado cambiado a ${FSM_LABELS[target] || target}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error en transición");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-48 bg-muted animate-pulse rounded" />
        <div className="h-64 bg-muted animate-pulse rounded-xl" />
      </div>
    );
  }

  if (!risk) {
    return (
      <div className="p-6">
        <Button variant="ghost" onClick={() => router.push("/riesgos")}>
          <ArrowLeft className="size-4 mr-1" /> Volver
        </Button>
        <p className="mt-4 text-muted-foreground">Riesgo no encontrado</p>
      </div>
    );
  }

  const isClosed = risk.status === "CERRADO";
  const isEditable = canEdit && !isClosed;
  const transitions = TRANSITIONS[risk.status ?? ""] || [];

  // Subject navigation
  const subjectHref = risk.subject_type === "core.ipr"
    ? `/ipr/${risk.subject_id}`
    : risk.subject_type === "core.dgi_process"
      ? `/procesos/${risk.subject_id}`
      : null;

  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-300">
      <Breadcrumb items={buildBreadcrumbs(pathname, risk?.code)} />
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={() => router.push("/riesgos")}>
          <ArrowLeft className="size-4 mr-1" /> Volver
        </Button>
      </div>

      {/* Hero card */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <ShieldAlert className="size-5 text-muted-foreground" />
                <span className="font-mono text-lg font-bold">{risk.code}</span>
                {risk.risk_type && (
                  <Badge variant="outline" className={TYPE_COLORS[risk.risk_type] ?? ""}>
                    {risk.risk_type_label}
                  </Badge>
                )}
                {risk.status && (
                  <Badge variant="outline" className={STATUS_COLORS[risk.status] ?? ""}>
                    {risk.status_label}
                  </Badge>
                )}
              </div>
              <h2 className="text-lg font-semibold">{risk.name}</h2>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                {risk.probability && (
                  <Badge variant="outline" className={`text-xs ${PROB_COLORS[risk.probability] ?? ""}`}>
                    Prob: {risk.probability_label}
                  </Badge>
                )}
                {risk.impact_label && (
                  <Badge variant="outline" className="text-xs">
                    Impacto: {risk.impact_label}
                  </Badge>
                )}
                {risk.subject_label && subjectHref && (
                  <button
                    className="text-blue-600 hover:underline text-sm"
                    onClick={() => router.push(subjectHref)}
                  >
                    {risk.subject_label}
                  </button>
                )}
              </div>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                {risk.identified_at && <span>Identificado: {formatDate(risk.identified_at)}</span>}
                {risk.created_by_name && <span>Creado por: {risk.created_by_name}</span>}
                <span>Creado: {formatDateTime(risk.created_at)}</span>
              </div>
            </div>

            {isEditable && transitions.length > 0 && (
              <div className="flex gap-2">
                {transitions.map((t) => (
                  <Button
                    key={t.target}
                    size="sm"
                    variant={t.target === "CERRADO" ? "outline" : "default"}
                    onClick={() => setConfirmTransition(t.target)}
                    disabled={saving}
                  >
                    {t.label}
                  </Button>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* FSM Stepper */}
      <div className="flex items-center gap-1">
        {FSM_STEPS.map((step, idx) => {
          const currentIdx = FSM_STEPS.indexOf(risk.status ?? "");
          const isCompleted = idx < currentIdx;
          const isCurrent = idx === currentIdx;
          return (
            <div key={step} className="flex items-center gap-1 flex-1">
              <div
                className={`h-2 flex-1 rounded-full ${
                  isCompleted
                    ? "bg-green-500"
                    : isCurrent
                      ? "bg-blue-500"
                      : "bg-muted"
                }`}
              />
              <span
                className={`text-[10px] whitespace-nowrap ${
                  isCurrent ? "font-semibold text-foreground" : "text-muted-foreground"
                }`}
              >
                {FSM_LABELS[step]}
              </span>
            </div>
          );
        })}
      </div>

      {/* Mitigation Plan */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Plan de Mitigación</CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            value={mitigationPlan}
            onChange={(e) => setMitigationPlan(e.target.value)}
            disabled={!isEditable}
            placeholder="Describe las acciones de mitigación..."
            rows={6}
          />
        </CardContent>
      </Card>

      {isEditable && (
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Guardando..." : "Guardar Cambios"}
          </Button>
        </div>
      )}

      <ConfirmDialog
        open={!!confirmTransition}
        onOpenChange={() => setConfirmTransition(null)}
        title={`Cambiar estado a ${FSM_LABELS[confirmTransition ?? ""] ?? confirmTransition}`}
        description="Esta acción cambiará el estado del riesgo. ¿Desea continuar?"
        onConfirm={() => { if (confirmTransition) handleTransition(confirmTransition); }}
        loading={saving}
      />
    </div>
  );
}
