import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X } from "lucide-react";
import type { PaginatedResponse } from "@/types";
import type { DomainConfig } from "./types";

interface RendicionItem {
  id: string;
  agreement_number: string | null;
  renderer_name: string | null;
  state_label: string | null;
  period_start: string | null;
  period_end: string | null;
  submitted_at: string | null;
  agreement_total_amount: number | null;
}

function formatDate(s: string | null): string {
  if (!s) return "-";
  try {
    return new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(s));
  } catch { return s; }
}

function formatCLP(v: number | null): string {
  if (v == null) return "-";
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", notation: "compact", maximumFractionDigits: 1 }).format(v);
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-28">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

function RendicionDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const r = item as RendicionItem;
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">Convenio {r.agreement_number ?? "S/N"}</p>
          <h3 className="text-sm font-semibold leading-tight">{r.renderer_name ?? "Sin ejecutor"}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Estado" value={r.state_label ?? "-"} />
          <Separator />
          <DetailRow label="Ejecutor" value={r.renderer_name ?? "-"} />
          <Separator />
          <DetailRow label="Período inicio" value={formatDate(r.period_start)} />
          <Separator />
          <DetailRow label="Período fin" value={formatDate(r.period_end)} />
          <Separator />
          <DetailRow label="Enviado" value={formatDate(r.submitted_at)} />
          <Separator />
          <DetailRow label="Monto convenio" value={<span className="font-mono tabular-nums">{formatCLP(r.agreement_total_amount)}</span>} />
        </div>
      </ScrollArea>
    </div>
  );
}

export const rendicionesConfig: DomainConfig = {
  id: "rendiciones",
  label: "Rendiciones",
  paginationMode: "server",
  searchPlaceholder: "Buscar convenio o ejecutor...",
  filters: [],
  columns: [
    { key: "agreement_number", label: "Convenio", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "S/N")}</span> },
    { key: "renderer_name", label: "Ejecutor", render: (v) => <span className="text-xs line-clamp-1">{String(v ?? "-")}</span> },
    { key: "state_label", label: "Estado", render: (v) => <span className="text-xs">{String(v ?? "-")}</span> },
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
