"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { DrawerPanel } from "@/components/drawer-panel";
import { ConfirmDialog } from "@/components/confirm-dialog";
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
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { formatCLPExact } from "@/lib/format";
import { Plus, ExternalLink, ChevronDown, ChevronRight } from "lucide-react";

// ---------------------------------------------------------------------------
// Umbrales Types & Helpers
// ---------------------------------------------------------------------------

interface ThresholdItem {
  id: string;
  code: string;
  label: string;
  value_utm: number | null;
  value_pct: number | null;
  enforcement_point: string;
  source_normativa: string | null;
  applies_to_track: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const ENFORCEMENT_LABELS: Record<string, string> = {
  F3_F4: "Gate F3\u2192F4",
  F1_F2: "Gate F1\u2192F2",
  ACTO: "Actos Adm.",
  CONVENIO: "Convenios",
  GLOSA: "Glosa Presup.",
  CONFIG: "Configuraci\u00f3n",
};

function formatValue(item: ThresholdItem) {
  if (item.value_utm != null && item.code === "UTM_VALUE") {
    return formatCLPExact(item.value_utm);
  }
  if (item.value_utm != null) return `${Number(item.value_utm).toLocaleString("es-CL")} UTM`;
  if (item.value_pct != null) return `${item.value_pct}%`;
  return "-";
}

// ---------------------------------------------------------------------------
// SNI Levels Types & Helpers
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Financing Tracks Types
// ---------------------------------------------------------------------------

interface TrackSummary {
  track_code: string;
  track_label: string;
  total_iprs: number;
  by_phase: Record<string, number>;
  critical_alerts: number;
}

const PHASE_COLORS: Record<string, string> = {
  F0: "bg-gray-200 text-gray-800",
  F1: "bg-blue-100 text-blue-800",
  F2: "bg-indigo-100 text-indigo-800",
  F3: "bg-violet-100 text-violet-800",
  F4: "bg-emerald-100 text-emerald-800",
  F5: "bg-green-100 text-green-800",
};

// ---------------------------------------------------------------------------
// Collapsible Section
// ---------------------------------------------------------------------------

function ConfigSection({
  title,
  defaultOpen = false,
  children,
}: {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-lg border">
      <button
        type="button"
        className="flex items-center justify-between w-full px-4 py-3 text-left hover:bg-muted/30 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <h3 className="text-sm font-semibold">{title}</h3>
        {open ? <ChevronDown className="size-4 text-muted-foreground" /> : <ChevronRight className="size-4 text-muted-foreground" />}
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export function TabConfig() {
  return (
    <div className="space-y-4">
      <ConfigSection title="Umbrales Financieros" defaultOpen={true}>
        <UmbralesSection />
      </ConfigSection>

      <ConfigSection title="Niveles SNI">
        <NivelesSniSection />
      </ConfigSection>

      <ConfigSection title="Vías de Financiamiento">
        <FinancingTracksSection />
      </ConfigSection>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Umbrales Section
// ---------------------------------------------------------------------------

function UmbralesSection() {
  const [thresholds, setThresholds] = useState<ThresholdItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selected, setSelected] = useState<ThresholdItem | null>(null);
  const [editing, setEditing] = useState(false);
  const [editLabel, setEditLabel] = useState("");
  const [editValueUtm, setEditValueUtm] = useState("");
  const [editValuePct, setEditValuePct] = useState("");
  const [editSource, setEditSource] = useState("");
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [confirmDeactivate, setConfirmDeactivate] = useState(false);

  const loadThresholds = () => {
    setIsLoading(true);
    api
      .get<ThresholdItem[]>("/api/admin/thresholds")
      .then(setThresholds)
      .catch(() => setThresholds([]))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadThresholds();
  }, []);

  const openDetail = (item: ThresholdItem) => {
    setSelectedId(item.id);
    setSelected(item);
    setEditing(false);
    setEditError(null);
  };

  const openEdit = () => {
    if (!selected) return;
    setEditLabel(selected.label);
    setEditValueUtm(selected.value_utm != null ? String(selected.value_utm) : "");
    setEditValuePct(selected.value_pct != null ? String(selected.value_pct) : "");
    setEditSource(selected.source_normativa ?? "");
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
      if (editValueUtm) payload.value_utm = parseFloat(editValueUtm);
      if (editValuePct) payload.value_pct = parseFloat(editValuePct);
      if (editSource !== (selected?.source_normativa ?? "")) payload.source_normativa = editSource || null;

      await api.patch(`/api/admin/thresholds/${selectedId}`, payload);
      setEditing(false);
      loadThresholds();
      const updated = await api.get<ThresholdItem[]>("/api/admin/thresholds");
      const fresh = updated.find((t) => t.id === selectedId);
      if (fresh) setSelected(fresh);
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEditSaving(false);
    }
  };

  const performToggleActive = async () => {
    if (!selectedId || !selected) return;
    try {
      await api.patch(`/api/admin/thresholds/${selectedId}`, {
        is_active: !selected.is_active,
      });
      loadThresholds();
      setSelected({ ...selected, is_active: !selected.is_active });
    } catch {
      // ignore
    }
  };

  const handleToggleActive = () => {
    if (!selected) return;
    // Activar no requiere confirmación; desactivar sí.
    if (selected.is_active) {
      setConfirmDeactivate(true);
    } else {
      performToggleActive();
    }
  };

  return (
    <>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Código</TableHead>
              <TableHead>Descripción</TableHead>
              <TableHead>Valor</TableHead>
              <TableHead>Punto de Aplicación</TableHead>
              <TableHead>Estado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                  Cargando...
                </TableCell>
              </TableRow>
            ) : thresholds.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                  Sin umbrales configurados
                </TableCell>
              </TableRow>
            ) : (
              thresholds.map((t) => (
                <TableRow
                  key={t.id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => openDetail(t)}
                >
                  <TableCell className="font-mono text-xs">{t.code}</TableCell>
                  <TableCell className="text-sm">{t.label}</TableCell>
                  <TableCell className="font-mono text-xs tabular-nums">
                    {formatValue(t)}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-xs">
                      {ENFORCEMENT_LABELS[t.enforcement_point] ?? t.enforcement_point}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={t.is_active ? "default" : "secondary"} className="text-xs">
                      {t.is_active ? "Activo" : "Inactivo"}
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
        title="Detalle Umbral"
      >
        {selected && !editing ? (
          <div className="space-y-4">
            <div>
              <p className="font-mono text-xs text-muted-foreground">{selected.code}</p>
              <p className="font-semibold text-base mt-1">{selected.label}</p>
            </div>

            <div className="rounded-lg border divide-y text-sm">
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Valor</span>
                <span className="font-mono">{formatValue(selected)}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Punto de aplicación</span>
                <span>{ENFORCEMENT_LABELS[selected.enforcement_point] ?? selected.enforcement_point}</span>
              </div>
              {selected.source_normativa && (
                <div className="flex justify-between px-3 py-2">
                  <span className="text-muted-foreground">Fuente normativa</span>
                  <span className="text-right max-w-[200px]">{selected.source_normativa}</span>
                </div>
              )}
              {selected.applies_to_track && (
                <div className="flex justify-between px-3 py-2">
                  <span className="text-muted-foreground">Track</span>
                  <span className="font-mono">{selected.applies_to_track}</span>
                </div>
              )}
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
              Editar Umbral
            </p>
            <div>
              <label className="text-xs text-muted-foreground">Descripción</label>
              <Input
                value={editLabel}
                onChange={(e) => setEditLabel(e.target.value)}
                className="h-8 text-sm mt-1"
              />
            </div>
            {selected.value_utm != null && (
              <div>
                <label className="text-xs text-muted-foreground">
                  {selected.code === "UTM_VALUE" ? "Valor CLP" : "Valor UTM"}
                </label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={editValueUtm}
                  onChange={(e) => setEditValueUtm(e.target.value)}
                  className="h-8 text-sm font-mono mt-1"
                />
              </div>
            )}
            {selected.value_pct != null && (
              <div>
                <label className="text-xs text-muted-foreground">Valor %</label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  value={editValuePct}
                  onChange={(e) => setEditValuePct(e.target.value)}
                  className="h-8 text-sm font-mono mt-1"
                />
              </div>
            )}
            <div>
              <label className="text-xs text-muted-foreground">Fuente normativa</label>
              <Input
                value={editSource}
                onChange={(e) => setEditSource(e.target.value)}
                className="h-8 text-sm mt-1"
              />
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

      <ConfirmDialog
        open={confirmDeactivate}
        onOpenChange={setConfirmDeactivate}
        title="¿Desactivar umbral?"
        description={
          selected
            ? `¿Desactivar el umbral ${selected.label}? Dejará de exigirse en las transiciones. Puedes reactivarlo después.`
            : ""
        }
        confirmLabel="Desactivar"
        onConfirm={async () => {
          await performToggleActive();
          setConfirmDeactivate(false);
        }}
      />
    </>
  );
}

// ---------------------------------------------------------------------------
// Niveles SNI Section
// ---------------------------------------------------------------------------

function NivelesSniSection() {
  const [levels, setLevels] = useState<SniLevel[]>([]);
  const [isLoading, setIsLoading] = useState(false);

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

  const [showCreate, setShowCreate] = useState(false);
  const [createNumber, setCreateNumber] = useState("");
  const [createLabel, setCreateLabel] = useState("");
  const [createMinUtm, setCreateMinUtm] = useState("");
  const [createMaxUtm, setCreateMaxUtm] = useState("");
  const [createEvaluator, setCreateEvaluator] = useState("");
  const [createExternal, setCreateExternal] = useState(false);
  const [createSaving, setCreateSaving] = useState(false);
  const [confirmDeactivate, setConfirmDeactivate] = useState(false);

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

  const performToggleActive = async () => {
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

  const handleToggleActive = () => {
    if (!selected) return;
    // Activar no requiere confirmación; desactivar sí.
    if (selected.is_active) {
      setConfirmDeactivate(true);
    } else {
      performToggleActive();
    }
  };

  return (
    <>
      <div className="flex items-center justify-end mb-3">
        <Button size="sm" onClick={() => setShowCreate(!showCreate)}>
          <Plus className="size-4 mr-1" />Nuevo Nivel
        </Button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="rounded-lg border p-4 space-y-3 mb-3">
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
              <label className="text-xs text-muted-foreground">Min. UTM</label>
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
              <label className="text-xs text-muted-foreground">Max. UTM</label>
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
              id="create-external-sni"
            />
            <label htmlFor="create-external-sni" className="text-sm">Requiere evaluación externa</label>
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
                <label className="text-xs text-muted-foreground">Min. UTM</label>
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
                <label className="text-xs text-muted-foreground">Max. UTM</label>
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
                id="edit-external-sni"
              />
              <label htmlFor="edit-external-sni" className="text-sm">Requiere evaluación externa</label>
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

      <ConfirmDialog
        open={confirmDeactivate}
        onOpenChange={setConfirmDeactivate}
        title="¿Desactivar nivel SNI?"
        description={
          selected
            ? `¿Desactivar el nivel ${selected.label}? Dejará de exigirse en las transiciones. Puedes reactivarlo después.`
            : ""
        }
        confirmLabel="Desactivar"
        onConfirm={async () => {
          await performToggleActive();
          setConfirmDeactivate(false);
        }}
      />
    </>
  );
}

// ---------------------------------------------------------------------------
// Financing Tracks Section
// ---------------------------------------------------------------------------

function FinancingTracksSection() {
  const router = useRouter();
  const [tracks, setTracks] = useState<TrackSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<TrackSummary[]>("/api/ipr/track-summary")
      .then(setTracks)
      .catch(() => setTracks([]))
      .finally(() => setLoading(false));
  }, []);

  const totalIprs = tracks.reduce((s, t) => s + t.total_iprs, 0);
  const totalAlerts = tracks.reduce((s, t) => s + t.critical_alerts, 0);

  return (
    <>
      {/* Summary strip */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="rounded-lg border bg-card p-3">
          <p className="text-xs text-muted-foreground">Tracks activos</p>
          <p className="text-2xl font-semibold tabular-nums">{tracks.length}</p>
        </div>
        <div className="rounded-lg border bg-card p-3">
          <p className="text-xs text-muted-foreground">Total IPRs con mecanismo</p>
          <p className="text-2xl font-semibold tabular-nums">{totalIprs.toLocaleString("es-CL")}</p>
        </div>
        <div className="rounded-lg border bg-card p-3">
          <p className="text-xs text-muted-foreground">Alertas críticas</p>
          <p className={cn("text-2xl font-semibold tabular-nums", totalAlerts > 0 ? "text-red-600" : "")}>
            {totalAlerts}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {tracks.map((track) => (
            <div
              key={track.track_code}
              className="rounded-lg border bg-card p-4 space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="font-mono text-xs">
                    {track.track_code}
                  </Badge>
                  <span className="text-sm font-medium">{track.track_label}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-lg font-semibold tabular-nums">
                    {track.total_iprs}
                  </span>
                  <span className="text-xs text-muted-foreground">IPRs</span>
                  {track.critical_alerts > 0 && (
                    <Badge variant="destructive" className="text-xs">
                      {track.critical_alerts} alertas
                    </Badge>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 text-xs"
                    onClick={() => router.push(`/ipr?mechanism=${track.track_code}`)}
                  >
                    <ExternalLink className="size-3 mr-1" />
                    Ver IPRs
                  </Button>
                </div>
              </div>

              {/* Phase distribution bar */}
              {track.total_iprs > 0 && (
                <div className="space-y-1.5">
                  <div className="flex h-3 rounded-full overflow-hidden">
                    {Object.entries(track.by_phase).map(([phase, count]) =>
                      count > 0 ? (
                        <div
                          key={phase}
                          className={cn("h-full", PHASE_COLORS[phase]?.split(" ")[0] ?? "bg-gray-200")}
                          style={{ width: `${(count / track.total_iprs) * 100}%` }}
                          title={`${phase}: ${count} IPRs`}
                        />
                      ) : null
                    )}
                  </div>
                  <div className="flex gap-3 flex-wrap">
                    {Object.entries(track.by_phase).map(([phase, count]) =>
                      count > 0 ? (
                        <span
                          key={phase}
                          className={cn("text-[10px] px-1.5 py-0.5 rounded font-medium tabular-nums", PHASE_COLORS[phase] ?? "")}
                        >
                          {phase}: {count}
                        </span>
                      ) : null
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
