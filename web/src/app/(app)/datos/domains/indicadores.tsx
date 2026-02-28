import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TrendingUp, TrendingDown, Minus, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";
import type { DGIIndicator } from "@/types";
import type { DomainConfig } from "./types";

const signalColors: Record<string, string> = {
  VERDE: "bg-green-600",
  AMARILLO: "bg-amber-400",
  ROJO: "bg-red-600",
};

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

function IndicadorDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const ind = item as DGIIndicator;
  const pct = ind.current_value !== null && ind.target_value && ind.target_value > 0
    ? Math.min(100, Math.round((ind.current_value / ind.target_value) * 100))
    : null;

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
        </div>
      </ScrollArea>
    </div>
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
      options: [
        { value: "GESTION", label: "Gestión" },
        { value: "PRESUPUESTO", label: "Presupuesto" },
        { value: "PROCESO", label: "Proceso" },
        { value: "RESULTADO", label: "Resultado" },
        { value: "TD", label: "Transform. Digital" },
      ],
    },
    {
      key: "signal", label: "Señal",
      options: [
        { value: "VERDE", label: "Verde" },
        { value: "AMARILLO", label: "Amarillo" },
        { value: "ROJO", label: "Rojo" },
      ],
    },
  ],
  columns: [
    { key: "code", label: "Código", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "name", label: "Nombre", render: (v) => <span className="text-xs font-medium leading-snug">{String(v ?? "")}</span> },
    { key: "dimension", label: "Dimensión", render: (v) => <Badge variant="secondary" className="text-[10px] px-1.5 py-0">{String(v ?? "-")}</Badge> },
    {
      key: "current_value", label: "Valor",
      render: (value, row) => {
        const ind = row as DGIIndicator;
        return <span className="text-xs font-mono tabular-nums">{value !== null ? String(value) : "-"}{ind.unit ? <span className="text-muted-foreground ml-0.5">{ind.unit}</span> : null}</span>;
      },
    },
    {
      key: "signal", label: "Señal",
      render: (_, row) => {
        const ind = row as DGIIndicator;
        return <div className="flex items-center gap-1.5"><SignalDot signal={ind.signal} /><TrendIcon trend={ind.trend} /></div>;
      },
    },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    if (params.get("dimension")) apiParams.set("dimension", params.get("dimension")!);

    const data = await api.get<DGIIndicator[]>(`/api/dgi/data/indicators?${apiParams.toString()}`);

    // Client-side filter + paginate
    const search = params.get("search") ?? "";
    const signal = params.get("signal") ?? "";
    let filtered = data;
    if (signal) filtered = filtered.filter((i) => i.signal === signal);
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
};
