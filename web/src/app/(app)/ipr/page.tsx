"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import type { PaginatedResponse, IPRListItem } from "@/types";

const IPR_TYPE_OPTIONS = [
  { value: "INFRAESTRUCTURA", label: "Infraestructura" },
  { value: "EQUIPAMIENTO", label: "Equipamiento" },
  { value: "TRANSFERENCIA", label: "Transferencia" },
  { value: "PROGRAMA_SOCIAL", label: "Programa Social" },
  { value: "PROGRAMA_8PCT", label: "Programa 8%" },
  { value: "CONSERVACION", label: "Conservación" },
  { value: "ESTUDIO", label: "Estudio" },
];

const STATUS_OPTIONS = [
  { value: "EN_FORMULACION", label: "En Formulación" },
  { value: "EN_EJECUCION", label: "En Ejecución" },
  { value: "TERMINADO", label: "Terminado" },
  { value: "CERRADO", label: "Cerrado" },
];

const SECTOR_OPTIONS = [
  { value: "SPORTS", label: "Deportes" },
  { value: "CULTURE", label: "Cultura" },
  { value: "EDUCATION", label: "Educación" },
  { value: "HEALTH", label: "Salud" },
  { value: "INFRASTRUCTURE", label: "Infraestructura" },
];

const ALERT_LEVEL_OPTIONS = [
  { value: "CRITICO", label: "Crítico" },
  { value: "ALTO", label: "Alto" },
  { value: "ATENCION", label: "Atención" },
  { value: "INFO", label: "Info" },
];

const alertLevelColors: Record<string, string> = {
  CRITICO: "bg-red-600 text-white",
  ALTO: "bg-orange-500 text-white",
  ATENCION: "bg-amber-400 text-white",
  INFO: "bg-blue-500 text-white",
};

function formatCurrency(value: number | null): string {
  if (value === null) return "-";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export default function IprPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [data, setData] = useState<PaginatedResponse<IPRListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const page = Number(searchParams.get("page") ?? "1");
  const tipo = searchParams.get("tipo") ?? "";
  const estado = searchParams.get("estado") ?? "";
  const sector = searchParams.get("sector") ?? "";
  const alertLevel = searchParams.get("alert_level") ?? "";
  const search = searchParams.get("search") ?? "";

  const filterValues: Record<string, string> = {
    tipo,
    estado,
    sector,
    alert_level: alertLevel,
  };

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) {
          params.delete(k);
        } else {
          params.set(k, String(v));
        }
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  const handleFilterChange = (key: string, value: string) => {
    router.push(buildUrl({ [key]: value, page: 1 }));
  };

  const handleSearchChange = (value: string) => {
    router.push(buildUrl({ search: value, page: 1 }));
  };

  const handleClear = () => {
    router.push(pathname);
  };

  const handlePageChange = (newPage: number) => {
    router.push(buildUrl({ page: newPage }));
  };

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (tipo) params.set("ipr_type", tipo);
    if (estado) params.set("status", estado);
    if (sector) params.set("sector", sector);
    if (alertLevel) params.set("alert_level", alertLevel);
    if (search) params.set("search", search);

    api
      .get<PaginatedResponse<IPRListItem>>(`/api/ipr?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, tipo, estado, sector, alertLevel, search]);

  const columns = [
    {
      key: "alert_level",
      label: "Alerta",
      render: (value: unknown) => {
        const v = String(value ?? "");
        if (!v) return null;
        return (
          <span
            className={`inline-block rounded-full size-3 ${alertLevelColors[v] ?? "bg-gray-300"}`}
            title={v}
          />
        );
      },
    },
    {
      key: "codigo_bip",
      label: "BIP",
      render: (value: unknown) => (
        <span className="text-xs font-mono">{String(value ?? "-")}</span>
      ),
    },
    {
      key: "name",
      label: "Nombre",
      render: (value: unknown) => (
        <span className="font-medium">{String(value ?? "")}</span>
      ),
    },
    {
      key: "ipr_type",
      label: "Tipo",
      render: (value: unknown) => (
        <Badge variant="outline" className="text-xs">
          {String(value ?? "-")}
        </Badge>
      ),
    },
    {
      key: "status",
      label: "Estado",
      render: (value: unknown) => <StatusBadge status={String(value ?? "")} size="sm" />,
    },
    {
      key: "total_budget",
      label: "$",
      render: (value: unknown) => (
        <span className="text-xs text-right tabular-nums">
          {formatCurrency(value as number | null)}
        </span>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold">IPR</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Intervenciones Públicas Regionales
        </p>
      </div>

      <FilterBar
        filters={[
          { key: "tipo", label: "Tipo", options: IPR_TYPE_OPTIONS },
          { key: "estado", label: "Estado", options: STATUS_OPTIONS },
          { key: "sector", label: "Sector", options: SECTOR_OPTIONS },
          { key: "alert_level", label: "Alerta", options: ALERT_LEVEL_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar por nombre o BIP..."
        searchValue={search}
        onSearchChange={handleSearchChange}
      />

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        page={page}
        totalPages={data?.total_pages ?? 1}
        total={data?.total ?? 0}
        onPageChange={handlePageChange}
        onRowClick={(row) => {
          const ipr = row as IPRListItem;
          router.push(`/ipr/${ipr.id}`);
        }}
        isLoading={isLoading}
      />
    </div>
  );
}
