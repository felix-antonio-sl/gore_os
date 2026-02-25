import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PaginatedResponse, PresupuestoListItem } from "@/types";
import type { DomainConfig } from "./types";

function formatCLP(v: number | null | undefined): string {
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

function PresupuestoDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const p = item as PresupuestoListItem;
  const execPct = p.execution_pct ?? 0;

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">{p.code}</p>
          <h3 className="text-sm font-semibold leading-tight line-clamp-2">{p.name}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="División" value={p.division_name ?? "-"} />
          <Separator />
          <DetailRow label="Año fiscal" value={p.fiscal_year} />
          <Separator />
          <DetailRow label="Tipo programa" value={p.program_type_label ?? "-"} />
          <Separator />
          <DetailRow label="Subtítulo" value={p.subtitle_label ?? "-"} />
          <Separator />
          <DetailRow label="Monto inicial" value={<span className="font-mono tabular-nums">{formatCLP(p.initial_amount)}</span>} />
          <Separator />
          <DetailRow label="Monto actual" value={<span className="font-mono tabular-nums">{formatCLP(p.current_amount)}</span>} />
          <Separator />
          <DetailRow label="Comprometido" value={<span className="font-mono tabular-nums">{formatCLP(p.committed_amount)}</span>} />
          <Separator />
          <DetailRow label="Devengado" value={<span className="font-mono tabular-nums">{formatCLP(p.accrued_amount)}</span>} />
          <Separator />
          <DetailRow label="Pagado" value={<span className="font-mono tabular-nums font-semibold">{formatCLP(p.paid_amount)}</span>} />
          <Separator />
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Ejecución</span>
              <span className="font-mono font-semibold">{execPct}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className={cn("h-full rounded-full", execPct >= 70 ? "bg-green-600" : execPct >= 40 ? "bg-amber-400" : "bg-red-500")}
                style={{ width: `${Math.min(100, execPct)}%` }}
              />
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}

export const presupuestoConfig: DomainConfig = {
  id: "presupuesto",
  label: "Presupuesto",
  paginationMode: "server",
  searchPlaceholder: "Buscar programa...",
  filters: [
    {
      key: "fiscal_year", label: "Año",
      options: [
        { value: "2026", label: "2026" },
        { value: "2025", label: "2025" },
        { value: "2024", label: "2024" },
      ],
    },
  ],
  columns: [
    { key: "code", label: "Código", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "name", label: "Nombre", render: (v) => <span className="text-xs font-medium line-clamp-1 max-w-xs">{String(v ?? "")}</span> },
    { key: "division_name", label: "División", render: (v) => <span className="text-xs text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "fiscal_year", label: "Año", render: (v) => <span className="text-xs tabular-nums">{String(v ?? "-")}</span> },
    { key: "paid_amount", label: "Pagado", render: (v) => <span className="text-xs font-mono tabular-nums">{formatCLP(v as number)}</span> },
    {
      key: "execution_pct", label: "Ejec.",
      render: (v) => {
        const pct = Number(v ?? 0);
        return (
          <span className={cn("text-xs font-mono font-semibold tabular-nums", pct >= 70 ? "text-green-600" : pct >= 40 ? "text-amber-600" : "text-red-600")}>
            {pct}%
          </span>
        );
      },
    },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    if (params.get("fiscal_year")) apiParams.set("fiscal_year", params.get("fiscal_year")!);
    if (params.get("search")) apiParams.set("search", params.get("search")!);

    const response = await api.get<PaginatedResponse<PresupuestoListItem>>(`/api/presupuesto?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: PresupuestoDetailPanel,
};
