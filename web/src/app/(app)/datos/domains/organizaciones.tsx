import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X } from "lucide-react";
import type { PaginatedResponse } from "@/types";
import type { DomainConfig } from "./types";

interface OrganizacionItem {
  id: string;
  code: string;
  name: string;
  short_name: string | null;
  org_type: string | null;
  parent_name: string | null;
  rut: string | null;
  user_count: number;
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-28">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

function OrgDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const o = item as OrganizacionItem;
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">{o.code}</p>
          <h3 className="text-sm font-semibold leading-tight">{o.name}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          {o.short_name && <><DetailRow label="Nombre corto" value={o.short_name} /><Separator /></>}
          <DetailRow label="Tipo" value={o.org_type ?? "-"} />
          <Separator />
          <DetailRow label="Organización padre" value={o.parent_name ?? "-"} />
          <Separator />
          <DetailRow label="RUT" value={o.rut ? <span className="font-mono">{o.rut}</span> : "-"} />
          <Separator />
          <DetailRow label="Usuarios" value={<span className="font-semibold">{o.user_count}</span>} />
        </div>
      </ScrollArea>
    </div>
  );
}

export const organizacionesConfig: DomainConfig = {
  id: "organizaciones",
  label: "Organizaciones",
  paginationMode: "server",
  searchPlaceholder: "Buscar organización...",
  filters: [],
  columns: [
    { key: "code", label: "Código", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "name", label: "Nombre", render: (v) => <span className="text-xs font-medium line-clamp-1">{String(v ?? "")}</span> },
    { key: "org_type", label: "Tipo", render: (v) => v ? <Badge variant="outline" className="text-[10px] px-1.5 py-0">{String(v)}</Badge> : <span className="text-muted-foreground text-xs">-</span> },
    { key: "parent_name", label: "Padre", render: (v) => <span className="text-xs text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "user_count", label: "Usuarios", render: (v) => <span className="text-xs font-mono tabular-nums">{String(v ?? 0)}</span> },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    if (params.get("search")) apiParams.set("search", params.get("search")!);

    const response = await api.get<PaginatedResponse<OrganizacionItem>>(`/api/dgi/data/organizaciones?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: OrgDetailPanel,
};
