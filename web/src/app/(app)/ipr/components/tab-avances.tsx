"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { DrawerPanel } from "@/components/drawer-panel";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DateField } from "@/components/date-field";
import { Plus } from "lucide-react";
import { formatDate } from "@/lib/format";
import { EmptyState } from "@/components/empty-state";

interface ProgressReport {
  id: string;
  report_number: number;
  report_date: string;
  physical_progress: number | null;
  financial_progress: number | null;
  description: string | null;
  issues_detected: string | null;
  reported_by_name: string | null;
  created_at: string;
}

interface TabAvancesProps {
  iprId: string;
  canManage: boolean;
}

export function TabAvances({ iprId, canManage }: TabAvancesProps) {
  const [avances, setAvances] = useState<ProgressReport[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [avanceDate, setAvanceDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [avancePhysical, setAvancePhysical] = useState("");
  const [avanceFinancial, setAvanceFinancial] = useState("");
  const [avanceDesc, setAvanceDesc] = useState("");
  const [avanceIssues, setAvanceIssues] = useState("");
  const [avanceSubmitting, setAvanceSubmitting] = useState(false);
  const [avanceError, setAvanceError] = useState<string | null>(null);

  const loadAvances = () => {
    setLoading(true);
    api
      .get<ProgressReport[]>(`/api/ipr/${iprId}/avances`)
      .then(setAvances)
      .catch(() => setAvances(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAvances();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const handleAvanceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!avanceDate) {
      setAvanceError("La fecha es requerida.");
      return;
    }
    setAvanceSubmitting(true);
    setAvanceError(null);
    try {
      await api.post(`/api/ipr/${iprId}/avances`, {
        report_date: avanceDate,
        physical_progress: avancePhysical ? parseFloat(avancePhysical) : null,
        financial_progress: avanceFinancial ? parseFloat(avanceFinancial) : null,
        description: avanceDesc || null,
        issues_detected: avanceIssues || null,
      });
      setShowForm(false);
      setAvanceDate(new Date().toISOString().split("T")[0]);
      setAvancePhysical("");
      setAvanceFinancial("");
      setAvanceDesc("");
      setAvanceIssues("");
      loadAvances();
    } catch (err) {
      setAvanceError(err instanceof Error ? err.message : "Error al registrar avance");
    } finally {
      setAvanceSubmitting(false);
    }
  };

  const avanceColumns = [
    {
      key: "report_number",
      label: "#",
      render: (v: unknown) => <span className="font-mono text-xs">{String(v)}</span>,
    },
    {
      key: "report_date",
      label: "Fecha",
      render: (v: unknown) => <span className="text-xs">{v ? formatDate(String(v)) : "-"}</span>,
    },
    {
      key: "physical_progress",
      label: "% Fisico",
      render: (v: unknown) => (
        <span className="text-xs tabular-nums">{v != null ? `${Number(v).toFixed(1)}%` : "-"}</span>
      ),
    },
    {
      key: "financial_progress",
      label: "% Financiero",
      render: (v: unknown) => (
        <span className="text-xs tabular-nums">{v != null ? `${Number(v).toFixed(1)}%` : "-"}</span>
      ),
    },
    {
      key: "description",
      label: "Descripción",
      render: (v: unknown) => (
        <span className="text-xs line-clamp-1 max-w-xs">{String(v ?? "-")}</span>
      ),
    },
    { key: "reported_by_name", label: "Reportado por" },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {avances ? `${avances.length} reportes de avance` : ""}
        </p>
        {canManage && (
          <Button size="sm" onClick={() => setShowForm(true)}>
            <Plus className="size-4 mr-1" />
            Registrar Avance
          </Button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-12 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !avances || avances.length === 0 ? (
        <EmptyState compact title="No hay reportes de avance para este IPR." />
      ) : (
        <DataTable
          columns={avanceColumns}
          data={avances}
          page={1}
          totalPages={1}
          total={avances.length}
          onPageChange={() => {}}
          isLoading={loading}
        />
      )}

      <DrawerPanel
        open={showForm}
        onClose={() => setShowForm(false)}
        title="Registrar Avance"
      >
        <form onSubmit={handleAvanceSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Fecha del reporte *</label>
            <DateField
              value={avanceDate}
              onChange={(v) => setAvanceDate(v)}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Avance fisico (%)</label>
            <Input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={avancePhysical}
              onChange={(e) => setAvancePhysical(e.target.value)}
              placeholder="0 - 100"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Avance financiero (%)</label>
            <Input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={avanceFinancial}
              onChange={(e) => setAvanceFinancial(e.target.value)}
              placeholder="0 - 100"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripción</label>
            <textarea
              className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={avanceDesc}
              onChange={(e) => setAvanceDesc(e.target.value)}
              placeholder="Descripción del avance..."
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Problemas detectados</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={avanceIssues}
              onChange={(e) => setAvanceIssues(e.target.value)}
              placeholder="Problemas o riesgos detectados..."
            />
          </div>

          {avanceError && (
            <p className="text-sm text-red-600">{avanceError}</p>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={avanceSubmitting}>
              {avanceSubmitting ? "Guardando..." : "Guardar Avance"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowForm(false)}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>
    </div>
  );
}
