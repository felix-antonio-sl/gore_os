"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DrawerPanel } from "@/components/drawer-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";

interface SniLevel {
  id: string;
  level_number: number;
  label: string;
  min_utm: number;
  max_utm: number | null;
  evaluator_code: string;
  requires_external_eval: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

function formatUtm(value: number | null) {
  if (value == null) return "Sin límite";
  return `${Number(value).toLocaleString("es-CL")} UTM`;
}

export default function NivelesSniPage() {
  const { user } = useAuth();
  const [levels, setLevels] = useState<SniLevel[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Detail/edit drawer
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selected, setSelected] = useState<SniLevel | null>(null);
  const [editing, setEditing] = useState(false);
  const [editLabel, setEditLabel] = useState("");
  const [editMinUtm, setEditMinUtm] = useState("");
  const [editMaxUtm, setEditMaxUtm] = useState("");
  const [editEvaluator, setEditEvaluator] = useState("");
  const [editExternal, setEditExternal] = useState(false);
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  // Create form
  const [showCreate, setShowCreate] = useState(false);
  const [createNumber, setCreateNumber] = useState("");
  const [createLabel, setCreateLabel] = useState("");
  const [createMinUtm, setCreateMinUtm] = useState("");
  const [createMaxUtm, setCreateMaxUtm] = useState("");
  const [createEvaluator, setCreateEvaluator] = useState("");
  const [createExternal, setCreateExternal] = useState(false);
  const [createSaving, setCreateSaving] = useState(false);

  const loadLevels = () => {
    setIsLoading(true);
    api
      .get<SniLevel[]>("/api/admin/sni-levels")
      .then(setLevels)
      .catch(() => setLevels([]))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadLevels();
  }, []);

  const openDetail = (item: SniLevel) => {
    setSelectedId(item.id);
    setSelected(item);
    setEditing(false);
    setEditError(null);
  };

