import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X } from "lucide-react";
import type { PaginatedResponse } from "@/types";
import type { DomainConfig } from "./types";

interface TerritorioItem {
  id: string;
  code: string;
  name: string;
  territory_type: string | null;
  parent_name: string | null;
  population: number | null;
  area_km2: number | null;
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-28">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

function TerritorioDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const t = item as TerritorioItem;
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">{t.code}</p>
          <h3 className="text-sm font-semibold leading-tight">{t.name}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Tipo" value={t.territory_type ?? "-"} />
          <Separator />
          <DetailRow label="Pertenece a" value={t.parent_name ?? "-"} />
          <Separator />
          <DetailRow
            label="Población"
            value={t.population != null
              ? <span className="font-mono tabular-nums">{t.population.toLocaleString("es-CL")} hab.</span>
              : "-"}
          />
          <Separator />
          <DetailRow
            label="Superficie"
            value={t.area_km2 != null
              ? <span className="font-mono tabular-nums">{t.area_km2.toLocaleString("es-CL")} km²</span>
              : "-"}
          />
        </div>
      </ScrollArea>
    </div>
  );
}

export const territorioConfig: DomainConfig = {
  id: "territorio",
  label: "Territorio",
  paginationMode: "server",
  searchPlaceholder: "Buscar territorio...",
  filters: [],
  columns: [
    { key: "code", label: "Código", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "name", label: "Nombre", render: (v) => <span className="text-xs font-medium">{String(v ?? "")}</span> },
    { key: "territory_type", label: "Tipo", render: (v) => v ? <Badge variant="outline" className="text-[10px] px-1.5 py-0">{String(v)}</Badge> : <span className="text-muted-foreground text-xs">-</span> },
    { key: "parent_name", label: "Pertenece a", render: (v) => <span className="text-xs text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "population", label: "Población", render: (v) => <span className="text-xs font-mono tabular-nums">{v != null ? Number(v).toLocaleString("es-CL") : "-"}</span> },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    if (params.get("search")) apiParams.set("search", params.get("search")!);

    const response = await api.get<PaginatedResponse<TerritorioItem>>(`/api/dgi/data/territorio?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: TerritorioDetailPanel,
};
