"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { AlertCard } from "@/components/alert-card";
import { FilterBar } from "@/components/filter-bar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Download } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import type { PaginatedResponse, AlertaListItem } from "@/types";

const CSV_COLUMNS = [
  { key: "severity", label: "Severidad" },
  { key: "message", label: "Mensaje" },
  { key: "subject_label", label: "Sujeto" },
  { key: "triggered_at", label: "Fecha" },
];

const NIVEL_OPTIONS = [
  { value: "CRITICO", label: "Crítico" },
  { value: "ALTO", label: "Alto" },
  { value: "ATENCION", label: "Atención" },
  { value: "INFO", label: "Info" },
];

const TIPO_OPTIONS = [
  { value: "COMPROMISO_VENCIDO", label: "Compromiso Vencido" },
  { value: "COMPROMISO_PROXIMO", label: "Compromiso Próximo" },
  { value: "PROBLEMA_CRITICO", label: "Problema Crítico" },
  { value: "IPR_SIN_ACTIVIDAD", label: "IPR Sin Actividad" },
  { value: "PRESUPUESTO", label: "Presupuesto" },
];

export default function AlertasPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [data, setData] = useState<PaginatedResponse<AlertaListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const nivel = searchParams.get("nivel") ?? "";
  const tipo = searchParams.get("tipo") ?? "";
  const soloActivas = searchParams.get("activas") !== "0";
  const dateFrom = searchParams.get("date_from") ?? "";
  const dateTo = searchParams.get("date_to") ?? "";

  const filterValues: Record<string, string> = {
    nivel,
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
    router.push(buildUrl({ [key]: value }));
  };

  const handleClear = () => {
    router.push(pathname);
  };

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams();
    params.set("page_size", "50");
    if (nivel) params.set("severity", nivel);
    if (tipo) params.set("alert_type", tipo);
    if (!soloActivas) params.set("active_only", "false");
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);

    queueMicrotask(() => {
      if (active) setIsLoading(true);
    });

    api
      .get<PaginatedResponse<AlertaListItem>>(`/api/alertas?${params.toString()}`)
      .then((response) => {
        if (active) setData(response);
      })
      .catch(() => {
        if (active) setData(null);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [nivel, tipo, soloActivas, dateFrom, dateTo]);

  const handleAttend = async (id: string) => {
    try {
      await api.post(`/api/alertas/${id}/atender`, {});
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          items: prev.items.map((a) =>
            a.id === id
              ? { ...a, attended_at: new Date().toISOString() }
              : a
          ),
        };
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al atender alerta");
    }
  };

  const handleViewSubject = (type: string, subjectId: string) => {
    if (type === "ipr" || type === "IPR" || type === "core.ipr") {
      router.push(`/ipr/${subjectId}`);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Alertas"
        description="Alertas y notificaciones del sistema"
        actions={
          <Button variant="outline" size="sm" onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "alertas")}>
            <Download className="size-4 mr-1" />CSV
          </Button>
        }
      />

      <FilterBar
        filters={[
          { key: "nivel", label: "Nivel", options: NIVEL_OPTIONS },
          { key: "tipo", label: "Tipo", options: TIPO_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
      />

      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground whitespace-nowrap">Fecha:</span>
        <Input type="date" className="h-8 w-36 text-xs" value={dateFrom} onChange={(e) => router.push(buildUrl({ date_from: e.target.value }))} />
        <span className="text-xs text-muted-foreground">—</span>
        <Input type="date" className="h-8 w-36 text-xs" value={dateTo} onChange={(e) => router.push(buildUrl({ date_to: e.target.value }))} />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="rounded-xl border bg-card p-8 text-center">
          <EmptyState compact title="No hay alertas para los filtros seleccionados." />
        </div>
      ) : (
        <div className="space-y-3">
          {data.items.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onAttend={handleAttend}
              onViewSubject={handleViewSubject}
            />
          ))}
          <p className="text-xs text-muted-foreground text-right">
            {data.total} alerta{data.total !== 1 ? "s" : ""} en total
          </p>
        </div>
      )}
    </div>
  );
}
