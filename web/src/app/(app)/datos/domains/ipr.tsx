import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatCurrency } from "@/lib/format";
import type { PaginatedResponse, IPRListItem } from "@/types";
import type { DomainConfig } from "./types";

const alertLevelColors: Record<string, string> = {
  CRITICO: "bg-red-600 text-white",
  ALTO: "bg-orange-500 text-white",
  ATENCION: "bg-amber-400 text-white",
  INFO: "bg-blue-500 text-white",
};

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-24">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

function IPRDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const ipr = item as IPRListItem;
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">{ipr.codigo_bip}</p>
          <h3 className="text-sm font-semibold leading-tight line-clamp-2">{ipr.name}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Tipo" value={ipr.ipr_type ?? "-"} />
          <Separator />
          <DetailRow label="Estado" value={<StatusBadge status={ipr.status ?? ""} size="sm" />} />
          <Separator />
          <DetailRow label="Sector" value={ipr.investment_sector ?? "-"} />
          <Separator />
          <DetailRow label="Fuente" value={ipr.funding_source ?? "-"} />
          <Separator />
          <DetailRow label="Ejecutor" value={ipr.executor_name ?? "-"} />
          <Separator />
          <DetailRow
            label="Presupuesto"
            value={<span className="font-mono tabular-nums text-xs">{formatCurrency(ipr.total_budget)}</span>}
          />
          <Separator />
          <DetailRow
            label="Alerta"
            value={
              ipr.alert_level ? (
                <Badge className={cn("text-[10px] px-1.5 py-0", alertLevelColors[ipr.alert_level] ?? "bg-gray-300")}>
                  {ipr.alert_level}
                </Badge>
              ) : "-"
            }
          />
          <Separator />
          <DetailRow
            label="Problemas"
            value={
              ipr.has_open_problems
                ? <Badge variant="destructive" className="text-[10px] px-1.5 py-0">Con problemas</Badge>
                : <span className="text-muted-foreground text-xs">Sin problemas</span>
            }
          />
        </div>
      </ScrollArea>
    </div>
  );
}

export const iprConfig: DomainConfig = {
  id: "ipr",
  label: "IPR",
  paginationMode: "server",
  searchPlaceholder: "Buscar por nombre o BIP...",
  filters: [
    {
      key: "tipo", label: "Tipo",
      options: [
        { value: "INFRAESTRUCTURA", label: "Infraestructura" },
        { value: "EQUIPAMIENTO", label: "Equipamiento" },
        { value: "TRANSFERENCIA", label: "Transferencia" },
        { value: "PROGRAMA_SOCIAL", label: "Programa Social" },
        { value: "PROGRAMA_8PCT", label: "Programa 8%" },
        { value: "CONSERVACION", label: "Conservación" },
        { value: "ESTUDIO", label: "Estudio" },
      ],
    },
    {
      key: "estado", label: "Estado",
      options: [
        { value: "EN_FORMULACION", label: "En Formulación" },
        { value: "EN_EJECUCION", label: "En Ejecución" },
        { value: "TERMINADO", label: "Terminado" },
        { value: "CERRADO", label: "Cerrado" },
      ],
    },
    {
      key: "sector", label: "Sector",
      options: [
        { value: "SPORTS", label: "Deportes" },
        { value: "CULTURE", label: "Cultura" },
        { value: "EDUCATION", label: "Educación" },
        { value: "HEALTH", label: "Salud" },
        { value: "INFRASTRUCTURE", label: "Infraestructura" },
      ],
    },
    {
      key: "alert_level", label: "Alerta",
      options: [
        { value: "CRITICO", label: "Crítico" },
        { value: "ALTO", label: "Alto" },
        { value: "ATENCION", label: "Atención" },
        { value: "INFO", label: "Info" },
      ],
    },
  ],
  columns: [
    {
      key: "alert_level", label: "",
      render: (value) => {
        const v = String(value ?? "");
        if (!v || v === "null") return <span className="inline-block size-2 rounded-full bg-transparent" />;
        return <span className={cn("inline-block rounded-full size-2.5", alertLevelColors[v] ?? "bg-gray-300")} title={v} />;
      },
    },
    { key: "codigo_bip", label: "BIP", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "name", label: "Nombre", render: (v) => <span className="text-xs font-medium leading-snug line-clamp-2">{String(v ?? "")}</span> },
    { key: "ipr_type", label: "Tipo", render: (v) => <Badge variant="outline" className="text-[10px] px-1.5 py-0">{String(v ?? "-")}</Badge> },
    { key: "status", label: "Estado", render: (v) => <StatusBadge status={String(v ?? "")} size="sm" /> },
    { key: "total_budget", label: "Presup.", render: (v) => <span className="text-[11px] tabular-nums font-mono">{formatCurrency(v as number | null)}</span> },
  ],
  fetchData: async (params) => {
    // Map domain param keys to API param keys
    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    if (params.get("tipo")) apiParams.set("ipr_type", params.get("tipo")!);
    if (params.get("estado")) apiParams.set("status", params.get("estado")!);
    if (params.get("sector")) apiParams.set("sector", params.get("sector")!);
    if (params.get("alert_level")) apiParams.set("alert_level", params.get("alert_level")!);
    if (params.get("search")) apiParams.set("search", params.get("search")!);

    const response = await api.get<PaginatedResponse<IPRListItem>>(`/api/ipr?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: IPRDetailPanel,
};
