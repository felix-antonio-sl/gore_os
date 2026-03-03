"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DrawerPanel } from "@/components/drawer-panel";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Flag, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";
import type { IprMilestoneItem, CategoryRef } from "@/types";

interface TabHitosProps {
  iprId: string;
  canManage: boolean;
}

export function TabHitos({ iprId, canManage }: TabHitosProps) {
  const [hitos, setHitos] = useState<IprMilestoneItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [hitoTypeId, setHitoTypeId] = useState("");
  const [hitoPlannedDate, setHitoPlannedDate] = useState("");
  const [hitoDesc, setHitoDesc] = useState("");
  const [hitoTypes, setHitoTypes] = useState<CategoryRef[]>([]);
  const [hitoSubmitting, setHitoSubmitting] = useState(false);
  const [hitoError, setHitoError] = useState<string | null>(null);

  const loadHitos = () => {
    setLoading(true);
    api
      .get<IprMilestoneItem[]>(`/api/ipr/${iprId}/hitos`)
      .then(setHitos)
      .catch(() => setHitos(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadHitos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const openHitoForm = () => {
    setHitoTypeId("");
    setHitoPlannedDate("");
    setHitoDesc("");
    setHitoError(null);
    setShowForm(true);
    if (hitoTypes.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/milestone_type").then(setHitoTypes).catch(() => {});
    }
  };

  const handleHitoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!hitoTypeId || !hitoPlannedDate) {
      setHitoError("Tipo de hito y fecha planificada son requeridos.");
      return;
    }
    setHitoSubmitting(true);
    setHitoError(null);
    try {
      await api.post(`/api/ipr/${iprId}/hitos`, {
        milestone_type_id: hitoTypeId,
        planned_date: hitoPlannedDate,
        description: hitoDesc || null,
      });
      setShowForm(false);
      loadHitos();
    } catch (err) {
      setHitoError(err instanceof Error ? err.message : "Error al crear hito");
    } finally {
      setHitoSubmitting(false);
    }
  };

  const handleCompleteHito = async (hitoId: string) => {
    try {
      await api.patch(`/api/ipr/${iprId}/hitos/${hitoId}`, {
        actual_date: new Date().toISOString().split("T")[0],
      });
      loadHitos();
    } catch {
      // silent
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {hitos ? `${hitos.length} hitos` : ""}
        </p>
        {canManage && (
          <Button size="sm" onClick={openHitoForm}>
            <Plus className="size-4 mr-1" />
            Nuevo Hito
          </Button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !hitos || hitos.length === 0 ? (
        <p className="text-sm text-muted-foreground">No hay hitos registrados para este IPR.</p>
      ) : (
        <div className="space-y-3">
          {hitos.map((h) => {
            const today = new Date().toISOString().split("T")[0];
            const isCompleted = !!h.actual_date;
            const isOverdue = !isCompleted && h.planned_date < today;
            const isFuture = !isCompleted && h.planned_date >= today;
            const borderColor = isCompleted
              ? (h.deviation_days != null && h.deviation_days > 0 ? "border-l-amber-500" : "border-l-green-500")
              : isOverdue
              ? "border-l-red-500"
              : "border-l-gray-300";

            return (
              <div
                key={h.id}
                className={cn("rounded-md border border-l-4 px-4 py-3 text-sm", borderColor)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Flag className="size-4 text-muted-foreground" />
                    <span className="font-medium">{h.milestone_type_label}</span>
                    {h.deviation_days != null && (
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-xs",
                          h.deviation_days > 0
                            ? "text-red-600 border-red-200"
                            : h.deviation_days < 0
                            ? "text-green-600 border-green-200"
                            : "text-gray-600"
                        )}
                      >
                        {h.deviation_days > 0
                          ? `+${h.deviation_days}d atraso`
                          : h.deviation_days < 0
                          ? `${h.deviation_days}d adelanto`
                          : "A tiempo"}
                      </Badge>
                    )}
                    {isOverdue && (
                      <Badge variant="outline" className="text-xs text-red-600 border-red-200">
                        Vencido
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {isCompleted ? (
                      <Badge variant="default" className="text-xs bg-green-600">Completado</Badge>
                    ) : canManage ? (
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs h-7"
                        onClick={() => handleCompleteHito(h.id)}
                      >
                        <CheckCircle2 className="size-3.5 mr-1" />
                        Completar
                      </Button>
                    ) : isFuture ? (
                      <Badge variant="outline" className="text-xs">Pendiente</Badge>
                    ) : null}
                  </div>
                </div>
                <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  <span>Planificado: {formatDate(h.planned_date)}</span>
                  {h.actual_date && <span>Completado: {formatDate(h.actual_date)}</span>}
                  {h.completed_by_name && <span>Por: {h.completed_by_name}</span>}
                </div>
                {h.description && (
                  <p className="mt-1 text-xs text-muted-foreground">{h.description}</p>
                )}
                {h.verification_notes && (
                  <p className="mt-1 text-xs italic text-muted-foreground">Notas: {h.verification_notes}</p>
                )}
              </div>
            );
          })}
        </div>
      )}

      <DrawerPanel
        open={showForm}
        onClose={() => setShowForm(false)}
        title="Nuevo Hito"
      >
        <form onSubmit={handleHitoSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Tipo de hito *</label>
            <Select value={hitoTypeId} onValueChange={setHitoTypeId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione tipo" />
              </SelectTrigger>
              <SelectContent>
                {hitoTypes.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Fecha planificada *</label>
            <Input
              type="date"
              value={hitoPlannedDate}
              onChange={(e) => setHitoPlannedDate(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripción</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={hitoDesc}
              onChange={(e) => setHitoDesc(e.target.value)}
              placeholder="Descripción del hito..."
            />
          </div>
          {hitoError && <p className="text-sm text-red-600">{hitoError}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={hitoSubmitting}>
              {hitoSubmitting ? "Guardando..." : "Crear Hito"}
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
