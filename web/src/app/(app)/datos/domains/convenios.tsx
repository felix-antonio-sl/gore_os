import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { StatusBadge } from "@/components/status-badge";
import { X } from "lucide-react";
import type { PaginatedResponse, ConvenioListItem } from "@/types";
import type { DomainConfig } from "./types";

function formatCLP(v: number | null | undefined): string {
  if (v == null) return "-";
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", notation: "compact", maximumFractionDigits: 1 }).format(v);
}

function formatDate(s: string | null | undefined): string {
  if (!s) return "-";
  try {
    return new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(s));
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

function ConvenioDetailPanel({ item, onClose }: { item: unknown; onClose: () => void }) {
  const c = item as ConvenioListItem;
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">{c.agreement_number ?? "S/N"}</p>
          <h3 className="text-sm font-semibold leading-tight">{c.agreement_type_label}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Estado" value={<StatusBadge status={c.state} size="sm" />} />
          <Separator />
          <DetailRow label="Cedente" value={c.giver_name ?? "-"} />
          <Separator />
          <DetailRow label="Receptor" value={c.receiver_name ?? "-"} />
          <Separator />
          <DetailRow label="IPR" value={c.ipr_codigo_bip ? <span className="font-mono">{c.ipr_codigo_bip}</span> : "-"} />
          <Separator />
          <DetailRow label="Monto total" value={<span className="font-mono tabular-nums font-semibold">{formatCLP(c.total_amount)}</span>} />
          <Separator />
          <DetailRow label="Firmado" value={formatDate(c.signed_at)} />
          <Separator />
          <DetailRow label="Vigente desde" value={formatDate(c.valid_from)} />
          <Separator />
          <DetailRow label="Vence" value={formatDate(c.valid_to)} />
          <Separator />
          <DetailRow
            label="Cuotas"
            value={
              <span className="font-mono">
                {c.paid_installments}/{c.installment_count} pagadas
              </span>
            }
          />
          {c.days_to_expiry !== null && (
            <>
              <Separator />
              <DetailRow
                label="Días para vencer"
                value={
                  <span className={c.days_to_expiry <= 30 ? "text-red-600 font-semibold" : ""}>
                    {c.days_to_expiry}d
                  </span>
                }
              />
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

export const conveniosConfig: DomainConfig = {
  id: "convenios",
  label: "Convenios",
  paginationMode: "server",
  searchPlaceholder: "Buscar convenio...",
  filters: [
    {
      key: "estado", label: "Estado",
      options: [
        { value: "BORRADOR", label: "Borrador" },
        { value: "VIGENTE", label: "Vigente" },
        { value: "VENCIDO", label: "Vencido" },
        { value: "TERMINADO", label: "Terminado" },
      ],
    },
    {
      key: "tipo", label: "Tipo",
      options: [
        { value: "MANDATO", label: "Mandato" },
        { value: "TRANSFERENCIA", label: "Transferencia" },
        { value: "COLABORACION", label: "Colaboración" },
      ],
    },
  ],
  columns: [
    { key: "agreement_number", label: "N°", render: (v) => <span className="text-[11px] font-mono text-muted-foreground">{String(v ?? "S/N")}</span> },
    { key: "agreement_type_label", label: "Tipo", render: (v) => <Badge variant="outline" className="text-[10px] px-1.5 py-0">{String(v ?? "-")}</Badge> },
    { key: "state", label: "Estado", render: (v) => <StatusBadge status={String(v ?? "")} size="sm" /> },
    { key: "giver_name", label: "Cedente", render: (v) => <span className="text-xs line-clamp-1">{String(v ?? "-")}</span> },
    { key: "total_amount", label: "Monto", render: (v) => <span className="text-xs font-mono tabular-nums">{formatCLP(v as number)}</span> },
    {
      key: "installment_count", label: "Cuotas",
      render: (_, row) => {
        const c = row as ConvenioListItem;
        return <span className="text-xs font-mono">{c.paid_installments}/{c.installment_count}</span>;
      },
    },
  ],
  fetchData: async (params) => {
    const apiParams = new URLSearchParams();
    apiParams.set("page", params.get("page") ?? "1");
    apiParams.set("page_size", "25");
    if (params.get("estado")) apiParams.set("state", params.get("estado")!);
    if (params.get("tipo")) apiParams.set("agreement_type", params.get("tipo")!);
    if (params.get("search")) apiParams.set("search", params.get("search")!);

    const response = await api.get<PaginatedResponse<ConvenioListItem>>(`/api/convenios?${apiParams.toString()}`);
    return { items: response.items, total: response.total, totalPages: response.total_pages };
  },
  DetailPanel: ConvenioDetailPanel,
};
