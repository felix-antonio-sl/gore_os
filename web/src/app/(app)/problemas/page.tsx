"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import type { PaginatedResponse, ProblemaListItem } from "@/types";

const ESTADO_OPTIONS = [
  { value: "ABIERTO", label: "Abierto" },
  { value: "EN_GESTION", label: "En Gestión" },
  { value: "RESUELTO", label: "Resuelto" },
  { value: "CERRADO_SIN_RESOLVER", label: "Cerrado sin Resolver" },
];

const TIPO_OPTIONS = [
  { value: "TECNICO", label: "Técnico" },
  { value: "FINANCIERO", label: "Financiero" },
  { value: "LEGAL", label: "Legal" },
  { value: "ADMINISTRATIVO", label: "Administrativo" },
  { value: "AMBIENTAL", label: "Ambiental" },
  { value: "SOCIAL", label: "Social" },
];

export default function ProblemasPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [data, setData] = useState<PaginatedResponse<ProblemaListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const page = Number(searchParams.get("page") ?? "1");
  const estado = searchParams.get("estado") ?? "";
  const tipo = searchParams.get("tipo") ?? "";
  const search = searchParams.get("search") ?? "";

  const filterValues: Record<string, string> = {
    estado,
    tipo,
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
    if (estado) params.set("state", estado);
    if (tipo) params.set("problem_type", tipo);
    if (search) params.set("search", search);

    api
      .get<PaginatedResponse<ProblemaListItem>>(`/api/problemas?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, estado, tipo, search]);

  const columns = [
    {
      key: "days_open",
      label: "Días abierto",
      render: (v: unknown) => (
        <span className="text-xs tabular-nums text-muted-foreground">{String(v ?? 0)}d</span>
      ),
    },
    {
      key: "ipr_codigo_bip",
      label: "BIP",
      render: (v: unknown) => (
        <span className="text-xs font-mono text-muted-foreground">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "problem_type_label",
      label: "Tipo",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "-")}</Badge>
      ),
    },
    {
      key: "impact_label",
      label: "Impacto",
      render: (v: unknown) => {
        const val = String(v ?? "-");
        const colorMap: Record<string, string> = {
          ALTO: "border-red-500 text-red-600",
          MEDIO: "border-orange-500 text-orange-600",
          BAJO: "border-gray-400 text-gray-600",
        };
        return (
          <Badge variant="outline" className={`text-xs ${colorMap[val.toUpperCase()] ?? ""}`}>
            {val}
          </Badge>
        );
      },
    },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Problemas</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Registro de problemas e impedimentos en IPRs
        </p>
      </div>

      <FilterBar
        filters={[
          { key: "estado", label: "Estado", options: ESTADO_OPTIONS },
          { key: "tipo", label: "Tipo", options: TIPO_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar problema..."
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
        isLoading={isLoading}
      />
    </div>
  );
}