  const openEdit = () => {
    if (!selected) return;
    setEditLabel(selected.label);
    setEditMinUtm(String(selected.min_utm ?? ""));
    setEditMaxUtm(selected.max_utm != null ? String(selected.max_utm) : "");
    setEditEvaluator(selected.evaluator_code);
    setEditExternal(selected.requires_external_eval);
    setEditError(null);
    setEditing(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId) return;
    setEditSaving(true);
    setEditError(null);
    try {
      const payload: Record<string, unknown> = {};
      if (editLabel && editLabel !== selected?.label) payload.label = editLabel;
      if (editMinUtm) payload.min_utm = parseFloat(editMinUtm);
      if (editMaxUtm) payload.max_utm = parseFloat(editMaxUtm);
      else if (selected?.max_utm != null && !editMaxUtm) payload.max_utm = null;
      if (editEvaluator && editEvaluator !== selected?.evaluator_code) payload.evaluator_code = editEvaluator;
      if (editExternal !== selected?.requires_external_eval) payload.requires_external_eval = editExternal;

      await api.patch(`/api/admin/sni-levels/${selectedId}`, payload);
      toast.success("Nivel SNI actualizado");
      setEditing(false);
      loadLevels();
      const updated = await api.get<SniLevel[]>("/api/admin/sni-levels");
      const fresh = updated.find((l) => l.id === selectedId);
      if (fresh) setSelected(fresh);
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEditSaving(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateSaving(true);
    try {
      await api.post("/api/admin/sni-levels", {
        level_number: parseInt(createNumber),
        label: createLabel,
        min_utm: parseFloat(createMinUtm) || 0,
        max_utm: createMaxUtm ? parseFloat(createMaxUtm) : undefined,
        evaluator_code: createEvaluator,
        requires_external_eval: createExternal,
      });
      toast.success("Nivel SNI creado");
      setShowCreate(false);
      setCreateNumber("");
      setCreateLabel("");
      setCreateMinUtm("");
      setCreateMaxUtm("");
      setCreateEvaluator("");
      setCreateExternal(false);
      loadLevels();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear nivel");
    } finally {
      setCreateSaving(false);
    }
  };

  const handleToggleActive = async () => {
    if (!selectedId || !selected) return;
    try {
      await api.patch(`/api/admin/sni-levels/${selectedId}`, {
        is_active: !selected.is_active,
      });
      toast.success(selected.is_active ? "Nivel desactivado" : "Nivel activado");
      loadLevels();
      setSelected({ ...selected, is_active: !selected.is_active });
    } catch {
      // ignore
    }
  };

  if (!user || user.role_code !== "ADMIN_SISTEMA") {
    return <p className="p-6 text-muted-foreground">Acceso restringido a ADMIN_SISTEMA.</p>;
  }

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Niveles SNI"
        description="Configuración de niveles de evaluación SNI por rango UTM"
        actions={
          <Button size="sm" onClick={() => setShowCreate(!showCreate)}>
            <Plus className="size-4 mr-1" />Nuevo Nivel
          </Button>
        }
      />

      {showCreate && (
        <form onSubmit={handleCreate} className="rounded-lg border p-4 space-y-3">
          <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">Crear Nivel SNI</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-muted-foreground">Número *</label>
              <Input
                type="number"
                min="1"
                value={createNumber}
                onChange={(e) => setCreateNumber(e.target.value)}
                className="h-8 text-sm mt-1"
                required
              />
            </div>
            <div className="sm:col-span-2">
              <label className="text-xs text-muted-foreground">Descripción *</label>
              <Input
                value={createLabel}
                onChange={(e) => setCreateLabel(e.target.value)}
                className="h-8 text-sm mt-1"
                placeholder="Nivel 1 — hasta 2.000 UTM"
                required
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-muted-foreground">Mín. UTM</label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={createMinUtm}
                onChange={(e) => setCreateMinUtm(e.target.value)}
                className="h-8 text-sm font-mono mt-1"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Máx. UTM</label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={createMaxUtm}
                onChange={(e) => setCreateMaxUtm(e.target.value)}
                className="h-8 text-sm font-mono mt-1"
                placeholder="Vacío = sin límite"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Evaluador *</label>
              <Input
                value={createEvaluator}
                onChange={(e) => setCreateEvaluator(e.target.value)}
                className="h-8 text-sm mt-1"
                placeholder="GORE, MDSF..."
                required
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={createExternal}
              onChange={(e) => setCreateExternal(e.target.checked)}
              className="rounded border"
              id="create-external"
            />
            <label htmlFor="create-external" className="text-sm">Requiere evaluación externa</label>
          </div>
          <div className="flex gap-2 pt-1">
            <Button type="submit" size="sm" disabled={createSaving}>
              {createSaving ? "Creando..." : "Crear"}
            </Button>
            <Button type="button" size="sm" variant="outline" onClick={() => setShowCreate(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      )}

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-16">Nivel</TableHead>
              <TableHead>Descripción</TableHead>
              <TableHead>Rango UTM</TableHead>
              <TableHead>Evaluador</TableHead>
              <TableHead>Eval. Externa</TableHead>
              <TableHead>Estado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  Cargando...
                </TableCell>
              </TableRow>
            ) : levels.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  Sin niveles configurados
                </TableCell>
              </TableRow>
            ) : (
              levels.map((l) => (
                <TableRow
                  key={l.id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => openDetail(l)}
                >
                  <TableCell className="font-mono text-sm font-bold">{l.level_number}</TableCell>
                  <TableCell className="text-sm">{l.label}</TableCell>
                  <TableCell className="font-mono text-xs tabular-nums">
                    {formatUtm(l.min_utm)} — {formatUtm(l.max_utm)}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-xs">{l.evaluator_code}</Badge>
                  </TableCell>
                  <TableCell>
                    {l.requires_external_eval ? (
                      <Badge variant="default" className="text-xs">Sí</Badge>
                    ) : (
                      <span className="text-xs text-muted-foreground">No</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={l.is_active ? "default" : "secondary"} className="text-xs">
                      {l.is_active ? "Activo" : "Inactivo"}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <DrawerPanel
        open={!!selectedId}
        onClose={() => setSelectedId(null)}
        title="Detalle Nivel SNI"
      >
        {selected && !editing ? (
          <div className="space-y-4">
            <div>
              <p className="font-mono text-xs text-muted-foreground">Nivel {selected.level_number}</p>
              <p className="font-semibold text-base mt-1">{selected.label}</p>
            </div>

            <div className="rounded-lg border divide-y text-sm">
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Mínimo</span>
                <span className="font-mono">{formatUtm(selected.min_utm)}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Máximo</span>
                <span className="font-mono">{formatUtm(selected.max_utm)}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Evaluador</span>
                <span>{selected.evaluator_code}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Evaluación externa</span>
                <span>{selected.requires_external_eval ? "Sí" : "No"}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Estado</span>
                <Badge variant={selected.is_active ? "default" : "secondary"}>
                  {selected.is_active ? "Activo" : "Inactivo"}
                </Badge>
              </div>
            </div>

            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={openEdit} className="flex-1">
                Editar
              </Button>
              <Button
                size="sm"
                variant={selected.is_active ? "destructive" : "default"}
                onClick={handleToggleActive}
                className="flex-1"
              >
                {selected.is_active ? "Desactivar" : "Activar"}
              </Button>
            </div>
          </div>
        ) : selected && editing ? (
          <form onSubmit={handleSave} className="space-y-3">
            <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">
              Editar Nivel SNI
            </p>
            <div>
              <label className="text-xs text-muted-foreground">Descripción</label>
              <Input
                value={editLabel}
                onChange={(e) => setEditLabel(e.target.value)}
                className="h-8 text-sm mt-1"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted-foreground">Mín. UTM</label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={editMinUtm}
                  onChange={(e) => setEditMinUtm(e.target.value)}
                  className="h-8 text-sm font-mono mt-1"
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground">Máx. UTM</label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={editMaxUtm}
                  onChange={(e) => setEditMaxUtm(e.target.value)}
                  className="h-8 text-sm font-mono mt-1"
                  placeholder="Vacío = sin límite"
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Evaluador</label>
              <Input
                value={editEvaluator}
                onChange={(e) => setEditEvaluator(e.target.value)}
                className="h-8 text-sm mt-1"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={editExternal}
                onChange={(e) => setEditExternal(e.target.checked)}
                className="rounded border"
                id="edit-external"
              />
              <label htmlFor="edit-external" className="text-sm">Requiere evaluación externa</label>
            </div>
            {editError && <p className="text-xs text-red-600">{editError}</p>}
            <div className="flex gap-2 pt-1">
              <Button type="submit" size="sm" disabled={editSaving}>
                {editSaving ? "Guardando..." : "Guardar"}
              </Button>
              <Button type="button" size="sm" variant="outline" onClick={() => setEditing(false)}>
                Cancelar
              </Button>
            </div>
          </form>
        ) : null}
      </DrawerPanel>
    </div>
  );
}
