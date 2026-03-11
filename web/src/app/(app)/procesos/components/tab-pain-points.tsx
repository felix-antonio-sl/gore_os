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
import { Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { formatDate } from "@/lib/format";
import type { ProcessPainPoint } from "@/types";

interface TabPainPointsProps {
  processId: string;
  canEdit?: boolean;
}

const IMPACT_OPTIONS = ["ALTO", "MEDIO", "BAJO"] as const;

const impactColors: Record<string, string> = {
  ALTO: "bg-red-100 text-red-800 border-red-200",
  MEDIO: "bg-amber-100 text-amber-800 border-amber-200",
  BAJO: "bg-green-100 text-green-800 border-green-200",
};

export function TabPainPoints({ processId, canEdit = false }: TabPainPointsProps) {
  const [items, setItems] = useState<ProcessPainPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [description, setDescription] = useState("");
  const [impact, setImpact] = useState("");
  const [bpmnStage, setBpmnStage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .get<ProcessPainPoint[]>(`/api/dgi/processes/${processId}/pain-points`)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [processId]);

  const resetForm = () => {
    setDescription("");
    setImpact("");
    setBpmnStage("");
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim() || !impact) return;
    setSubmitting(true);
    try {
      await api.post(`/api/dgi/processes/${processId}/pain-points`, {
        description: description.trim(),
        impact,
        bpmn_stage: bpmnStage.trim() || null,
      });
      toast.success("Punto de dolor registrado");
      resetForm();
      setShowForm(false);
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear punto de dolor");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await api.delete(`/api/dgi/processes/${processId}/pain-points/${deleteId}`);
      toast.success("Punto de dolor eliminado");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al eliminar punto de dolor");
    } finally {
      setDeleting(false);
      setDeleteId(null);
    }
  };

  const columns = [
    {
      key: "description",
      label: "Descripción",
      className: "text-xs max-w-xs",
      render: (v: unknown) => (
        <span className="text-xs line-clamp-2">{String(v ?? "")}</span>
      ),
    },
    {
      key: "impact",
      label: "Impacto",
      className: "text-xs",
      render: (v: unknown) => {
        const val = String(v ?? "");
        return (
          <Badge variant="outline" className={`text-xs ${impactColors[val] ?? ""}`}>
            {val}
          </Badge>
        );
      },
    },
    {
      key: "bpmn_stage",
      label: "Etapa BPMN",
      className: "text-xs",
      render: (v: unknown) => (
        <span className="text-xs text-muted-foreground">{String(v ?? "—")}</span>
      ),
    },
    {
      key: "reported_by_name",
      label: "Reportado por",
      className: "text-xs",
      render: (v: unknown) => (
        <span className="text-xs text-muted-foreground">{String(v ?? "—")}</span>
      ),
    },
    {
      key: "created_at",
      label: "Fecha",
      className: "text-xs",
      render: (v: unknown) => (
        <span className="text-xs">{v ? formatDate(String(v)) : "—"}</span>
      ),
    },
    {
      key: "id",
      label: "",
      className: "w-10",
      render: (_: unknown, row: unknown) => {
        if (!canEdit) return null;
        const r = row as ProcessPainPoint;
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
          <EmptyState compact title="Sin puntos de dolor registrados" />
          {canEdit && (
            <Button size="sm" onClick={() => setShowForm(true)}>
              <Plus className="size-4 mr-1" />
              Agregar Punto de Dolor
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {items.length} {items.length === 1 ? "punto de dolor" : "puntos de dolor"}
        </p>
        {canEdit && (
          <Button size="sm" onClick={() => { resetForm(); setShowForm(!showForm); }}>
            <Plus className="size-4 mr-1" />
            Agregar Punto de Dolor
          </Button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-4 rounded-md border p-4 space-y-3">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripción *</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describa el punto de dolor..."
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Impacto *</label>
              <Select value={impact} onValueChange={setImpact}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione impacto" />
                </SelectTrigger>
                <SelectContent>
                  {IMPACT_OPTIONS.map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Etapa BPMN</label>
              <Input
                value={bpmnStage}
                onChange={(e) => setBpmnStage(e.target.value)}
                placeholder="Ej: Revisión documental"
              />
            </div>
          </div>
          <div className="flex gap-2 pt-1">
            <Button type="submit" size="sm" disabled={submitting || !description.trim() || !impact}>
              {submitting ? "Guardando..." : "Agregar"}
            </Button>
            <Button type="button" size="sm" variant="outline" onClick={() => setShowForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
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
        title="Eliminar punto de dolor"
        description="¿Está seguro de que desea eliminar este punto de dolor? Esta acción no se puede deshacer."
        onConfirm={handleDelete}
        loading={deleting}
      />
    </div>
  );
}
