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
import { Plus, FileEdit } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate, formatCLP } from "@/lib/format";
import { EmptyState } from "@/components/empty-state";
import { ConfirmDialog } from "@/components/confirm-dialog";
import type { CategoryRef } from "@/types";

interface ModificationItem {
  id: string;
  code: string;
  modification_type_code: string;
  modification_type_label: string;
  status_code: string;
  status_label: string;
  description: string;
  justification: string | null;
  field_changed: string | null;
  old_value: string | null;
  new_value: string | null;
  amount_delta: number | null;
  requested_by_name: string;
  approved_by_name: string | null;
  approved_at: string | null;
  created_at: string;
}

interface TabModificacionesProps {
  iprId: string;
  canManage: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  SOLICITADA: "border-l-amber-500",
  EN_REVISION: "border-l-blue-500",
  APROBADA: "border-l-green-500",
  RECHAZADA: "border-l-red-500",
};

const STATUS_BADGE: Record<string, string> = {
  SOLICITADA: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
  EN_REVISION: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  APROBADA: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  RECHAZADA: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
};

export function TabModificaciones({ iprId, canManage }: TabModificacionesProps) {
  const [mods, setMods] = useState<ModificationItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [modTypes, setModTypes] = useState<CategoryRef[]>([]);
  const [modStatuses, setModStatuses] = useState<CategoryRef[]>([]);

  // Form state
  const [typeId, setTypeId] = useState("");
  const [description, setDescription] = useState("");
  const [justification, setJustification] = useState("");
  const [fieldChanged, setFieldChanged] = useState("");
  const [oldValue, setOldValue] = useState("");
  const [newValue, setNewValue] = useState("");
  const [amountDelta, setAmountDelta] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Status transition dialog
  const [transitionMod, setTransitionMod] = useState<{ id: string; action: string } | null>(null);

  const loadMods = () => {
    setLoading(true);
    api
      .get<ModificationItem[]>(`/api/ipr/${iprId}/modificaciones`)
      .then(setMods)
      .catch(() => setMods(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadMods();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const openForm = () => {
    setTypeId("");
    setDescription("");
    setJustification("");
    setFieldChanged("");
    setOldValue("");
    setNewValue("");
    setAmountDelta("");
    setError(null);
    setShowForm(true);
    if (modTypes.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/modification_type").then(setModTypes).catch(() => {});
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!typeId || !description) {
      setError("Tipo y descripción son requeridos.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.post(`/api/ipr/${iprId}/modificaciones`, {
        modification_type_id: typeId,
        description,
        justification: justification || null,
        field_changed: fieldChanged || null,
        old_value: oldValue || null,
        new_value: newValue || null,
        amount_delta: amountDelta ? parseFloat(amountDelta) : null,
      });
      setShowForm(false);
      loadMods();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear modificación");
    } finally {
      setSubmitting(false);
    }
  };

  const handleTransition = async (modId: string, targetCode: string) => {
    if (modStatuses.length === 0) {
      const cats = await api.get<CategoryRef[]>("/api/catalogs/categories/modification_status");
      setModStatuses(cats);
      const target = cats.find((c) => c.code === targetCode);
      if (target) {
        await api.patch(`/api/ipr/${iprId}/modificaciones/${modId}`, { status_id: target.id });
        loadMods();
      }
    } else {
      const target = modStatuses.find((c) => c.code === targetCode);
      if (target) {
        await api.patch(`/api/ipr/${iprId}/modificaciones/${modId}`, { status_id: target.id });
        loadMods();
      }
    }
    setTransitionMod(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {mods ? `${mods.length} modificaciones` : ""}
        </p>
        {canManage && (
          <Button size="sm" onClick={openForm}>
            <Plus className="size-4 mr-1" />
            Nueva Modificación
          </Button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !mods || mods.length === 0 ? (
        <EmptyState compact title="No hay modificaciones registradas para este IPR." />
      ) : (
        <div className="space-y-3">
          {mods.map((m) => (
            <div
              key={m.id}
              className={cn("rounded-md border border-l-4 px-4 py-3 text-sm", STATUS_COLORS[m.status_code] || "border-l-gray-300")}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileEdit className="size-4 text-muted-foreground" />
                  <span className="font-medium">{m.code}</span>
                  <Badge variant="outline" className="text-xs">{m.modification_type_label}</Badge>
                  <Badge variant="secondary" className={cn("text-xs", STATUS_BADGE[m.status_code] || "")}>
                    {m.status_label}
                  </Badge>
                </div>
                <div className="flex items-center gap-1">
                  {canManage && m.status_code === "SOLICITADA" && (
                    <Button size="sm" variant="outline" className="text-xs h-7"
                      onClick={() => setTransitionMod({ id: m.id, action: "EN_REVISION" })}>
                      Revisar
                    </Button>
                  )}
                  {canManage && m.status_code === "EN_REVISION" && (
                    <>
                      <Button size="sm" variant="outline" className="text-xs h-7 text-green-700"
                        onClick={() => setTransitionMod({ id: m.id, action: "APROBADA" })}>
                        Aprobar
                      </Button>
                      <Button size="sm" variant="outline" className="text-xs h-7 text-red-700"
                        onClick={() => setTransitionMod({ id: m.id, action: "RECHAZADA" })}>
                        Rechazar
                      </Button>
                    </>
                  )}
                </div>
              </div>
              <p className="mt-1.5 text-sm">{m.description}</p>
              {m.justification && <p className="mt-1 text-xs text-muted-foreground">Justificación: {m.justification}</p>}
              <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                {m.amount_delta != null && (
                  <span>Delta: {formatCLP(m.amount_delta)}</span>
                )}
                {m.field_changed && <span>Campo: {m.field_changed}</span>}
                <span>Solicitado por: {m.requested_by_name}</span>
                <span>{formatDate(m.created_at)}</span>
                {m.approved_by_name && <span>Aprobado por: {m.approved_by_name}</span>}
              </div>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={!!transitionMod}
        onOpenChange={() => setTransitionMod(null)}
        title={`¿${transitionMod?.action === "APROBADA" ? "Aprobar" : transitionMod?.action === "RECHAZADA" ? "Rechazar" : "Enviar a revisión"} esta modificación?`}
        description="Esta acción cambiará el estado de la modificación."
        onConfirm={() => { if (transitionMod) handleTransition(transitionMod.id, transitionMod.action); }}
        confirmLabel="Confirmar"
      />

      <DrawerPanel open={showForm} onClose={() => setShowForm(false)} title="Nueva Modificación">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Tipo *</label>
            <Select value={typeId} onValueChange={setTypeId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione tipo" />
              </SelectTrigger>
              <SelectContent>
                {modTypes.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripción *</label>
            <textarea
              className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describa la modificación solicitada..."
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Justificación</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="Razón de la modificación..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Campo modificado</label>
              <input
                type="text"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs"
                value={fieldChanged}
                onChange={(e) => setFieldChanged(e.target.value)}
                placeholder="ej: monto_total"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Delta presupuestario</label>
              <input
                type="number"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs"
                value={amountDelta}
                onChange={(e) => setAmountDelta(e.target.value)}
                placeholder="0"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Valor anterior</label>
              <input
                type="text"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs"
                value={oldValue}
                onChange={(e) => setOldValue(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Valor nuevo</label>
              <input
                type="text"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
              />
            </div>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Guardando..." : "Crear Modificación"}
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
