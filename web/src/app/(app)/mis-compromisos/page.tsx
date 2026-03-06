"use client";

import { useEffect, useState, useMemo } from "react";
import { api } from "@/lib/api";
import { KpiCard } from "@/components/kpi-card";
import { DataTable } from "@/components/data-table";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { Input } from "@/components/ui/input";
import type { KPICardData, CompromisoListItem } from "@/types";

interface CompromisoGroup {
  label: string;
  count: number;
  items: CompromisoListItem[];
}

interface MisCompromisosData {
  kpis: KPICardData[];
  groups: CompromisoGroup[];
}

const groupColors: Record<string, string> = {
  "Vencidos": "text-red-600",
  "Esta Semana": "text-amber-600",
  "Pendientes": "text-blue-600",
};

const PAGE_SIZE = 10;

export default function MisCompromisosPage() {
  const [data, setData] = useState<MisCompromisosData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [groupPages, setGroupPages] = useState<Record<string, number>>({});

  useEffect(() => {
    api
      .get<MisCompromisosData>("/api/dashboard/mis-compromisos")
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, []);

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
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Mis Compromisos</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Vista personal de compromisos asignados
        </p>
      </div>

      {/* KPIs */}
      {isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {data?.kpis.map((kpi, i) => (
            <KpiCard key={i} label={kpi.label} value={kpi.value} sublabel={kpi.sublabel} color={kpi.color} />
          ))}
        </div>
      )}

      {/* Búsqueda */}
      {!isLoading && data && (
        <Input
          placeholder="Buscar por descripción o BIP..."
          value={searchQuery}
          onChange={(e) => { setSearchQuery(e.target.value); setGroupPages({}); }}
          className="h-9 w-full sm:w-72"
        />
      )}

      {/* Grupos de compromisos */}
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : (
        data?.groups.map((group) => {
          const filtered = searchQuery
            ? group.items.filter((item) =>
                item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (item.ipr_codigo_bip ?? "").toLowerCase().includes(searchQuery.toLowerCase())
              )
            : group.items;
          const currentPage = groupPages[group.label] ?? 1;
          const totalPages = Math.max(Math.ceil(filtered.length / PAGE_SIZE), 1);
          const paged = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

          return (
            <div key={group.label}>
              <h2 className={`text-lg font-semibold mb-3 ${groupColors[group.label] ?? ""}`}>
                {group.label}
                {filtered.length > 0 && (
                  <span className="ml-2 text-sm font-normal text-muted-foreground">
                    ({filtered.length})
                  </span>
                )}
              </h2>
              {filtered.length === 0 ? (
                <p className="text-sm text-muted-foreground py-2">
                  No hay compromisos en esta categoría.
                </p>
              ) : (
                <DataTable
                  columns={columns}
                  data={paged}
                  page={currentPage}
                  totalPages={totalPages}
                  total={filtered.length}
                  onPageChange={(p) => setGroupPages((prev) => ({ ...prev, [group.label]: p }))}
                  isLoading={false}
                />
              )}
            </div>
          );
        })
      )}
    </div>
  );
}
