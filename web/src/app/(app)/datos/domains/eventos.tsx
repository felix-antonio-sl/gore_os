import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X } from "lucide-react";
import type { PaginatedResponse } from "@/types";
import type { DomainConfig } from "./types";

interface EventoItem {
  id: string;
  occurred_at: string;
  event_type: string;
  event_type_label: string;
  subject_type: string;
  subject_id: string;
  actor_name: string | null;
  summary: string | null;
}

function formatDateTime(s: string): string {
  try {
    return new Intl.DateTimeFormat("es-CL", {
      day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    }).format(new Date(s));
  } catch { return s; }
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-28">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

function EventoDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const e = item as EventoItem;
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] text-muted-foreground">{formatDateTime(e.occurred_at)}</p>
          <h3 className="text-sm font-semibold leading-tight">{e.event_type_label}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Tipo evento" value={<Badge variant="outline" className="text-[10px]">{e.event_type}</Badge>} />
          <Separator />
          <DetailRow label="Entidad" value={<span className="font-mono text-[11px]">{e.subject_type}</span>} />
          <Separator />
          <DetailRow label="ID entidad" value={<span className="font-mono text-[11px] break-all">{e.subject_id.slice(0, 8)}…</span>} />
          <Separator />
          <DetailRow label="Actor" value={e.actor_name ?? "Sistema"} />
          {e.summary && (
            <>
              <Separator />
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground font-medium">Resumen</p>
                <p className="text-xs leading-relaxed">{e.summary}</p>
              </div>
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

// Helper to get default date range (last 30 days)
function defaultDateFrom(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().split("T")[0];
}

function defaultDateTo(): string {
  return new Date().toISOString().split("T")[0];
}

export const eventosConfig: DomainConfig = {
  id: "eventos",
  label: "Eventos",
  paginationMode: "server",
  searchPlaceholder: "Buscar tipo entidad...",
  filters: [
    {
      key: "subject_type", label: "Entidad",
      options: [
        { value: "core.ipr", label: "IPR" },
        { value: "core.operational_commitment", label: "Compromiso" },
        { value: "core.ipr_problem", label: "Problema" },
        { value: "core.alert", label: "Alerta" },
        { value: "core.agreement", label: "Convenio" },
        { value: "core.budget_program", label: "Presupuesto" },
      ],
    },
  ],
  columns: [
    { key: "occurred_at", label: "Fecha", render: (v) => <span className="text-[11px] tabular-nums">{formatDateTime(String(v ?? ""))}</span> },
    { key: "event_type_label", label: "Tipo", render: (v) => <Badge variant="outline" className="text-[10px] px-1.5 py-0">{String(v ?? "-")}</Badge> },
    { key: "subject_type", label: "Entidad", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "actor_name", label: "Actor", render: (v) => <span className="text-xs">{String(v ?? "Sistema")}</span> },
    { key: "summary", label: "Resumen", render: (v) => <span className="text-xs text-muted-foreground line-clamp-1">{String(v ?? "-")}</span> },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    // Date range — REQUIRED for partitioned table
    apiParams.set("date_from", params.get("date_from") ?? defaultDateFrom());
    apiParams.set("date_to", params.get("date_to") ?? defaultDateTo());
    if (params.get("subject_type")) apiParams.set("subject_type", params.get("subject_type")!);
    if (params.get("event_type")) apiParams.set("event_type", params.get("event_type")!);
    if (params.get("search")) apiParams.set("search", params.get("search")!);

    const response = await api.get<PaginatedResponse<EventoItem>>(`/api/dgi/data/eventos?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: EventoDetailPanel,
};
