"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ComboboxAsync } from "@/components/combobox-async";
import { Plus, CheckCircle2, XCircle, ShieldCheck, Trash2 } from "lucide-react";
import { formatDate } from "@/lib/format";
import { toast } from "sonner";
import { EmptyState } from "@/components/empty-state";
import type { KinshipDeclaration, PersonRef } from "@/types";

interface TabParentescoProps {
  iprId: string;
  canManage: boolean;
}

const DECLARATION_TYPES = [
  { value: "EVALUADOR", label: "Evaluador" },
  { value: "REPRESENTANTE_LEGAL", label: "Representante Legal" },
  { value: "PERSONAL_CONTRATADO", label: "Personal Contratado" },
];

const RELATIONSHIP_TYPES = [
  { value: "CONSANGUINIDAD", label: "Consanguinidad" },
  { value: "AFINIDAD", label: "Afinidad" },
];

export function TabParentesco({ iprId, canManage }: TabParentescoProps) {
  const [declarations, setDeclarations] = useState<KinshipDeclaration[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [personId, setPersonId] = useState("");
  const [declType, setDeclType] = useState("");
  const [noConflict, setNoConflict] = useState(true);
  const [authorityId, setAuthorityId] = useState("");
  const [relType, setRelType] = useState("");
  const [relDegree, setRelDegree] = useState("");

  const loadDeclarations = useCallback(() => {
    setLoading(true);
    api
      .get<KinshipDeclaration[]>(`/api/ipr/${iprId}/parentesco`)
      .then(setDeclarations)
      .catch(() => setDeclarations([]))
      .finally(() => setLoading(false));
  }, [iprId]);

  useEffect(() => {
    loadDeclarations();
  }, [loadDeclarations]);

  const searchPersons = async (query: string) => {
    const results = await api.get<PersonRef[]>(
      `/api/catalogs/persons?search=${encodeURIComponent(query)}`
    );
    return results.map((p) => ({
      value: p.id,
      label: `${p.paternal_surname}, ${p.names}${p.rut ? ` (${p.rut})` : ""}`,
    }));
  };

  const searchAuthorities = async (query: string) => {
    const results = await api.get<PersonRef[]>(
      `/api/catalogs/persons?search=${encodeURIComponent(query)}`
    );
    return results.map((p) => ({
      value: p.id,
      label: `${p.paternal_surname}, ${p.names}${p.rut ? ` (${p.rut})` : ""}`,
    }));
  };

  const resetForm = () => {
    setPersonId("");
    setDeclType("");
    setNoConflict(true);
    setAuthorityId("");
    setRelType("");
    setRelDegree("");
    setError(null);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const body: Record<string, unknown> = {
        person_id: personId,
        declaration_type: declType,
        declares_no_conflict: noConflict,
      };
      if (!noConflict) {
        body.related_authority_id = authorityId;
        body.relationship_type = relType;
        body.relationship_degree = parseInt(relDegree);
      }
      await api.post(`/api/ipr/${iprId}/parentesco`, body);
      setShowForm(false);
      resetForm();
      loadDeclarations();
      toast.success("Declaracion registrada");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error al crear declaracion";
      setError(msg);
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleValidate = async (declId: string) => {
    try {
      await api.patch(`/api/ipr/${iprId}/parentesco/${declId}`, { validated: true });
      loadDeclarations();
      toast.success("Declaracion validada");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al validar");
    }
  };

  const handleDelete = async (declId: string) => {
    try {
      await api.delete(`/api/ipr/${iprId}/parentesco/${declId}`);
      loadDeclarations();
      toast.success("Declaracion eliminada");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al eliminar");
    }
  };

  if (loading) return <p className="text-sm text-muted-foreground">Cargando...</p>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">
          Declaraciones de Parentesco ({declarations.length})
        </h3>
        {canManage && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => { setShowForm(!showForm); resetForm(); }}
          >
            <Plus className="h-4 w-4 mr-1" /> Nueva Declaracion
          </Button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="border rounded-lg p-4 space-y-3 bg-muted/30">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium">Persona declarante</label>
              <ComboboxAsync
                value={personId}
                onChange={setPersonId}
                searchFn={searchPersons}
                placeholder="Buscar por RUT o nombre..."
              />
            </div>
            <div>
              <label className="text-xs font-medium">Tipo de declaracion</label>
              <Select value={declType} onValueChange={setDeclType}>
                <SelectTrigger><SelectValue placeholder="Seleccione..." /></SelectTrigger>
                <SelectContent>
                  {DECLARATION_TYPES.map((t) => (
                    <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <label className="text-xs font-medium">Declara ausencia de conflicto?</label>
            <Select
              value={noConflict ? "true" : "false"}
              onValueChange={(v) => setNoConflict(v === "true")}
            >
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="true">Si — Sin conflicto de parentesco</SelectItem>
                <SelectItem value="false">No — Declara parentesco con autoridad</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {!noConflict && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 border-t pt-3">
              <div>
                <label className="text-xs font-medium">Autoridad relacionada</label>
                <ComboboxAsync
                  value={authorityId}
                  onChange={setAuthorityId}
                  searchFn={searchAuthorities}
                  placeholder="Buscar autoridad..."
                />
              </div>
              <div>
                <label className="text-xs font-medium">Tipo de parentesco</label>
                <Select value={relType} onValueChange={setRelType}>
                  <SelectTrigger><SelectValue placeholder="Seleccione..." /></SelectTrigger>
                  <SelectContent>
                    {RELATIONSHIP_TYPES.map((t) => (
                      <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium">Grado (1-4)</label>
                <Select value={relDegree} onValueChange={setRelDegree}>
                  <SelectTrigger><SelectValue placeholder="Grado" /></SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4].map((d) => (
                      <SelectItem key={d} value={String(d)}>{d}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={submitting || !personId || !declType}>
              {submitting ? "Guardando..." : "Guardar"}
            </Button>
            <Button type="button" size="sm" variant="ghost" onClick={() => setShowForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      )}

      {declarations.length === 0 && !showForm && (
        <EmptyState compact title="No hay declaraciones registradas." />
      )}

      <div className="space-y-2">
        {declarations.map((d) => (
          <div key={d.id} className="border rounded-lg p-3 flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                {d.declares_no_conflict ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-600" />
                )}
                <span className="font-medium text-sm">{d.person_name}</span>
                {d.person_rut && (
                  <span className="text-xs text-muted-foreground">({d.person_rut})</span>
                )}
                <Badge variant="outline" className="text-xs">
                  {d.declaration_type}
                </Badge>
              </div>
              {!d.declares_no_conflict && d.related_authority_name && (
                <p className="text-xs text-red-600 ml-6">
                  Parentesco {d.relationship_type?.toLowerCase()} {d.relationship_degree} con{" "}
                  {d.related_authority_name}
                </p>
              )}
              <p className="text-xs text-muted-foreground ml-6">
                Declarado: {formatDate(d.declared_at)}
                {d.validated_at && (
                  <span className="text-green-600 ml-2">
                    Validado: {formatDate(d.validated_at)}
                  </span>
                )}
              </p>
            </div>
            {canManage && (
              <div className="flex gap-1">
                {!d.validated_at && (
                  <Button size="sm" variant="ghost" onClick={() => handleValidate(d.id)} title="Validar">
                    <ShieldCheck className="h-4 w-4" />
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-red-600"
                  onClick={() => handleDelete(d.id)}
                  title="Eliminar"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
