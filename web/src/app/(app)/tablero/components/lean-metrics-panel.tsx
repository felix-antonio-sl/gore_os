"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Activity, Clock, Layers, TrendingUp } from "lucide-react";
import type { LeanMetrics } from "@/types";

interface LeanMetricsPanelProps {
  open: boolean;
}

export function LeanMetricsPanel({ open }: LeanMetricsPanelProps) {
  const [metrics, setMetrics] = useState<LeanMetrics | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    api
      .get<LeanMetrics>("/api/dgi/initiatives/lean-metrics")
      .then(setMetrics)
      .catch(() => setMetrics(null))
      .finally(() => setLoading(false));
  }, [open]);

  if (!open) return null;

  if (loading) {
    return (
      <div className="rounded-xl border bg-card p-4 animate-in fade-in duration-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!metrics) return null;

  const kpis = [
    {
      label: "Throughput (30d)",
      value: metrics.throughput_30d,
      sublabel: `${metrics.throughput_60d} (60d) \u00b7 ${metrics.throughput_90d} (90d)`,
      icon: <TrendingUp className="size-4 text-blue-500" />,
    },
    {
      label: "Lead Time",
      value: metrics.lead_time_avg !== null ? `${metrics.lead_time_avg}d` : "\u2014",
      sublabel: "Promedio creaci\u00f3n a completado",
      icon: <Clock className="size-4 text-purple-500" />,
    },
    {
      label: "Cycle Time",
      value: metrics.cycle_time_avg !== null ? `${metrics.cycle_time_avg}d` : "\u2014",
      sublabel: "Promedio inicio a completado",
      icon: <Activity className="size-4 text-amber-500" />,
    },
    {
      label: "WIP",
      value: metrics.wip_count,
      sublabel: "En Curso + Revisi\u00f3n",
      icon: <Layers className="size-4 text-green-500" />,
    },
  ];

  return (
    <div className="rounded-xl border bg-card p-4 space-y-4 animate-in fade-in duration-200">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="rounded-lg border bg-background p-3 space-y-1">
            <div className="flex items-center gap-2">
              {kpi.icon}
              <span className="text-xs text-muted-foreground">{kpi.label}</span>
            </div>
            <p className="text-2xl font-bold">{kpi.value}</p>
            <p className="text-[11px] text-muted-foreground">{kpi.sublabel}</p>
          </div>
        ))}
      </div>

      {/* Aging table */}
      {metrics.aging.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-muted-foreground mb-2">
            Envejecimiento de Iniciativas Activas
          </h4>
          <div className="space-y-1">
            {metrics.aging.slice(0, 10).map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between text-xs py-1 px-2 rounded hover:bg-muted/50"
              >
                <span className="truncate flex-1">{item.name}</span>
                <div className="flex items-center gap-2 shrink-0 ml-2">
                  <Badge variant="outline" className="text-[10px]">{item.column}</Badge>
                  <Badge
                    variant="outline"
                    className={`text-[10px] ${
                      item.days < 7
                        ? "bg-green-50 text-green-700 border-green-200"
                        : item.days < 14
                        ? "bg-amber-50 text-amber-700 border-amber-200"
                        : "bg-red-50 text-red-700 border-red-200"
                    }`}
                  >
                    {Math.round(item.days)}d
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
