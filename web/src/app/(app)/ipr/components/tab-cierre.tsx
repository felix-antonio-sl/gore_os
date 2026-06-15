"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DrawerPanel } from "@/components/drawer-panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { EmptyState } from "@/components/empty-state";
import { DateField } from "@/components/date-field";
import { FileCheck, PenLine, CheckCircle2 } from "lucide-react";
import { formatDate, formatCurrency } from "@/lib/format";

interface ClosureRecord {
  id: string;
  closure_date: string;
  closure_report: string | null;
  physical_completion: number | null;
  financial_completion: number | null;
  final_amount: number | null;
  signed_at: string | null;
  signed_by_name: string | null;
  created_by_name: string;
  closure_act_id: string | null;
  created_at: string;
}

interface TabCierreProps {
  iprId: string;
  canManage: boolean;
  iprStatus?: string;
}

function CompletionBar({ label, value }: { label: string; value: number | null }) {
  if (value == null) return null;
  const pct = Math.min(100, Math.max(0, value));
  const color = pct >= 90 ? "bg-green-500" : pct >= 70 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{value.toFixed(1)}%</span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function TabCierre({ iprId, canManage, iprStatus }: TabCierreProps) {
  const [closure, setClosure] = useState<ClosureRecord | null | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showSignConfirm, setShowSignConfirm] = useState(false);

  // Form state
  const [closureDate, setClosureDate] = useState("");
  const [closureReport, setClosureReport] = useState("");
  const [physical, setPhysical] = useState("");
  const [financial, setFinancial] = useState("");
  const [finalAmount, setFinalAmount] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadClosure = () => {
    setLoading(true);
    api
      .get<ClosureRecord | null>(`/api/ipr/${iprId}/cierre`)
      .then(setClosure)
      .catch(() => setClosure(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadClosure();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const openForm = () => {
    setClosureDate(new Date().toISOString().split("T")[0]);
    setClosureReport("");
    setPhysical("");
    setFinancial("");
    setFinalAmount("");
    setError(null);
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!closureDate) {
      setError("La fecha de cierre es requerida.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.post(`/api/ipr/${iprId}/cierre`, {
        closure_date: closureDate,
        closure_report: closureReport || null,
        physical_completion: physical ? parseFloat(physical) : null,
        financial_completion: financial ? parseFloat(financial) : null,
        final_amount: finalAmount ? parseFloat(finalAmount) : null,
      });
      setShowForm(false);
      loadClosure();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear registro de cierre");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSign = async () => {
    try {
      await api.patch(`/api/ipr/${iprId}/cierre`, { sign: true });
      loadClosure();
    } catch {
      // handled silently — toast could be added
    }
    setShowSignConfirm(false);
  };

  const isClosurePhase = ["EN_RENDICION", "RENDICION_APROBADA", "EN_CIERRE_ADMINISTRATIVO", "CERRADO"].includes(iprStatus ?? "");

  if (loading) {
    return <div className="h-32 rounded-lg bg-muted animate-pulse" />;
  }

  // No closure record yet
  if (!closure) {
    return (
      <div>
        <EmptyState
          compact
          title={
            isClosurePhase
              ? "No se ha creado el acta de cierre para este IPR."
              : "El acta de cierre se habilita en fases F5 (Rendición/Cierre)."
          }
        />
        {canManage && isClosurePhase && (
          <div className="mt-4 flex justify-center">
            <Button onClick={openForm}>
              <PenLine className="size-4 mr-1" />
              Crear Acta de Cierre
            </Button>
          </div>
        )}

        <DrawerPanel open={showForm} onClose={() => setShowForm(false)} title="Crear Acta de Cierre">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fecha de Cierre *</label>
              <DateField
                value={closureDate}
                onChange={(v) => setClosureDate(v)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Avance Físico (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                  value={physical}
                  onChange={(e) => setPhysical(e.target.value)}
                  placeholder="0.0"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Avance Financiero (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                  value={financial}
                  onChange={(e) => setFinancial(e.target.value)}
                  placeholder="0.0"
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Monto Final Ejecutado</label>
              <input
                type="number"
                min="0"
                step="1"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                value={finalAmount}
                onChange={(e) => setFinalAmount(e.target.value)}
                placeholder="0"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Informe de Cierre</label>
              <textarea
                className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={closureReport}
                onChange={(e) => setClosureReport(e.target.value)}
                placeholder="Resumen narrativo del cierre de la inversión..."
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Guardando..." : "Crear Acta"}
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                Cancelar
              </Button>
            </div>
          </form>
        </DrawerPanel>
      </div>
    );
  }

  // Closure record exists — show it
  const isSigned = !!closure.signed_at;

  return (
    <div className="space-y-4">
      <div className={`rounded-xl border p-5 ${isSigned ? "border-green-200 bg-green-50/50 dark:border-green-800 dark:bg-green-950/20" : "border-amber-200 bg-amber-50/50 dark:border-amber-800 dark:bg-amber-950/20"}`}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-2">
            {isSigned ? (
              <CheckCircle2 className="size-5 text-green-600" />
            ) : (
              <FileCheck className="size-5 text-amber-600" />
            )}
            <h3 className="font-semibold text-lg">
              Acta de Cierre
            </h3>
            <Badge variant={isSigned ? "default" : "outline"} className={isSigned ? "bg-green-600" : "border-amber-400 text-amber-700"}>
              {isSigned ? "Firmada" : "Pendiente de Firma"}
            </Badge>
          </div>
          {canManage && !isSigned && (
            <Button size="sm" onClick={() => setShowSignConfirm(true)}>
              <PenLine className="size-4 mr-1" />
              Firmar Cierre
            </Button>
          )}
        </div>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <CompletionBar label="Avance Físico" value={closure.physical_completion} />
          <CompletionBar label="Avance Financiero" value={closure.financial_completion} />
        </div>

        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm">
          <div>
            <span className="text-muted-foreground">Fecha Cierre: </span>
            <span className="font-medium">{formatDate(closure.closure_date)}</span>
          </div>
          {closure.final_amount != null && (
            <div>
              <span className="text-muted-foreground">Monto Final: </span>
              <span className="font-medium">{formatCurrency(closure.final_amount)}</span>
            </div>
          )}
          <div>
            <span className="text-muted-foreground">Creado por: </span>
            <span className="font-medium">{closure.created_by_name}</span>
          </div>
          {isSigned && closure.signed_by_name && (
            <div>
              <span className="text-muted-foreground">Firmado por: </span>
              <span className="font-medium">{closure.signed_by_name}</span>
            </div>
          )}
          {isSigned && closure.signed_at && (
            <div>
              <span className="text-muted-foreground">Fecha Firma: </span>
              <span className="font-medium">{formatDate(closure.signed_at)}</span>
            </div>
          )}
        </div>

        {closure.closure_report && (
          <div className="mt-4">
            <p className="text-xs font-medium text-muted-foreground mb-1">Informe de Cierre</p>
            <p className="text-sm whitespace-pre-wrap">{closure.closure_report}</p>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={showSignConfirm}
        onOpenChange={setShowSignConfirm}
        title="Firmar Acta de Cierre"
        description="Al firmar, el acta de cierre quedará registrada con su nombre y la fecha actual. Esta acción es requisito para transicionar a estado CERRADO."
        onConfirm={handleSign}
        confirmLabel="Firmar"
      />
    </div>
  );
}
