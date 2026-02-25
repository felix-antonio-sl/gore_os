import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X } from "lucide-react";
import type { PaginatedResponse } from "@/types";
import type { DomainConfig } from "./types";

interface PersonaItem {
  id: string;
  names: string;
  paternal_surname: string;
  maternal_surname: string | null;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  organization_name: string | null;
  estamento: string | null;
  position_name: string | null;
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-28">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

function PersonaDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const p = item as PersonaItem;
  const fullName = `${p.names} ${p.paternal_surname}${p.maternal_surname ? ` ${p.maternal_surname}` : ""}`;
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <h3 className="text-sm font-semibold leading-tight">{fullName}</h3>
          {p.email && <p className="text-[10px] text-muted-foreground">{p.email}</p>}
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Organización" value={p.organization_name ?? "-"} />
          <Separator />
          <DetailRow label="Estamento" value={p.estamento ?? "-"} />
          <Separator />
          <DetailRow label="Cargo" value={p.position_name ?? "-"} />
          <Separator />
          <DetailRow label="Email" value={p.email ? <a href={`mailto:${p.email}`} className="text-blue-600 hover:underline">{p.email}</a> : "-"} />
          <Separator />
          <DetailRow label="Teléfono" value={p.phone ?? "-"} />
          <Separator />
          <DetailRow label="Estado" value={p.is_active ? <Badge variant="secondary" className="text-[10px]">Activo</Badge> : <Badge variant="outline" className="text-[10px] text-muted-foreground">Inactivo</Badge>} />
        </div>
      </ScrollArea>
    </div>
  );
}

export const personasConfig: DomainConfig = {
  id: "personas",
  label: "Personas",
  paginationMode: "server",
  searchPlaceholder: "Buscar persona...",
  filters: [],
  columns: [
    {
      key: "names", label: "Nombre",
      render: (_, row) => {
        const p = row as PersonaItem;
        return <span className="text-xs font-medium">{p.names} {p.paternal_surname}</span>;
      },
    },
    { key: "email", label: "Email", render: (v) => <span className="text-xs text-muted-foreground">{String(v ?? "-")}</span> },
    { key: "organization_name", label: "Organización", render: (v) => <span className="text-xs line-clamp-1">{String(v ?? "-")}</span> },
    { key: "estamento", label: "Estamento", render: (v) => v ? <Badge variant="outline" className="text-[10px] px-1.5 py-0">{String(v)}</Badge> : <span className="text-muted-foreground text-xs">-</span> },
    { key: "is_active", label: "Estado", render: (v) => v ? <Badge variant="secondary" className="text-[10px]">Activo</Badge> : <Badge variant="outline" className="text-[10px] text-muted-foreground">Inactivo</Badge> },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    if (params.get("search")) apiParams.set("search", params.get("search")!);

    const response = await api.get<PaginatedResponse<PersonaItem>>(`/api/dgi/data/personas?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: PersonaDetailPanel,
};
