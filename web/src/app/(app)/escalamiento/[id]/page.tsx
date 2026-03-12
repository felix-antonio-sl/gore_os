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
import { ArrowLeft, Clock, Shield } from "lucide-react";
import { formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import type { Escalation } from "@/types";

const LEVEL_COLORS: Record<string, string> = {
  NIVEL_1: "bg-blue-50 text-blue-700 border-blue-200",
  NIVEL_2: "bg-amber-50 text-amber-700 border-amber-200",
  NIVEL_3: "bg-orange-50 text-orange-700 border-orange-200",
  NIVEL_4: "bg-red-50 text-red-700 border-red-200",
};

const STATUS_COLORS: Record<string, string> = {
  ABIERTO: "bg-slate-50 text-slate-700 border-slate-200",
  EN_GESTION: "bg-blue-50 text-blue-700 border-blue-200",
  RESUELTO: "bg-green-50 text-green-700 border-green-200",
  CERRADO: "bg-gray-50 text-gray-500 border-gray-200",
};

const FSM_STEPS = ["ABIERTO", "EN_GESTION", "RESUELTO", "CERRADO"];
const FSM_LABELS: Record<string, string> = {
  ABIERTO: "Abierto",
  EN_GESTION: "En Gestión",
  RESUELTO: "Resuelto",
  CERRADO: "Cerrado",
};

const TRANSITIONS: Record<string, { target: string; label: string }[]> = {
  ABIERTO: [
    { target: "EN_GESTION", label: "Iniciar Gestión" },
    { target: "CERRADO", label: "Cerrar" },
  ],
  EN_GESTION: [
    { target: "RESUELTO", label: "Marcar Resuelto" },
    { target: "CERRADO", label: "Cerrar" },
  ],
  RESUELTO: [{ target: "CERRADO", label: "Cerrar" }],
  CERRADO: [],
};

export default function EscalamientoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const canEdit =
    user && ["JEFE_DGI", "ESP_CONTROL_GESTION"].includes(user.role_code);

  const [esc, setEsc] = useState<Escalation | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [confirmTransition, setConfirmTransition] = useState<string | null>(null);

  // Editable fields
  const [situation, setSituation] = useState("");
  const [impact, setImpact] = useState("");
  const [recommendation, setRecommendation] = useState("");
  const [resolvedDescription, setResolvedDescription] = useState("");

  const fetchEsc = () => {
    setLoading(true);
    api
      .get<Escalation>(`/api/dgi/escalations/${params.id}`)
      .then((data) => {
        setEsc(data);
        setSituation(data.situation || "");
        setImpact(data.impact || "");
        setRecommendation(data.recommendation || "");
        setResolvedDescription(data.resolved_description || "");
      })
      .catch(() => toast.error("Error al cargar escalamiento"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchEsc();
  }, [params.id]);

  const handleSave = async () => {
    if (!esc) return;
    setSaving(true);
    try {
      const updated = await api.patch<Escalation>(
        `/api/dgi/escalations/${esc.id}`,
        {
          situation: situation !== esc.situation ? situation : undefined,
          impact: impact !== esc.impact ? impact : undefined,
          recommendation:
            recommendation !== esc.recommendation ? recommendation : undefined,
          resolved_description:
            resolvedDescription !== esc.resolved_description
              ? resolvedDescription
              : undefined,
        }
      );
      setEsc(updated);
      toast.success("Escalamiento actualizado");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleTransition = async (target: string) => {
    if (!esc) return;
    setSaving(true);
    try {
      const updated = await api.patch<Escalation>(
        `/api/dgi/escalations/${esc.id}`,
        { status: target }
      );
      setEsc(updated);
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

  if (!esc) {
    return (
      <div className="p-6">
        <Button variant="ghost" onClick={() => router.push("/escalamiento")}>
          <ArrowLeft className="size-4 mr-1" /> Volver
        </Button>
        <p className="mt-4 text-muted-foreground">Escalamiento no encontrado</p>
      </div>
    );
  }

  const isClosed = esc.status === "CERRADO";
  const isEditable = canEdit && !isClosed;
  const showResolution = esc.status === "RESUELTO" || esc.status === "CERRADO";
  const transitions = TRANSITIONS[esc.status] || [];

  // Deadline countdown
  let deadlineInfo: { text: string; color: string } | null = null;
  if (esc.deadline) {
    const dl = new Date(esc.deadline);
    const now = new Date();
    const hoursLeft = (dl.getTime() - now.getTime()) / (1000 * 60 * 60);
    if (hoursLeft < 0) {
      deadlineInfo = { text: `Vencido hace ${Math.abs(Math.round(hoursLeft))}h`, color: "text-red-600" };
    } else if (hoursLeft < 4) {
      deadlineInfo = { text: `${Math.round(hoursLeft)}h restantes`, color: "text-red-600" };
    } else if (hoursLeft < 24) {
      deadlineInfo = { text: `${Math.round(hoursLeft)}h restantes`, color: "text-amber-600" };
    } else {
      deadlineInfo = { text: `${Math.round(hoursLeft / 24)}d restantes`, color: "text-green-600" };
    }
  }

  return (
    <div className="p-6 space-y-6">
      <Breadcrumb items={buildBreadcrumbs(pathname, esc?.code)} />
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={() => router.push("/escalamiento")}>
          <ArrowLeft className="size-4 mr-1" /> Volver
        </Button>
      </div>

      {/* Hero card */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-lg font-bold">{esc.code}</span>
                <Badge variant="outline" className={LEVEL_COLORS[esc.level] ?? ""}>
                  {esc.level_label}
                </Badge>
                <Badge variant="outline" className={STATUS_COLORS[esc.status] ?? ""}>
                  {esc.status_label}
                </Badge>
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>
                  <Shield className="size-3.5 inline mr-1" />
                  Escalado a: <strong>{esc.escalated_to ?? "-"}</strong>
                </span>
                {deadlineInfo && (
                  <span className={deadlineInfo.color}>
                    <Clock className="size-3.5 inline mr-1" />
                    {deadlineInfo.text}
                  </span>
                )}
                <span>Creado: {formatDateTime(esc.created_at)}</span>
              </div>
            </div>

            {/* Transition buttons */}
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
          const currentIdx = FSM_STEPS.indexOf(esc.status);
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
                className={`text-xs whitespace-nowrap ${
                  isCurrent ? "font-semibold text-foreground" : "text-muted-foreground"
                }`}
              >
                {FSM_LABELS[step]}
              </span>
            </div>
          );
        })}
      </div>

      {/* Editable sections */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Situación</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={situation}
              onChange={(e) => setSituation(e.target.value)}
              disabled={!isEditable}
              rows={4}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Impacto</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={impact}
              onChange={(e) => setImpact(e.target.value)}
              disabled={!isEditable}
              rows={4}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recomendación</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={recommendation}
              onChange={(e) => setRecommendation(e.target.value)}
              disabled={!isEditable}
              rows={4}
            />
          </CardContent>
        </Card>

        {showResolution && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Resolución</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={resolvedDescription}
                onChange={(e) => setResolvedDescription(e.target.value)}
                disabled={!isEditable}
                placeholder="Descripción de la resolución"
                rows={4}
              />
              {esc.resolved_at && (
                <p className="text-xs text-muted-foreground mt-2">
                  Resuelto: {formatDateTime(esc.resolved_at)}
                </p>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {isEditable && (
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Guardando..." : "Guardar Cambios"}
          </Button>
        </div>
      )}

      {/* Confirm transition dialog */}
      <ConfirmDialog
        open={!!confirmTransition}
        onOpenChange={() => setConfirmTransition(null)}
        title={`Cambiar estado a ${FSM_LABELS[confirmTransition ?? ""] ?? confirmTransition}`}
        description="Esta acción cambiará el estado del escalamiento. ¿Desea continuar?"
        onConfirm={() => { if (confirmTransition) handleTransition(confirmTransition); }}
        loading={saving}
      />
    </div>
  );
}
