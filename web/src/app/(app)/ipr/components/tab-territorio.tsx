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
import { Plus, MapPin, Trash2 } from "lucide-react";
import { EmptyState } from "@/components/empty-state";
import { ConfirmDialog } from "@/components/confirm-dialog";
import type { IprTerritoryItem, CategoryRef, TerritoryOption } from "@/types";

interface TabTerritorioProps {
  iprId: string;
  canManage: boolean;
}

export function TabTerritorio({ iprId, canManage }: TabTerritorioProps) {
  const [territorios, setTerritorios] = useState<IprTerritoryItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [terrTerritoryId, setTerrTerritoryId] = useState("");
  const [terrImpactId, setTerrImpactId] = useState("");
  const [terrOptions, setTerrOptions] = useState<TerritoryOption[]>([]);
  const [terrImpactTypes, setTerrImpactTypes] = useState<CategoryRef[]>([]);
  const [terrSubmitting, setTerrSubmitting] = useState(false);
  const [terrError, setTerrError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const loadTerritorios = () => {
    setLoading(true);
    api
      .get<IprTerritoryItem[]>(`/api/ipr/${iprId}/territorio`)
      .then(setTerritorios)
      .catch(() => setTerritorios(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTerritorios();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const openTerrForm = () => {
    setTerrTerritoryId("");
    setTerrImpactId("");
    setTerrError(null);
    setShowForm(true);
    if (terrOptions.length === 0) {
      api.get<TerritoryOption[]>("/api/catalogs/territories").then(setTerrOptions).catch(() => {});
    }
    if (terrImpactTypes.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/territory_impact").then(setTerrImpactTypes).catch(() => {});
    }
  };

  const handleTerrSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!terrTerritoryId || !terrImpactId) {
      setTerrError("Territorio y tipo de impacto son requeridos.");
      return;
    }
    setTerrSubmitting(true);
    setTerrError(null);
    try {
      await api.post(`/api/ipr/${iprId}/territorio`, {
        territory_id: terrTerritoryId,
        impact_type_id: terrImpactId,
      });
      setShowForm(false);
      loadTerritorios();
    } catch (err) {
      setTerrError(err instanceof Error ? err.message : "Error al agregar territorio");
    } finally {
      setTerrSubmitting(false);
    }
  };

  const handleDeleteTerritory = async () => {
    if (!deleteTarget) return;
    try {
      await api.delete(`/api/ipr/${iprId}/territorio/${deleteTarget}`);
      loadTerritorios();
    } catch {
      // silent
    } finally {
      setDeleteTarget(null);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {territorios ? `${territorios.length} territorios vinculados` : ""}
        </p>
        {canManage && (
          <Button size="sm" onClick={openTerrForm}>
            <Plus className="size-4 mr-1" />
            Agregar Territorio
          </Button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !territorios || territorios.length === 0 ? (
        <EmptyState compact title="No hay territorios vinculados a este IPR." />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {territorios.map((t) => (
            <div key={t.id} className="rounded-lg border p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <MapPin className="size-4 text-muted-foreground shrink-0" />
                  <div>
                    <p className="font-medium text-sm">{t.territory_name}</p>
                    {t.territory_code && (
                      <p className="text-xs text-muted-foreground font-mono">{t.territory_code}</p>
                    )}
                  </div>
                </div>
                {canManage && (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="size-7 p-0 text-muted-foreground hover:text-red-600"
                    onClick={() => setDeleteTarget(t.id)}
                  >
                    <Trash2 className="size-3.5" />
                  </Button>
                )}
              </div>
              <div className="mt-2 flex items-center gap-2">
                <Badge variant="outline" className="text-xs">{t.impact_type_label}</Badge>
                {t.is_primary && <Badge variant="default" className="text-xs">Principal</Badge>}
              </div>
              {t.notes && <p className="mt-2 text-xs text-muted-foreground">{t.notes}</p>}
            </div>
          ))}
        </div>
      )}

      <DrawerPanel
        open={showForm}
        onClose={() => setShowForm(false)}
        title="Agregar Territorio"
      >
        <form onSubmit={handleTerrSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Territorio *</label>
            <Select value={terrTerritoryId} onValueChange={setTerrTerritoryId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione territorio" />
              </SelectTrigger>
              <SelectContent>
                {terrOptions.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.name} ({t.territory_type})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Tipo de impacto *</label>
            <Select value={terrImpactId} onValueChange={setTerrImpactId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione tipo de impacto" />
              </SelectTrigger>
              <SelectContent>
                {terrImpactTypes.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {terrError && <p className="text-sm text-red-600">{terrError}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={terrSubmitting}>
              {terrSubmitting ? "Guardando..." : "Agregar Territorio"}
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => { if (!open) setDeleteTarget(null); }}
        title="Eliminar territorio"
        description="¿Está seguro de que desea eliminar este registro territorial? Esta acción no se puede deshacer."
        onConfirm={handleDeleteTerritory}
      />
    </div>
  );
}
