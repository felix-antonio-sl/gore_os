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
import type { ProcessActor } from "@/types";

interface TabActorsProps {
  processId: string;
  canEdit?: boolean;
}

const ACTOR_TYPES = ["ROL", "SISTEMA", "DIVISION"] as const;

const actorTypeBadge: Record<string, string> = {
  ROL: "bg-blue-100 text-blue-800 border-blue-200",
  SISTEMA: "bg-purple-100 text-purple-800 border-purple-200",
  DIVISION: "bg-teal-100 text-teal-800 border-teal-200",
};

export function TabActors({ processId, canEdit = false }: TabActorsProps) {
  const [items, setItems] = useState<ProcessActor[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [actorType, setActorType] = useState("");
  const [actorName, setActorName] = useState("");
  const [laneLabel, setLaneLabel] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .get<ProcessActor[]>(`/api/dgi/processes/${processId}/actors`)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [processId]);

  const resetForm = () => {
    setActorType("");
    setActorName("");
    setLaneLabel("");
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actorName.trim() || !actorType) return;
    setSubmitting(true);
    try {
      await api.post(`/api/dgi/processes/${processId}/actors`, {
        actor_type: actorType,
        actor_name: actorName.trim(),
        lane_label: laneLabel.trim() || null,
      });
      toast.success("Actor agregado");
      resetForm();
      setShowForm(false);
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear actor");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await api.delete(`/api/dgi/processes/${processId}/actors/${deleteId}`);
      toast.success("Actor eliminado");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al eliminar actor");
    } finally {
      setDeleting(false);
      setDeleteId(null);
    }
  };

  const columns = [
    { key: "actor_name", label: "Nombre", className: "text-xs" },
    {
      key: "actor_type",
      label: "Tipo",
      className: "text-xs",
      render: (v: unknown) => {
        const val = String(v ?? "");
        return (
          <Badge variant="outline" className={`text-xs ${actorTypeBadge[val] ?? ""}`}>
            {val}
          </Badge>
        );
      },
    },
    {
      key: "lane_label",
      label: "Carril BPMN",
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
        const r = row as ProcessActor;
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
          <EmptyState compact title="Sin actores registrados" />
          {canEdit && (
            <Button size="sm" onClick={() => setShowForm(true)}>
              <Plus className="size-4 mr-1" />
              Agregar Actor
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
          {items.length} {items.length === 1 ? "actor" : "actores"}
        </p>
        {canEdit && (
          <Button size="sm" onClick={() => { resetForm(); setShowForm(!showForm); }}>
            <Plus className="size-4 mr-1" />
            Agregar Actor
          </Button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-4 rounded-md border p-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo *</label>
              <Select value={actorType} onValueChange={setActorType}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione tipo" />
                </SelectTrigger>
                <SelectContent>
                  {ACTOR_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Nombre *</label>
              <Input
                value={actorName}
                onChange={(e) => setActorName(e.target.value)}
                placeholder="Nombre del actor"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Carril BPMN</label>
              <Input
                value={laneLabel}
                onChange={(e) => setLaneLabel(e.target.value)}
                placeholder="Ej: Lane Finanzas"
              />
            </div>
          </div>
          <div className="flex gap-2 pt-1">
            <Button type="submit" size="sm" disabled={submitting || !actorName.trim() || !actorType}>
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
        title="Eliminar actor"
        description="¿Está seguro de que desea eliminar este actor del proceso? Esta acción no se puede deshacer."
        onConfirm={handleDelete}
        loading={deleting}
      />
    </div>
  );
}
