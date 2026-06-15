"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { TrendingUp, TrendingDown, Minus, X, Plus, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";
import { toast } from "sonner";
import type { DGIIndicator } from "@/types";
import type { DomainConfig } from "./types";

const signalColors: Record<string, string> = {
  VERDE: "bg-green-600",
  AMARILLO: "bg-amber-400",
  ROJO: "bg-red-600",
};

const lifecycleColors: Record<string, string> = {
  BORRADOR: "bg-slate-100 text-slate-700",
  APROBADO: "bg-blue-100 text-blue-700",
  VIGENTE: "bg-green-100 text-green-700",
  DEPRECADO: "bg-gray-100 text-gray-500",
};

const LIFECYCLE_FSM: Record<string, { target: string; label: string; variant: "default" | "outline" | "destructive" }[]> = {
  BORRADOR: [{ target: "APROBADO", label: "Aprobar", variant: "default" }],
  APROBADO: [{ target: "VIGENTE", label: "Publicar", variant: "default" }],
  VIGENTE: [{ target: "DEPRECADO", label: "Deprecar", variant: "destructive" }],
};

const DIMENSION_OPTIONS = [
  { value: "PRESUPUESTO", label: "Presupuesto" },
  { value: "CARTERA_IPR", label: "Cartera IPR" },
  { value: "CONVENIOS", label: "Convenios" },
  { value: "TDE", label: "Transform. Digital" },
  { value: "RIESGOS", label: "Riesgos" },
];

const FREQUENCY_OPTIONS = [
  { value: "DIARIA", label: "Diaria" },
  { value: "SEMANAL", label: "Semanal" },
  { value: "QUINCENAL", label: "Quincenal" },
  { value: "MENSUAL", label: "Mensual" },
  { value: "TRIMESTRAL", label: "Trimestral" },
];

const SOURCE_TYPE_OPTIONS = [
  { value: "AUTO", label: "Auto" },
  { value: "MANUAL", label: "Manual" },
  { value: "EXTERNAL", label: "External" },
];

function TrendIcon({ trend }: { trend: "up" | "down" | "flat" | null }) {
  if (trend === "up") return <TrendingUp className="size-3 text-green-600 inline-block" />;
  if (trend === "down") return <TrendingDown className="size-3 text-red-600 inline-block" />;
  return <Minus className="size-3 text-muted-foreground inline-block" />;
}

