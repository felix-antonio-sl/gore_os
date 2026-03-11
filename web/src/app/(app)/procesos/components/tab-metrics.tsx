"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import { ConfirmDialog } from "@/components/confirm-dialog";
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
import { Plus, Trash2, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { formatDate } from "@/lib/format";
import type { ProcessMetric, MetricComparison } from "@/types";

interface TabMetricsProps {
  processId: string;
  canEdit?: boolean;
}

const MEASUREMENT_TYPES = ["BASELINE", "POST_MEJORA", "PERIODICA"] as const;

export function TabMetrics({ processId, canEdit = false }: TabMetricsProps) {
  const [items, setItems] = useState<ProcessMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [value, setValue] = useState("");
  const [unit, setUnit] = useState("");
  const [measurementType, setMeasurementType] = useState("");
  const [measuredAt, setMeasuredAt] = useState("");
  const [source, setSource] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [comparisons, setComparisons] = useState<MetricComparison[]>([]);
  const [loadingComparison, setLoadingComparison] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .get<ProcessMetric[]>(`/api/dgi/processes/${processId}/metrics`)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  const loadComparison = () => {
    setLoadingComparison(true);
    api
      .get<MetricComparison[]>(`/api/dgi/processes/${processId}/metrics/comparison`)
      .then(setComparisons)
      .catch(() => setComparisons([]))
      .finally(() => setLoadingComparison(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [processId]);

  const resetForm = () => {
    setName("");
    setValue("");
    setUnit("");
    setMeasurementType("");
    setMeasuredAt("");
    setSource("");
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !measurementType) return;
    setSubmitting(true);
    try {
      await api.post(`/api/dgi/processes/${processId}/metrics`, {
        name: name.trim(),
        value: value ? parseFloat(value) : null,
        unit: unit.trim() || null,
        measurement_type: measurementType,
        measured_at: measuredAt || null,
        source: source.trim() || null,
      });
      toast.success("Métrica agregada");
      resetForm();
      setShowForm(false);
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear métrica");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await api.delete(`/api/dgi/processes/${processId}/metrics/${deleteId}`);
      toast.success("Métrica eliminada");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al eliminar métrica");
    } finally {
      setDeleting(false);
      setDeleteId(null);
    }
  };

  const columns = [
    { key: "name", label: "Nombre", className: "text-xs" },
    {
      key: "value",
      label: "Valor",
      className: "text-xs",
      render: (_: unknown, row: unknown) => {
        const r = row as ProcessMetric;
        if (r.value == null) return <span className="text-xs text-muted-foreground">—</span>;
        return <span className="text-xs">{r.value}{r.unit ? ` ${r.unit}` : ""}</span>;
      },
    },
    {
      key: "measurement_type",
      label: "Tipo",
      className: "text-xs",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "")}</Badge>
      ),
    },
    {
      key: "measured_at",
      label: "Fecha",
      className: "text-xs",
      render: (v: unknown) => (
        <span className="text-xs">{v ? formatDate(String(v)) : "—"}</span>
      ),
    },
    {
      key: "source",
      label: "Fuente",
      className: "text-xs",
      render: (v: unknown) => (
        <span className="text-xs text-muted-foreground">{String(v ?? "—")}</span>
      ),
    },
    {
      key: "id",
      label: "",
      className: "w-10",
      render: (_: unknown, row: unknown) => {
        if (!canEdit) return null;
        const r = row as ProcessMetric;
        return (
          <Button
            size="sm"
            variant="ghost"
            className="size-7 p-0 text-muted-foreground hover:text-red-600"
            onClick={() => setDeleteId(r.id)}
          >
            <Trash2 className="size-3.5" />
          </Button>
        );
      },
    },
  ];

  if (!loading && items.length === 0 && !showForm) {
    return (
      <div>
        <div className="flex items-center justify-between mb-4">
          <EmptyState compact title="Sin métricas registradas" />
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant={showComparison ? "secondary" : "outline"}
              onClick={() => {
                const next = !showComparison;
                setShowComparison(next);
                if (next) loadComparison();
              }}
            >
              <ArrowRight className="size-4 mr-1" />
              Comparar
            </Button>
            {canEdit && (
              <Button size="sm" onClick={() => setShowForm(true)}>
                <Plus className="size-4 mr-1" />
                Agregar Métrica
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {items.length} {items.length === 1 ? "métrica" : "métricas"}
        </p>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={showComparison ? "secondary" : "outline"}
            onClick={() => {
              const next = !showComparison;
              setShowComparison(next);
              if (next) loadComparison();
            }}
          >
            <ArrowRight className="size-4 mr-1" />
            Comparar
          </Button>
          {canEdit && (
            <Button size="sm" onClick={() => { resetForm(); setShowForm(!showForm); }}>
              <Plus className="size-4 mr-1" />
              Agregar Métrica
            </Button>
          )}
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-4 rounded-md border p-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Nombre *</label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ej: Tiempo de ciclo"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Valor</label>
              <Input
                type="number"
                step="any"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Ej: 15.5"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Unidad</label>
              <Input
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                placeholder="Ej: días, hrs, %"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo *</label>
              <Select value={measurementType} onValueChange={setMeasurementType}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione tipo" />
                </SelectTrigger>
                <SelectContent>
                  {MEASUREMENT_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fecha medición</label>
              <Input
                type="date"
                value={measuredAt}
                onChange={(e) => setMeasuredAt(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fuente</label>
              <Input
                value={source}
                onChange={(e) => setSource(e.target.value)}
                placeholder="Ej: SIGFE, manual"
              />
            </div>
          </div>
          <div className="flex gap-2 pt-1">
            <Button type="submit" size="sm" disabled={submitting || !name.trim() || !measurementType}>
              {submitting ? "Guardando..." : "Agregar"}
            </Button>
            <Button type="button" size="sm" variant="outline" onClick={() => setShowForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      )}

      {showComparison && (
        <div className="mb-4 rounded-md border p-4 space-y-2">
          <h4 className="text-sm font-medium">Comparacion Antes/Despues</h4>
          {loadingComparison ? (
            <div className="h-20 bg-muted animate-pulse rounded" />
          ) : comparisons.length === 0 ? (
            <p className="text-xs text-muted-foreground">Sin metricas BASELINE y POST_MEJORA para comparar.</p>
          ) : (
            <div className="space-y-2">
              {comparisons.map((c) => (
                <div key={c.name} className="flex items-center gap-3 text-sm py-1.5 px-2 rounded hover:bg-muted/50">
                  <span className="flex-1 font-medium">{c.name}</span>
                  <span className="text-muted-foreground font-mono">
                    {c.baseline_value !== null ? c.baseline_value : "\u2014"}
                  </span>
                  <ArrowRight className="size-3 text-muted-foreground" />
                  <span className="font-mono font-medium">
                    {c.post_mejora_value !== null ? c.post_mejora_value : "\u2014"}
                  </span>
                  {c.unit && <span className="text-xs text-muted-foreground">{c.unit}</span>}
                  {c.delta !== null && (
                    <Badge
                      variant="outline"
                      className={`text-xs ${c.improved ? "bg-green-50 text-green-700 border-green-200" : "bg-red-50 text-red-700 border-red-200"}`}
                    >
                      {c.delta > 0 ? "+" : ""}{c.delta}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <DataTable
        columns={columns}
        data={items}
        page={1}
        totalPages={1}
        total={items.length}
        onPageChange={() => {}}
        isLoading={loading}
      />

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => { if (!open) setDeleteId(null); }}
        title="Eliminar métrica"
        description="¿Está seguro de que desea eliminar esta métrica del proceso? Esta acción no se puede deshacer."
        onConfirm={handleDelete}
        loading={deleting}
      />
    </div>
  );
}
