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
import { Plus, Building2, Trash2, HardHat, AlertCircle } from "lucide-react";
import { ComboboxAsync, type ComboboxOption } from "@/components/combobox-async";
import { formatDate } from "@/lib/format";
import { EmptyState } from "@/components/empty-state";
import { ConfirmDialog } from "@/components/confirm-dialog";
import type { IprPartyItem, CategoryRef } from "@/types";

interface TabPartesProps {
  iprId: string;
  canManage: boolean;
}

export function TabPartes({ iprId, canManage }: TabPartesProps) {
  const [partes, setPartes] = useState<IprPartyItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [parteOrgId, setParteOrgId] = useState("");
  const [parteRoleId, setParteRoleId] = useState("");
  const [parteRoles, setParteRoles] = useState<CategoryRef[]>([]);
  const [parteSubmitting, setParteSubmitting] = useState(false);
  const [parteError, setParteError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const loadPartes = () => {
    setLoading(true);
    api
      .get<IprPartyItem[]>(`/api/ipr/${iprId}/partes`)
      .then(setPartes)
      .catch(() => setPartes(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadPartes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const openParteForm = () => {
    setParteOrgId("");
    setParteRoleId("");
    setParteError(null);
    setShowForm(true);
    if (parteRoles.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/ipr_party_role").then(setParteRoles).catch(() => {});
    }
  };

  const handleParteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!parteOrgId || !parteRoleId) {
      setParteError("Organización y rol son requeridos.");
      return;
    }
    setParteSubmitting(true);
    setParteError(null);
    try {
      await api.post(`/api/ipr/${iprId}/partes`, {
        organization_id: parteOrgId,
        party_role_id: parteRoleId,
      });
      setShowForm(false);
      loadPartes();
    } catch (err) {
      setParteError(err instanceof Error ? err.message : "Error al agregar parte");
    } finally {
      setParteSubmitting(false);
    }
  };

  const handleDeleteParty = async () => {
    if (!deleteTarget) return;
    try {
      await api.delete(`/api/ipr/${iprId}/partes/${deleteTarget}`);
      loadPartes();
    } catch {
      // silent
    } finally {
      setDeleteTarget(null);
    }
  };

  const searchOrganizations = async (query: string): Promise<ComboboxOption[]> => {
    const data = await api.get<{ id: string; name: string; code: string }[]>(
      `/api/catalogs/organizations?search=${encodeURIComponent(query)}`
    );
    return data.map((o) => ({ value: o.id, label: `${o.name} (${o.code})` }));
  };

  // Find ITO/ITP parties
  const itoParty = partes?.find((p) => p.role_code === "ITO" || p.role_label?.toUpperCase().includes("ITO"));
  const itpParty = partes?.find((p) => p.role_code === "ITP" || p.role_label?.toUpperCase().includes("ITP"));

  const handleAssignIto = () => {
    // Pre-select ITO role in form
    openParteForm();
    // The role will need to be selected manually, but we set the drawer open
  };

  return (
    <div>
      {/* ITO/ITP Highlight Card */}
      {!loading && partes && (
        <div className="mb-4 rounded-lg border bg-card">
          <div className="p-3 space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium">
              <HardHat className="size-4 text-indigo-600" />
              <span>Inspección Técnica</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {itoParty ? (
                <div className="flex items-center gap-2 rounded-md bg-green-50 border border-green-200 px-3 py-2 text-xs">
                  <span className="font-medium text-green-800">ITO:</span>
                  <span className="text-green-700">{itoParty.organization_name}</span>
                  {itoParty.contact_person && (
                    <span className="text-green-600">— {itoParty.contact_person}</span>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-2 rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-xs">
                  <AlertCircle className="size-3.5 text-amber-600 shrink-0" />
                  <span className="text-amber-800">Sin ITO asignado</span>
                  {canManage && (
                    <Button size="sm" variant="outline" className="ml-auto h-6 text-[10px] px-2" onClick={handleAssignIto}>
                      Asignar ITO
                    </Button>
                  )}
                </div>
              )}
              {itpParty ? (
                <div className="flex items-center gap-2 rounded-md bg-green-50 border border-green-200 px-3 py-2 text-xs">
                  <span className="font-medium text-green-800">ITP:</span>
                  <span className="text-green-700">{itpParty.organization_name}</span>
                  {itpParty.contact_person && (
                    <span className="text-green-600">— {itpParty.contact_person}</span>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-2 rounded-md border px-3 py-2 text-xs text-muted-foreground">
                  <span>Sin ITP asignado</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {partes ? `${partes.length} partes involucradas` : ""}
        </p>
        {canManage && (
          <Button size="sm" onClick={openParteForm}>
            <Plus className="size-4 mr-1" />
            Agregar Parte
          </Button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !partes || partes.length === 0 ? (
        <EmptyState compact title="No hay partes registradas para este IPR." />
      ) : (
        <div className="space-y-2">
          {partes.map((p) => (
            <div key={p.id} className="rounded-md border px-4 py-3 text-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Building2 className="size-4 text-muted-foreground" />
                  <span className="font-medium">{p.organization_name}</span>
                  {p.organization_code && (
                    <span className="font-mono text-xs text-muted-foreground">{p.organization_code}</span>
                  )}
                  {p.is_primary && (
                    <Badge variant="default" className="text-xs">Principal</Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">{p.role_label}</Badge>
                  {canManage && (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="size-7 p-0 text-muted-foreground hover:text-red-600"
                      onClick={() => setDeleteTarget(p.id)}
                    >
                      <Trash2 className="size-3.5" />
                    </Button>
                  )}
                </div>
              </div>
              {(p.contact_person || p.contact_email || p.agreement_number) && (
                <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  {p.contact_person && <span>Contacto: {p.contact_person}</span>}
                  {p.contact_email && <span>{p.contact_email}</span>}
                  {p.agreement_number && <span>Convenio: {p.agreement_number}</span>}
                  {p.valid_from && <span>Desde: {formatDate(p.valid_from)}</span>}
                  {p.valid_to && <span>Hasta: {formatDate(p.valid_to)}</span>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <DrawerPanel
        open={showForm}
        onClose={() => setShowForm(false)}
        title="Agregar Parte"
      >
        <form onSubmit={handleParteSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Organización *</label>
            <ComboboxAsync
              value={parteOrgId}
              onChange={setParteOrgId}
              searchFn={searchOrganizations}
              placeholder="Buscar organización..."
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Rol *</label>
            <Select value={parteRoleId} onValueChange={setParteRoleId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione rol" />
              </SelectTrigger>
              <SelectContent>
                {parteRoles.map((r) => (
                  <SelectItem key={r.id} value={r.id}>
                    {r.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {parteError && <p className="text-sm text-red-600">{parteError}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={parteSubmitting}>
              {parteSubmitting ? "Guardando..." : "Agregar Parte"}
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
        title="Eliminar parte"
        description="¿Está seguro de que desea eliminar esta parte del IPR? Esta acción no se puede deshacer."
        onConfirm={handleDeleteParty}
      />
    </div>
  );
}
