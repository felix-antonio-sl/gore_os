"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import type { ProcessProgressItem, LeanMetrics } from "@/types";

const STATUS_COLORS: Record<string, string> = {
  identificado: "bg-slate-100 text-slate-700",
  en_levantamiento: "bg-blue-100 text-blue-700",
  modelado: "bg-cyan-100 text-cyan-700",
  validado: "bg-amber-100 text-amber-700",
  publicado: "bg-green-100 text-green-700",
  suspendido: "bg-red-100 text-red-700",
};

export default function ProcesoProgresoPage() {
  const [progress, setProgress] = useState<ProcessProgressItem[]>([]);
  const [leanMetrics, setLeanMetrics] = useState<LeanMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<ProcessProgressItem[]>("/api/dgi/processes/progress"),
      api.get<LeanMetrics>("/api/dgi/initiatives/lean-metrics").catch(() => null),
    ])
      .then(([prog, lean]) => {
        setProgress(prog);
        setLeanMetrics(lean);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // Compute DMAIC pipeline summary from lean metrics aging data
  const dmaicSummary = (() => {
    if (!leanMetrics) return null;
    // We don't have per-initiative dmaic phase in lean metrics
    // Show throughput and WIP as DMAIC pipeline proxy
    return {
      throughput: leanMetrics.throughput_30d,
      wip: leanMetrics.wip_count,
      leadTime: leanMetrics.lead_time_avg,
      cycleTime: leanMetrics.cycle_time_avg,
    };
  })();

  const columns = [
    { key: "division_name", label: "División", className: "text-sm font-medium" },
    { key: "total", label: "Total", className: "text-sm text-center font-bold" },
    ...["identificado", "en_levantamiento", "modelado", "validado", "publicado", "suspendido"].map(
      (status) => ({
        key: status,
        label: status.replace(/_/g, " ").replace(/^\w/, (c: string) => c.toUpperCase()),
        className: "text-sm text-center",
        render: (v: unknown) => {
          const count = Number(v ?? 0);
          if (count === 0) return <span className="text-xs text-muted-foreground">&mdash;</span>;
          return (
            <Badge variant="secondary" className={`text-xs ${STATUS_COLORS[status] ?? ""}`}>
              {count}
            </Badge>
          );
        },
      })
    ),
  ];

  // Totals row
  const totals = progress.reduce(
    (acc, row) => ({
      total: acc.total + row.total,
      identificado: acc.identificado + row.identificado,
      en_levantamiento: acc.en_levantamiento + row.en_levantamiento,
      modelado: acc.modelado + row.modelado,
      validado: acc.validado + row.validado,
      publicado: acc.publicado + row.publicado,
      suspendido: acc.suspendido + row.suspendido,
    }),
    { total: 0, identificado: 0, en_levantamiento: 0, modelado: 0, validado: 0, publicado: 0, suspendido: 0 }
  );

  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Progreso de Procesos"
        description="Estado de procesos por división y pipeline DMAIC"
      />

      {/* DMAIC Pipeline Summary */}
      {dmaicSummary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-lg border bg-card p-4">
            <p className="text-xs text-muted-foreground">Throughput (30d)</p>
            <p className="text-2xl font-bold">{dmaicSummary.throughput}</p>
            <p className="text-[11px] text-muted-foreground">Iniciativas completadas</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-xs text-muted-foreground">WIP Activo</p>
            <p className="text-2xl font-bold">{dmaicSummary.wip}</p>
            <p className="text-[11px] text-muted-foreground">En Curso + Revisión</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-xs text-muted-foreground">Lead Time</p>
            <p className="text-2xl font-bold">{dmaicSummary.leadTime !== null ? `${dmaicSummary.leadTime}d` : "\u2014"}</p>
            <p className="text-[11px] text-muted-foreground">Promedio total</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-xs text-muted-foreground">Cycle Time</p>
            <p className="text-2xl font-bold">{dmaicSummary.cycleTime !== null ? `${dmaicSummary.cycleTime}d` : "\u2014"}</p>
            <p className="text-[11px] text-muted-foreground">Promedio ejecución</p>
          </div>
        </div>
      )}

      {/* Process Status by Division */}
      <div className="rounded-xl border bg-card p-4">
        <h3 className="text-sm font-medium mb-4">Estado por División</h3>
        {!loading && progress.length === 0 ? (
          <EmptyState compact title="Sin procesos registrados" />
        ) : (
          <>
            <DataTable
              columns={columns}
              data={progress}
              page={1}
              totalPages={1}
              total={progress.length}
              onPageChange={() => {}}
              isLoading={loading}
            />
            {progress.length > 0 && (
              <div className="mt-3 pt-3 border-t flex items-center gap-4 text-sm">
                <span className="font-medium">Totales:</span>
                <span>{totals.total} procesos</span>
                <span className="text-green-700">{totals.publicado} publicados</span>
                <span className="text-amber-700">{totals.validado} validados</span>
                <span className="text-blue-700">{totals.en_levantamiento + totals.modelado} en progreso</span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
