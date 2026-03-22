"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ComboboxAsync } from "@/components/combobox-async";
import type { ComboboxOption } from "@/components/combobox-async";
import { StatusBadge } from "@/components/status-badge";
import { TimelineHistory } from "@/components/timeline-history";
import { X, Loader2, Plus, AlertTriangle } from "lucide-react";
import { formatDate, formatCLP } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { PaginatedResponse, CategoryRef, HistoryEntry } from "@/types";
import type { DomainConfig } from "./types";

interface RendicionItem {
  id: string;
  agreement_number: string | null;
  ipr_codigo_bip: string | null;
  ipr_id: string | null;
  renderer_name: string | null;
  state_code: string | null;
  state_label: string | null;
  period_start: string | null;
  period_end: string | null;
  submitted_at: string | null;
  agreement_total_amount: number | null;
  amount: number | null;
  is_overdue: boolean;
  days_in_state: number | null;
}

interface RendicionDetailData extends RendicionItem {
  agreement_id: string | null;
  renderer_id: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string | null;
  history: HistoryEntry[];
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-28">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

// Multi-role state transition actions
// DGI roles see RTF/UCR review actions; operativa sees initiate/re-submit
interface StateAction {
  label: string;
  target: string;
  variant: "default" | "outline" | "destructive";
  population: "dgi" | "operativa" | "any";
}

const STATE_ACTIONS: Record<string, StateAction[]> = {
  PENDIENTE: [
    { label: "Enviar a Revisión RTF", target: "EN_REVISION_RTF", variant: "default", population: "any" },
  ],
  EN_REVISION_RTF: [
    { label: "Visar RTF", target: "VISADA_RTF", variant: "default", population: "dgi" },
    { label: "Observar", target: "OBSERVADA", variant: "outline", population: "dgi" },
  ],
  VISADA_RTF: [
    { label: "Enviar a UCR", target: "EN_REVISION_UCR", variant: "default", population: "dgi" },
  ],
  EN_REVISION_UCR: [
    { label: "Aprobar", target: "APROBADA", variant: "default", population: "dgi" },
    { label: "Aprobar Parcialmente", target: "APROBADA_PARCIALMENTE", variant: "outline", population: "dgi" },
    { label: "Observar", target: "OBSERVADA", variant: "outline", population: "dgi" },
    { label: "Rechazar", target: "RECHAZADA", variant: "destructive", population: "dgi" },
  ],
  APROBADA_PARCIALMENTE: [
    { label: "Re-enviar a Revisión RTF", target: "EN_REVISION_RTF", variant: "default", population: "any" },
  ],
  OBSERVADA: [
    { label: "Re-enviar a Revisión RTF", target: "EN_REVISION_RTF", variant: "default", population: "any" },
  ],
};

function RendicionDetailPanel({ item, onClose, onRefresh }: { item: unknown; onClose: () => void; onRefresh?: () => void }) {
  const r = item as RendicionItem;
  const { user } = useAuth();
  const population = user?.population ?? "operativa";

  const [stateMap, setStateMap] = useState<Record<string, string>>({});
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [comment, setComment] = useState("");
  const [detail, setDetail] = useState<RendicionDetailData | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Fetch rendition_state category codes → ids
  useEffect(() => {
    api.get<CategoryRef[]>("/api/catalogs/categories/rendition_state")
      .then((cats) => {
        const map: Record<string, string> = {};
        for (const c of cats) map[c.code] = c.id;
        setStateMap(map);
      })
      .catch(() => {});
  }, []);

  // Fetch detail (with history) when panel opens
  useEffect(() => {
    setLoadingDetail(true);
    api.get<RendicionDetailData>(`/api/dgi/data/rendiciones/${r.id}`)
      .then(setDetail)
      .catch(() => {})
      .finally(() => setLoadingDetail(false));
  }, [r.id]);

  const handleAction = useCallback(async (targetCode: string) => {
    const targetId = stateMap[targetCode];
    if (!targetId) return;
    setActionLoading(targetCode);
    setError(null);
    try {
      const payload: Record<string, unknown> = { state_id: targetId };
      if (comment.trim()) payload.comment = comment.trim();
      await api.patch(`/api/dgi/data/rendiciones/${r.id}`, payload);
      setComment("");
      onRefresh?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al actualizar");
    } finally {
      setActionLoading(null);
    }
  }, [r.id, stateMap, comment, onRefresh]);

  // Filter actions by user population
  const allActions = r.state_code ? STATE_ACTIONS[r.state_code] ?? [] : [];
  const actions = allActions.filter(
    (a) => a.population === "any" || a.population === population
  );

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">
            {r.ipr_codigo_bip ?? "Sin BIP"} · {r.agreement_number ?? "S/N"}
          </p>
          <h3 className="text-sm font-semibold leading-tight">{r.renderer_name ?? "Sin ejecutor"}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow
            label="Estado"
            value={
              r.state_code ? (
                <div className="flex items-center gap-1.5">
                  <StatusBadge status={r.state_code} size="sm" />
                  {r.is_overdue && (
                    <Badge variant="destructive" className="text-[10px] px-1.5 py-0 gap-0.5">
                      <AlertTriangle className="size-3" />
                      Vencida ({r.days_in_state?.toFixed(0)}d)
                    </Badge>
                  )}
                </div>
              ) : (
                r.state_label ?? "-"
              )
            }
          />
          <Separator />
          <DetailRow label="Ejecutor" value={r.renderer_name ?? "-"} />
          <Separator />
          <DetailRow label="BIP" value={r.ipr_codigo_bip ?? "-"} />
          <Separator />
          <DetailRow label="Período inicio" value={formatDate(r.period_start)} />
          <Separator />
          <DetailRow label="Período fin" value={formatDate(r.period_end)} />
          <Separator />
          <DetailRow label="Enviado" value={formatDate(r.submitted_at)} />
          <Separator />
          <DetailRow label="Monto rendido" value={<span className="font-mono tabular-nums">{r.amount ? formatCLP(r.amount) : "-"}</span>} />
          <Separator />
          <DetailRow label="Monto convenio" value={<span className="font-mono tabular-nums">{formatCLP(r.agreement_total_amount)}</span>} />
          {r.days_in_state !== null && (
            <>
              <Separator />
              <DetailRow label="Días en estado" value={<span className="tabular-nums">{r.days_in_state?.toFixed(1)}</span>} />
            </>
          )}

          {/* State transition actions */}
          {actions.length > 0 && (
            <>
              <Separator />
              <div className="pt-1">
                <p className="text-xs font-semibold text-muted-foreground mb-2">Acciones</p>
                <textarea
                  placeholder="Comentario (opcional)"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  className="w-full mb-2 h-16 text-xs rounded-md border border-input bg-background px-3 py-2 resize-none"
                />
                <div className="flex flex-wrap gap-2">
                  {actions.map((action) => (
                    <Button
                      key={action.target}
                      size="sm"
                      variant={action.variant}
                      className="h-7 text-xs"
                      disabled={actionLoading !== null || !stateMap[action.target]}
                      onClick={() => handleAction(action.target)}
                    >
                      {actionLoading === action.target && <Loader2 className="size-3 mr-1 animate-spin" />}
                      {action.label}
                    </Button>
                  ))}
                </div>
                {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
              </div>
            </>
          )}

          {/* History timeline */}
          <Separator />
          <div className="pt-1">
            <p className="text-xs font-semibold text-muted-foreground mb-2">Historial</p>
            {loadingDetail ? (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Loader2 className="size-3 animate-spin" /> Cargando...
              </div>
            ) : detail?.history && detail.history.length > 0 ? (
              <TimelineHistory entries={detail.history} />
            ) : (
              <p className="text-xs text-muted-foreground">Sin historial disponible.</p>
            )}
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}

function NuevaRendicionAction({ onRefresh }: { onRefresh: () => void }) {
  const [open, setOpen] = useState(false);
  const [iprId, setIprId] = useState("");
  const [rendererId, setRendererId] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [submittedAt, setSubmittedAt] = useState("");
  const [amount, setAmount] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchIprs = async (q: string): Promise<ComboboxOption[]> => {
    const res = await api.get<{ items: { id: string; codigo_bip: string; name: string }[] }>(
      `/api/catalogs/iprs?search=${encodeURIComponent(q)}&page_size=20`
    );
    return res.items.map((i) => ({ value: i.id, label: `${i.codigo_bip} — ${i.name}` }));
  };

  const searchOrgs = async (q: string): Promise<ComboboxOption[]> => {
    const res = await api.get<{ id: string; name: string }[]>(
      `/api/catalogs/organizations?search=${encodeURIComponent(q)}`
    );
    return res.map((o) => ({ value: o.id, label: o.name }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!iprId) { setError("Seleccione una IPR"); return; }
    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/dgi/data/rendiciones", {
        ipr_id: iprId || undefined,
        renderer_id: rendererId || undefined,
        period_start: periodStart || undefined,
        period_end: periodEnd || undefined,
        submitted_at: submittedAt ? new Date(submittedAt).toISOString() : undefined,
        amount: amount ? parseFloat(amount) : undefined,
      });
      setOpen(false);
      setIprId(""); setRendererId(""); setPeriodStart(""); setPeriodEnd(""); setSubmittedAt(""); setAmount("");
      onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear rendición");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="h-7 text-xs gap-1.5">
          <Plus className="size-3.5" />
          Nueva Rendición
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Registrar Rendición</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-medium">IPR *</label>
            <ComboboxAsync
              value={iprId}
              onChange={setIprId}
              searchFn={searchIprs}
              placeholder="Buscar por BIP o nombre..."
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Ejecutor (opcional)</label>
            <ComboboxAsync
              value={rendererId}
              onChange={setRendererId}
              searchFn={searchOrgs}
              placeholder="Buscar organización..."
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium">Período inicio</label>
              <input type="date" value={periodStart} onChange={(e) => setPeriodStart(e.target.value)}
                className="w-full h-8 text-xs rounded-md border border-input bg-background px-3 py-1" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Período fin</label>
              <input type="date" value={periodEnd} onChange={(e) => setPeriodEnd(e.target.value)}
                className="w-full h-8 text-xs rounded-md border border-input bg-background px-3 py-1" />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Monto rendido (opcional)</label>
            <input type="number" step="1" min="0" value={amount} onChange={(e) => setAmount(e.target.value)}
              placeholder="$0"
              className="w-full h-8 text-xs rounded-md border border-input bg-background px-3 py-1" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Fecha de envío (opcional)</label>
            <input type="date" value={submittedAt} onChange={(e) => setSubmittedAt(e.target.value)}
              className="w-full h-8 text-xs rounded-md border border-input bg-background px-3 py-1" />
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" size="sm" disabled={submitting}>
              {submitting ? "Guardando..." : "Registrar"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export const rendicionesConfig: DomainConfig = {
  id: "rendiciones",
  label: "Rendiciones",
  paginationMode: "server",
  searchPlaceholder: "Buscar convenio, BIP o ejecutor...",
  filters: [
    {
      key: "state",
      label: "Estado",
      options: [
        { value: "PENDIENTE", label: "Pendiente" },
        { value: "EN_REVISION_RTF", label: "En Revisión RTF" },
        { value: "VISADA_RTF", label: "Visada RTF" },
        { value: "EN_REVISION_UCR", label: "En Revisión UCR" },
        { value: "OBSERVADA", label: "Observada" },
        { value: "APROBADA", label: "Aprobada" },
        { value: "APROBADA_PARCIALMENTE", label: "Aprobada Parcialmente" },
        { value: "RECHAZADA", label: "Rechazada" },
        { value: "VENCIDAS", label: "\u26A0 Vencidas (SLA)" },
      ],
    },
  ],
  columns: [
    { key: "ipr_codigo_bip", label: "BIP", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "agreement_number", label: "Convenio", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "S/N")}</span> },
    { key: "renderer_name", label: "Ejecutor", render: (v) => <span className="text-xs line-clamp-1">{String(v ?? "-")}</span> },
    {
      key: "state_code", label: "Estado",
      render: (_, row) => {
        const r = row as RendicionItem;
        return (
          <div className="flex items-center gap-1">
            {r.state_code ? (
              <StatusBadge status={r.state_code} size="sm" />
            ) : (
              <Badge variant="outline" className="text-[10px]">{r.state_label ?? "-"}</Badge>
            )}
            {r.is_overdue && (
              <Badge variant="destructive" className="text-[10px] px-1 py-0 gap-0.5">
                <AlertTriangle className="size-2.5" />
                {r.days_in_state !== null && `${Math.floor(r.days_in_state)}d`}
              </Badge>
            )}
          </div>
        );
      },
    },
    {
      key: "days_in_state", label: "SLA",
      render: (_, row) => {
        const r = row as RendicionItem;
        if (r.days_in_state === null || r.days_in_state === undefined) return <span className="text-muted-foreground">-</span>;
        const days = Math.floor(r.days_in_state);
        const slaMap: Record<string, number> = { EN_REVISION_RTF: 7, VISADA_RTF: 1, EN_REVISION_UCR: 2, OBSERVADA: 15 };
        const sla = r.state_code ? slaMap[r.state_code] : undefined;
        if (!sla) return <span className="text-xs text-muted-foreground tabular-nums">{days}d</span>;
        const ratio = r.days_in_state / sla;
        return (
          <div className="flex items-center gap-1.5">
            <div className="h-1.5 w-10 rounded-full bg-gray-200 overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  ratio >= 1 ? "bg-red-500" : ratio >= 0.7 ? "bg-amber-500" : "bg-green-500"
                )}
                style={{ width: `${Math.min(ratio * 100, 100)}%` }}
              />
            </div>
            <span className={cn(
              "text-[10px] tabular-nums font-mono",
              ratio >= 1 ? "text-red-600 font-semibold" : ratio >= 0.7 ? "text-amber-600" : "text-muted-foreground"
            )}>
              {days}/{sla}d
            </span>
          </div>
        );
      },
    },
    {
      key: "period_start", label: "Período",
      render: (_, row) => {
        const r = row as RendicionItem;
        return <span className="text-xs tabular-nums">{formatDate(r.period_start)} — {formatDate(r.period_end)}</span>;
      },
    },
    { key: "amount", label: "Monto", render: (v) => <span className="text-xs font-mono tabular-nums">{v ? formatCLP(v as number) : "-"}</span> },
  ],
  fetchData: async (params) => {
    const stateFilter = params.get("state");

    // Special case: "VENCIDAS" uses dedicated endpoint
    if (stateFilter === "VENCIDAS") {
      const apiParams = new URLSearchParams();
      apiParams.set("page", params.get("page") ?? "1");
      apiParams.set("page_size", "25");
      if (params.get("search")) apiParams.set("search", params.get("search")!);
      const response = await api.get<PaginatedResponse<RendicionItem>>(`/api/dgi/data/rendiciones/vencidas?${apiParams.toString()}`);
      return { items: response.items, total: response.total, totalPages: response.total_pages };
    }

    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    if (params.get("search")) apiParams.set("search", params.get("search")!);
    if (stateFilter) apiParams.set("state", stateFilter);
    const response = await api.get<PaginatedResponse<RendicionItem>>(`/api/dgi/data/rendiciones?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: RendicionDetailPanel,
  CreateAction: NuevaRendicionAction,
};
