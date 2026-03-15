"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download, X } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import { DeadlineCell } from "@/components/deadline-cell";
import type { PaginatedResponse, CompromisoListItem } from "@/types";

const CSV_COLUMNS = [
  { key: "code", label: "Código" },
  { key: "description", label: "Descripción" },
  { key: "responsible_name", label: "Responsable" },
  { key: "state", label: "Estado" },
  { key: "due_date", label: "Fecha Límite" },
  { key: "days_remaining", label: "Días Restantes" },
];

const ESTADO_OPTIONS = [
  { value: "PENDIENTE", label: "Pendiente" },
  { value: "EN_PROGRESO", label: "En Progreso" },
  { value: "COMPLETADO", label: "Completado" },
  { value: "VERIFICADO", label: "Verificado" },
  { value: "VENCIDO", label: "Vencido" },
  { value: "CANCELADO", label: "Cancelado" },
];

interface Props {
  onItemClick: (item: CompromisoListItem) => void;
  refreshKey: number;
  onRefresh: () => void;
}

export function CompromisosListView({ onItemClick, refreshKey }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<CompromisoListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const page = Number(searchParams.get("page") ?? "1");
  const estado = searchParams.get("estado") ?? "";
  const division = searchParams.get("division") ?? "";
  const responsibleId = searchParams.get("responsible_id") ?? "";
  const soloMios = searchParams.get("solo_mios") === "1";
  const overdue = searchParams.get("overdue") === "true";
  const dateFrom = searchParams.get("date_from") ?? "";
  const dateTo = searchParams.get("date_to") ?? "";

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) params.delete(k);
        else params.set(k, String(v));
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (estado) params.set("state", estado);
    if (division) params.set("division_id", division);
    if (responsibleId) params.set("responsible_id", responsibleId);
    else if (soloMios && user?.id) params.set("responsible_id", user.id);
    if (overdue) params.set("overdue", "true");
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);

    api
      .get<PaginatedResponse<CompromisoListItem>>(`/api/compromisos?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, estado, division, responsibleId, soloMios, overdue, dateFrom, dateTo, user?.id, refreshKey]);

  const columns = [
    {
      key: "days_remaining",
      label: "Urgencia",
      render: (_: unknown, row: unknown) => {
        const r = row as CompromisoListItem;
        return <TemporalIndicator daysRemaining={r.days_remaining} state={r.state} />;
      },
    },
    {
      key: "description",
      label: "Descripción",
      render: (v: unknown) => (
        <span className="font-medium line-clamp-1 max-w-xs">{String(v ?? "")}</span>
      ),
    },
    {
      key: "ipr_codigo_bip",
      label: "BIP",
      render: (v: unknown) => (
        <span className="text-xs font-mono text-muted-foreground">{String(v ?? "-")}</span>
      ),
    },
    { key: "responsible_name", label: "Responsable" },
    {
      key: "due_date",
      label: "Vence",
      render: (v: unknown, row: unknown) => {
        const r = row as CompromisoListItem;
        return <DeadlineCell date={v ? String(v) : null} daysRemaining={r.days_remaining} />;
      },
    },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  return (
    <div className="space-y-4">
      {responsibleId && (
        <div className="flex items-center gap-2 text-sm bg-muted/50 rounded-lg px-3 py-2">
          <span className="text-muted-foreground">Filtrando por responsable</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2"
            onClick={() => router.push(pathname)}
          >
            <X className="size-3.5 mr-1" />
            Limpiar
          </Button>
        </div>
      )}

      <FilterBar
        filters={[
          { key: "estado", label: "Estado", options: ESTADO_OPTIONS },
          { key: "division", label: "División", options: [] },
        ]}
        values={{ estado, division }}
        onChange={(key, value) => router.push(buildUrl({ [key]: value, page: 1 }))}
        onClear={() => router.push(pathname)}
        searchPlaceholder="Buscar compromiso..."
      />

      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground whitespace-nowrap">Vencimiento:</span>
        <Input
          type="date"
          className="h-8 w-36 text-xs"
          value={dateFrom}
          onChange={(e) => router.push(buildUrl({ date_from: e.target.value, page: 1 }))}
        />
        <span className="text-xs text-muted-foreground">—</span>
        <Input
          type="date"
          className="h-8 w-36 text-xs"
          value={dateTo}
          onChange={(e) => router.push(buildUrl({ date_to: e.target.value, page: 1 }))}
        />
        <Button
          variant="outline"
          size="sm"
          className="ml-auto"
          onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "compromisos")}
        >
          <Download className="size-4 mr-1" />
          CSV
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        page={page}
        totalPages={data?.total_pages ?? 1}
        total={data?.total ?? 0}
        onPageChange={(p) => router.push(buildUrl({ page: p }))}
        onRowClick={(row) => onItemClick(row as CompromisoListItem)}
        isLoading={isLoading}
      />
    </div>
  );
}
