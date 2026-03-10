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
import { Plus, Building2, Trash2 } from "lucide-react";
import { ComboboxAsync, type ComboboxOption } from "@/components/combobox-async";
import { formatDate } from "@/lib/format";
import { EmptyState } from "@/components/empty-state";
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

  const handleDeleteParty = async (partyId: string) => {
    try {
      await api.delete(`/api/ipr/${iprId}/partes/${partyId}`);
      loadPartes();
    } catch {
      // silent
    }
  };

  const searchOrganizations = async (query: string): Promise<ComboboxOption[]> => {
    const data = await api.get<{ id: string; name: string; code: string }[]>(
      `/api/catalogs/organizations?search=${encodeURIComponent(query)}`
    );
    return data.map((o) => ({ value: o.id, label: `${o.name} (${o.code})` }));
  };

  return (
    <div>
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
                      onClick={() => handleDeleteParty(p.id)}
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
    </div>
  );
}