function SignalDot({ signal }: { signal: "VERDE" | "AMARILLO" | "ROJO" | null }) {
  if (!signal) return <span className="inline-block size-2.5 rounded-full bg-gray-300" />;
  return <span className={cn("inline-block size-2.5 rounded-full", signalColors[signal] ?? "bg-gray-300")} title={signal} />;
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-24">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

function IndicadorDetailPanel({ item, onClose, onRefresh }: { item: unknown; onClose: () => void; onRefresh?: () => void }) {
  const ind = item as DGIIndicator;
  const { user } = useAuth();
  const isJefeDGI = user?.role_code === "JEFE_DGI";

  const pct = ind.current_value !== null && ind.target_value && ind.target_value > 0
    ? Math.min(100, Math.round((ind.current_value / ind.target_value) * 100))
    : null;

  const [lifecycleLoading, setLifecycleLoading] = useState<string | null>(null);
  const [deprecarOpen, setDeprecarOpen] = useState(false);
  const [manualValue, setManualValue] = useState("");
  const [manualComment, setManualComment] = useState("");
  const [manualSubmitting, setManualSubmitting] = useState(false);

  const handleLifecycleTransition = useCallback(async (target: string) => {
    setLifecycleLoading(target);
    try {
      await api.post(`/api/dgi/data/indicators/${ind.id}/lifecycle`, { target_status: target });
      toast.success("Estado de ciclo de vida actualizado");
      onRefresh?.();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al cambiar estado");
    } finally {
      setLifecycleLoading(null);
    }
  }, [ind.id, onRefresh]);

  const handleManualValue = useCallback(async () => {
    setManualSubmitting(true);
    try {
      await api.post(`/api/dgi/data/indicators/${ind.id}/value`, {
        value: parseFloat(manualValue),
        comment: manualComment || undefined,
      });
      toast.success("Valor registrado");
      setManualValue("");
      setManualComment("");
      onRefresh?.();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al registrar valor");
    } finally {
      setManualSubmitting(false);
    }
  }, [ind.id, manualValue, manualComment, onRefresh]);

  const transitions = ind.lifecycle_status ? LIFECYCLE_FSM[ind.lifecycle_status] ?? [] : [];

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">{ind.code}</p>
          <h3 className="text-sm font-semibold leading-tight">{ind.name}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Dimensión" value={ind.dimension} />
          <Separator />
          <DetailRow label="Unidad" value={ind.unit} />
          <Separator />
          <DetailRow label="Valor actual" value={
            <span className="font-mono tabular-nums font-semibold text-base">
              {ind.current_value !== null ? ind.current_value : "-"}{" "}
              <span className="text-xs font-normal text-muted-foreground">{ind.unit}</span>
            </span>
          } />
          <Separator />
          <DetailRow label="Meta" value={
            <span className="font-mono tabular-nums">
              {ind.target_value !== null ? ind.target_value : "-"}{" "}
              <span className="text-xs text-muted-foreground">{ind.unit}</span>
            </span>
          } />
          {pct !== null && (
            <>
              <Separator />
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Avance</span>
                  <span className="font-mono">{pct}%</span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className={cn("h-full rounded-full transition-all", pct >= 90 ? "bg-green-600" : pct >= 60 ? "bg-amber-400" : "bg-red-500")}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            </>
          )}
          <Separator />
          <DetailRow label="Señal" value={<div className="flex items-center gap-1.5"><SignalDot signal={ind.signal} /><span>{ind.signal ?? "-"}</span></div>} />
          <Separator />
          <DetailRow label="Tendencia" value={<div className="flex items-center gap-1"><TrendIcon trend={ind.trend} /><span className="text-xs capitalize">{ind.trend ?? "-"}</span></div>} />
          <Separator />
          <DetailRow label="Actualizado" value={formatDate(ind.last_updated_at)} />
          {ind.description && (
            <>
              <Separator />
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground font-medium">Descripción</p>
                <p className="text-xs leading-relaxed text-foreground/80">{ind.description}</p>
              </div>
            </>
          )}
          <Separator />
          <DetailRow label="Fórmula" value={ind.formula ?? "-"} />
          <Separator />
          <DetailRow label="Frecuencia" value={ind.frequency ?? "-"} />
          <Separator />
          <DetailRow label="Fuente" value={ind.source_type ?? "-"} />
          <Separator />
          <DetailRow label="Ciclo de Vida" value={
            <Badge className={cn("text-[10px] px-1.5 py-0 border-0", lifecycleColors[ind.lifecycle_status ?? ""] ?? "")}>
              {ind.lifecycle_status ?? "-"}
            </Badge>
          } />

          {isJefeDGI && transitions.length > 0 && (
            <>
              <Separator />
              <div className="pt-1">
                <p className="text-xs font-semibold text-muted-foreground mb-2">Transiciones</p>
                <div className="flex flex-wrap gap-2">
                  {transitions.map((t) =>
                    t.variant === "destructive" ? (
                      <span key={t.target}>
                        <Button
                          size="sm"
                          variant="destructive"
                          className="h-7 text-xs"
                          disabled={lifecycleLoading !== null}
                          onClick={() => setDeprecarOpen(true)}
                        >
                          {lifecycleLoading === t.target && <Loader2 className="size-3 mr-1 animate-spin" />}
                          {t.label}
                        </Button>
                        <ConfirmDialog
                          open={deprecarOpen}
                          onOpenChange={setDeprecarOpen}
                          title="Deprecar indicador"
                          description="Esta accion marcara el indicador como deprecado. No se incluira en calculos ni reportes futuros."
                          variant="destructive"
                          confirmLabel="Deprecar"
                          loading={lifecycleLoading === t.target}
                          onConfirm={() => handleLifecycleTransition(t.target)}
                        />
                      </span>
                    ) : (
                      <Button
                        key={t.target}
                        size="sm"
                        variant={t.variant}
                        className="h-7 text-xs"
                        disabled={lifecycleLoading !== null}
                        onClick={() => handleLifecycleTransition(t.target)}
                      >
                        {lifecycleLoading === t.target && <Loader2 className="size-3 mr-1 animate-spin" />}
                        {t.label}
                      </Button>
                    )
                  )}
                </div>
              </div>
            </>
          )}

          {(ind.source_type === "MANUAL" || ind.source_type === "EXTERNAL") && ind.lifecycle_status === "VIGENTE" && (
            <>
              <Separator />
              <div className="space-y-2 pt-2">
                <p className="text-xs font-semibold text-muted-foreground">Registrar Valor Manual</p>
                <div className="flex gap-2">
                  <input
                    type="number"
                    step="any"
                    value={manualValue}
                    onChange={(e) => setManualValue(e.target.value)}
                    placeholder="Valor"
                    className="flex-1 h-7 text-xs rounded-md border border-input bg-background px-2"
                  />
                  <input
                    value={manualComment}
                    onChange={(e) => setManualComment(e.target.value)}
                    placeholder="Comentario"
                    className="flex-1 h-7 text-xs rounded-md border border-input bg-background px-2"
                  />
                </div>
                <Button
                  size="sm"
                  className="h-7 text-xs"
                  onClick={handleManualValue}
                  disabled={manualSubmitting || !manualValue}
                >
                  {manualSubmitting ? "Registrando..." : "Registrar"}
                </Button>
              </div>
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

function NuevoIndicadorAction({ onRefresh }: { onRefresh: () => void }) {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [dimension, setDimension] = useState("");
  const [description, setDescription] = useState("");
  const [formula, setFormula] = useState("");
  const [frequency, setFrequency] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [unit, setUnit] = useState("");
  const [targetValue, setTargetValue] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (user?.role_code !== "JEFE_DGI") return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError("Nombre es requerido"); return; }
    if (!dimension) { setError("Dimension es requerida"); return; }
    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/dgi/data/indicators", {
        name: name.trim(),
        dimension,
        description: description.trim() || undefined,
        formula: formula.trim() || undefined,
        frequency: frequency || undefined,
        source_type: sourceType || undefined,
        unit: unit.trim() || undefined,
        target_value: targetValue ? parseFloat(targetValue) : undefined,
      });
      toast.success("Indicador creado");
      setOpen(false);
      setName(""); setDimension(""); setDescription(""); setFormula("");
      setFrequency(""); setSourceType(""); setUnit(""); setTargetValue("");
      onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear indicador");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="h-7 text-xs gap-1.5">
          <Plus className="size-3.5" />
          Nuevo Indicador
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Crear Indicador</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-medium">Nombre *</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nombre del indicador"
              className="w-full h-8 text-xs rounded-md border border-input bg-background px-3 py-1"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Dimensión *</label>
            <Select value={dimension} onValueChange={setDimension}>
              <SelectTrigger className="h-8 text-xs">
                <SelectValue placeholder="Seleccionar dimensión" />
              </SelectTrigger>
              <SelectContent>
                {DIMENSION_OPTIONS.map((o) => (
                  <SelectItem key={o.value} value={o.value} className="text-xs">{o.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Descripción</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Descripción del indicador"
              className="w-full h-16 text-xs rounded-md border border-input bg-background px-3 py-2 resize-none"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Fórmula</label>
            <input
              value={formula}
              onChange={(e) => setFormula(e.target.value)}
              placeholder="Ej: (pagado / vigente) * 100"
              className="w-full h-8 text-xs rounded-md border border-input bg-background px-3 py-1"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium">Frecuencia</label>
              <Select value={frequency} onValueChange={setFrequency}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue placeholder="Seleccionar" />
                </SelectTrigger>
                <SelectContent>
                  {FREQUENCY_OPTIONS.map((o) => (
                    <SelectItem key={o.value} value={o.value} className="text-xs">{o.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Tipo fuente</label>
              <Select value={sourceType} onValueChange={setSourceType}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue placeholder="Seleccionar" />
                </SelectTrigger>
                <SelectContent>
                  {SOURCE_TYPE_OPTIONS.map((o) => (
                    <SelectItem key={o.value} value={o.value} className="text-xs">{o.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium">Unidad</label>
              <input
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                placeholder="Ej: %"
                className="w-full h-8 text-xs rounded-md border border-input bg-background px-3 py-1"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Valor meta</label>
              <input
                type="number"
                step="any"
                value={targetValue}
                onChange={(e) => setTargetValue(e.target.value)}
                placeholder="0"
                className="w-full h-8 text-xs rounded-md border border-input bg-background px-3 py-1"
              />
            </div>
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" size="sm" disabled={submitting}>
              {submitting ? "Guardando..." : "Crear"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export const indicadoresConfig: DomainConfig = {
  id: "indicadores",
  label: "Indicadores",
  paginationMode: "client",
  searchPlaceholder: "Buscar indicador...",
  filters: [
    {
      key: "dimension", label: "Dimensión",
      options: DIMENSION_OPTIONS,
    },
    {
      key: "signal", label: "Señal",
      options: [
        { value: "VERDE", label: "Verde" },
        { value: "AMARILLO", label: "Amarillo" },
        { value: "ROJO", label: "Rojo" },
      ],
    },
    {
      key: "trend", label: "Tendencia",
      options: [
        { value: "down", label: "Empeorando" },
        { value: "up", label: "Mejorando" },
        { value: "flat", label: "Estable" },
      ],
    },
    {
      key: "lifecycle", label: "Ciclo de Vida",
      options: [
        { value: "BORRADOR", label: "Borrador" },
        { value: "APROBADO", label: "Aprobado" },
        { value: "VIGENTE", label: "Vigente" },
        { value: "DEPRECADO", label: "Deprecado" },
      ],
    },
  ],
  columns: [
    {
      key: "signal", label: "",
      render: (_, row) => {
        const ind = row as DGIIndicator;
        return <div className="flex items-center gap-1.5"><SignalDot signal={ind.signal} /><TrendIcon trend={ind.trend} /></div>;
      },
    },
    { key: "name", label: "Nombre", render: (v) => <span className="text-xs font-medium leading-snug">{String(v ?? "")}</span> },
    { key: "dimension", label: "Dimensión", render: (v) => <Badge variant="secondary" className="text-[10px] px-1.5 py-0">{String(v ?? "-")}</Badge> },
    {
      key: "current_value", label: "Valor",
      render: (value, row) => {
        const ind = row as DGIIndicator;
        return <span className="text-xs font-mono tabular-nums">{value !== null ? String(value) : "-"}{ind.unit ? <span className="text-muted-foreground ml-0.5">{ind.unit}</span> : null}</span>;
      },
    },
    { key: "lifecycle_status", label: "Ciclo", render: (v) => {
      return <Badge className={cn("text-[10px] px-1.5 py-0 border-0", lifecycleColors[String(v)] ?? "")}>{String(v ?? "-")}</Badge>;
    }},
    { key: "frequency", label: "Frecuencia", render: (v) => <Badge variant="outline" className="text-[10px] px-1.5 py-0">{String(v ?? "-")}</Badge> },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    if (params.get("dimension")) apiParams.set("dimension", params.get("dimension")!);
    if (params.get("lifecycle")) apiParams.set("lifecycle", params.get("lifecycle")!);

    const data = await api.get<DGIIndicator[]>(`/api/dgi/data/indicators?${apiParams.toString()}`);

    const search = params.get("search") ?? "";
    const signal = params.get("signal") ?? "";
    const trend = params.get("trend") ?? "";
    let filtered = data;
    if (signal) filtered = filtered.filter((i) => i.signal === signal);
    if (trend) filtered = filtered.filter((i) => i.trend === trend);
    if (search) {
      const q = search.toLowerCase();
      filtered = filtered.filter((i) => i.name.toLowerCase().includes(q) || i.code.toLowerCase().includes(q));
    }

    const PAGE_SIZE = 25;
    const page = Number(params.get("page") ?? "1");
    const total = filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    const items = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    return { items, total, totalPages };
  },
  DetailPanel: IndicadorDetailPanel,
  CreateAction: NuevoIndicadorAction,
};
