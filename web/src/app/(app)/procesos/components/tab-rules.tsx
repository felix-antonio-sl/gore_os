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
import type { ProcessRule } from "@/types";

interface TabRulesProps {
  processId: string;
  canEdit?: boolean;
}

const RULE_TYPES = ["NORMATIVA", "NEGOCIO", "OPERACIONAL", "VALIDACION"] as const;

export function TabRules({ processId, canEdit = false }: TabRulesProps) {
  const [items, setItems] = useState<ProcessRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");
  const [ruleType, setRuleType] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .get<ProcessRule[]>(`/api/dgi/processes/${processId}/rules`)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [processId]);

  const resetForm = () => {
    setCode("");
    setDescription("");
    setRuleType("");
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim() || !description.trim() || !ruleType) return;
    setSubmitting(true);
    try {
      await api.post(`/api/dgi/processes/${processId}/rules`, {
        code: code.trim(),
        description: description.trim(),
        rule_type: ruleType,
      });
      toast.success("Regla creada");
      resetForm();
      setShowForm(false);
      load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error al crear regla";
      if (msg.includes("409") || msg.toLowerCase().includes("duplicate") || msg.toLowerCase().includes("ya existe")) {
        toast.error("Código ya existe");
      } else {
        toast.error(msg);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await api.delete(`/api/dgi/processes/${processId}/rules/${deleteId}`);
      toast.success("Regla eliminada");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al eliminar regla");
    } finally {
      setDeleting(false);
      setDeleteId(null);
    }
  };

  const columns = [
    {
      key: "code",
      label: "Código",
      className: "text-xs",
      render: (v: unknown) => (
        <span className="font-mono text-xs">{String(v ?? "")}</span>
      ),
    },
    { key: "description", label: "Descripción", className: "text-xs" },
    {
      key: "rule_type",
      label: "Tipo",
      className: "text-xs",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "")}</Badge>
      ),
    },
    {
      key: "id",
      label: "",
      className: "w-10",
      render: (_: unknown, row: unknown) => {
        if (!canEdit) return null;
        const r = row as ProcessRule;
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
          <EmptyState compact title="Sin reglas registradas" />
          {canEdit && (
            <Button size="sm" onClick={() => setShowForm(true)}>
              <Plus className="size-4 mr-1" />
              Agregar Regla
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
          {items.length} {items.length === 1 ? "regla" : "reglas"}
        </p>
        {canEdit && (
          <Button size="sm" onClick={() => { resetForm(); setShowForm(!showForm); }}>
            <Plus className="size-4 mr-1" />
            Agregar Regla
          </Button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-4 rounded-md border p-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Código *</label>
              <Input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Ej: RN-001"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo *</label>
              <Select value={ruleType} onValueChange={setRuleType}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione tipo" />
                </SelectTrigger>
                <SelectContent>
                  {RULE_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripción *</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Descripción de la regla..."
            />
          </div>
          <div className="flex gap-2 pt-1">
            <Button type="submit" size="sm" disabled={submitting || !code.trim() || !description.trim() || !ruleType}>
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
        title="Eliminar regla"
        description="¿Está seguro de que desea eliminar esta regla del proceso? Esta acción no se puede deshacer."
        onConfirm={handleDelete}
        loading={deleting}
      />
    </div>
  );
}
