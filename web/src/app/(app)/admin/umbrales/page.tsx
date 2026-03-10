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
import { formatCLP } from "@/lib/format";
import { PageHeader } from "@/components/page-header";

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
    return formatCLP(item.value_utm);
  }
  if (item.value_utm != null) return `${Number(item.value_utm).toLocaleString("es-CL")} UTM`;
  if (item.value_pct != null) return `${item.value_pct}%`;
  return "-";
}

export default function UmbralesPage() {
  const { user } = useAuth();
  const [thresholds, setThresholds] = useState<ThresholdItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Edit drawer
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selected, setSelected] = useState<ThresholdItem | null>(null);
  const [editing, setEditing] = useState(false);
  const [editLabel, setEditLabel] = useState("");
  const [editValueUtm, setEditValueUtm] = useState("");
  const [editValuePct, setEditValuePct] = useState("");
  const [editSource, setEditSource] = useState("");
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

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
      // Refresh selected
      const updated = await api.get<ThresholdItem[]>("/api/admin/thresholds");
      const fresh = updated.find((t) => t.id === selectedId);
      if (fresh) setSelected(fresh);
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEditSaving(false);
    }
  };

  const handleToggleActive = async () => {
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

  if (!user || user.role_code !== "ADMIN_SISTEMA") {
    return <p className="p-6 text-muted-foreground">Acceso restringido a ADMIN_SISTEMA.</p>;
  }

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Umbrales Financieros"
        description="Configuración de límites de compliance financiero"
      />

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>C&oacute;digo</TableHead>
              <TableHead>Descripci&oacute;n</TableHead>
              <TableHead>Valor</TableHead>
              <TableHead>Punto de Aplicaci&oacute;n</TableHead>
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
                <span className="text-muted-foreground">Punto de aplicaci&oacute;n</span>
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
              <label className="text-xs text-muted-foreground">Descripci&oacute;n</label>
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
    </div>
  );
}
