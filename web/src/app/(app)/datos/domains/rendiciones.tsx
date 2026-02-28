"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X, Loader2 } from "lucide-react";
import { formatDate, formatCLP } from "@/lib/format";
import type { PaginatedResponse, CategoryRef } from "@/types";
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
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-28">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

// State transition actions map
const STATE_ACTIONS: Record<string, { label: string; target: string; variant: "default" | "outline" | "destructive" }[]> = {
  PENDIENTE: [
    { label: "Iniciar Revisión", target: "EN_REVISION", variant: "default" },
  ],
  EN_REVISION: [
    { label: "Aprobar", target: "APROBADA", variant: "default" },
    { label: "Observar", target: "OBSERVADA", variant: "outline" },
    { label: "Rechazar", target: "RECHAZADA", variant: "destructive" },
  ],
  OBSERVADA: [
    { label: "Re-enviar a Revisión", target: "EN_REVISION", variant: "default" },
  ],
};

const stateBadgeColor: Record<string, string> = {
  PENDIENTE: "bg-gray-100 text-gray-700 border-gray-300",
  EN_REVISION: "bg-amber-50 text-amber-700 border-amber-300",
  OBSERVADA: "bg-orange-50 text-orange-700 border-orange-300",
  APROBADA: "bg-green-50 text-green-700 border-green-300",
  RECHAZADA: "bg-red-50 text-red-700 border-red-300",
};

function RendicionDetailPanel({ item, onClose, onRefresh }: { item: unknown; onClose: () => void; onRefresh?: () => void }) {
  const r = item as RendicionItem;
  const { user } = useAuth();
  const isDGI = user?.population === "dgi";

  const [stateMap, setStateMap] = useState<Record<string, string>>({});
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  const handleAction = useCallback(async (targetCode: string) => {
    const targetId = stateMap[targetCode];
    if (!targetId) return;
    setActionLoading(targetCode);
    setError(null);
    try {
      await api.patch(`/api/dgi/data/rendiciones/${r.id}`, { state_id: targetId });
      onRefresh?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al actualizar");
    } finally {
      setActionLoading(null);
    }
  }, [r.id, stateMap, onRefresh]);

  const actions = r.state_code ? STATE_ACTIONS[r.state_code] ?? [] : [];

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
                <Badge variant="outline" className={`text-xs ${stateBadgeColor[r.state_code] ?? ""}`}>
                  {r.state_label ?? r.state_code}
                </Badge>
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
          <DetailRow label="Monto convenio" value={<span className="font-mono tabular-nums">{formatCLP(r.agreement_total_amount)}</span>} />

          {/* State transition actions */}
          {isDGI && actions.length > 0 && (
            <>
              <Separator />
              <div className="pt-1">
                <p className="text-xs font-semibold text-muted-foreground mb-2">Acciones</p>
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
        </div>
      </ScrollArea>
    </div>
  );
}

export const rendicionesConfig: DomainConfig = {
  id: "rendiciones",
  label: "Rendiciones",
  paginationMode: "server",
  searchPlaceholder: "Buscar convenio, BIP o ejecutor...",
  filters: [],
  columns: [
    { key: "ipr_codigo_bip", label: "BIP", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "agreement_number", label: "Convenio", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "S/N")}</span> },
    { key: "renderer_name", label: "Ejecutor", render: (v) => <span className="text-xs line-clamp-1">{String(v ?? "-")}</span> },
    {
      key: "state_code", label: "Estado",
      render: (_, row) => {
        const r = row as RendicionItem;
        const color = r.state_code ? stateBadgeColor[r.state_code] ?? "" : "";
        return (
          <Badge variant="outline" className={`text-[10px] ${color}`}>
            {r.state_label ?? "-"}
          </Badge>
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
    { key: "agreement_total_amount", label: "Monto", render: (v) => <span className="text-xs font-mono tabular-nums">{formatCLP(v as number)}</span> },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    if (params.get("search")) apiParams.set("search", params.get("search")!);

    const response = await api.get<PaginatedResponse<RendicionItem>>(`/api/dgi/data/rendiciones?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: RendicionDetailPanel,
};
