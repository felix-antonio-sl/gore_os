"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { KpiCard } from "@/components/kpi-card";
import { DataTable } from "@/components/data-table";
import { AlertCard } from "@/components/alert-card";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { ExecutionBarChart } from "@/components/charts/execution-bar-chart";
import { CommitmentDonut } from "@/components/charts/commitment-donut";
import { AlertsBySeverity } from "@/components/charts/alerts-by-severity";
import { CockpitJefeDGIView } from "@/components/cockpit-jefe-dgi";
import { CockpitControlGestionView } from "@/components/cockpit-control-gestion";
import { CockpitProcesosView } from "@/components/cockpit-procesos";
import { CockpitTDView } from "@/components/cockpit-td";
import { SemaforoCard } from "@/components/semaforo-card";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/empty-state";
import type {
  DashboardData,
  CompromisoListItem,
  AlertaListItem,
  CockpitJefeDGI,
  CockpitControlGestion,
  CockpitProcesos,
  CockpitTD,
} from "@/types";

interface DivisionBreakdown {
  division_name: string;
  vencidos: number;
  total_compromisos: number;
  problemas_abiertos: number;
  ejecucion_pct: number;
}

interface SemaforoItem {
  dimension: string;
  label: string;
  signal: "VERDE" | "AMARILLO" | "ROJO";
  indicator_count: number;
}

interface ExecutiveDashboardData extends DashboardData {
  divisions: DivisionBreakdown[];
  semaforo?: SemaforoItem[];
}

interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

interface BudgetChartPoint {
  division: string;
  ejecucion_pct: number;
  pagado: number;
  vigente: number;
}

interface ChartDataResponse {
  commitments_by_state: ChartDataPoint[];
  alerts_by_severity: ChartDataPoint[];
  budget_by_division: BudgetChartPoint[];
}

// Union type for all DGI cockpit responses
type DGICockpitData =
  | { role: "JEFE_DGI"; data: CockpitJefeDGI }
  | { role: "ESP_CONTROL_GESTION"; data: CockpitControlGestion }
  | { role: "ESP_PROCESOS"; data: CockpitProcesos }
  | { role: "ESP_TD"; data: CockpitTD };

// Drill-down map: KPI label → destination route
const DRILLDOWNS: Record<string, string> = {
  // ADMIN_REGIONAL / Executive
  "IPRs críticas": "/alertas?severity=CRITICO",
  "Compromisos vencidos": "/compromisos?overdue=true",
  "Ejec. Presupuestaria": "/presupuesto",
  "Convenios por vencer": "/convenios?state=VIGENTE",
  // JEFE_DIVISION
  "Vencidos mi div": "/compromisos?overdue=true",
  "Por Verificar": "/compromisos?estado=COMPLETADO",
  "Problemas abiertos": "/problemas?estado=ABIERTO",
  // ENCARGADO
  "Pendientes": "/compromisos?estado=PENDIENTE",
  "En Progreso": "/compromisos?estado=EN_PROGRESO",
  "Completados": "/compromisos?estado=COMPLETADO",
  "Mis Alertas": "/alertas",
  // mi-division
  "Vencidos": "/compromisos?overdue=true",
  "Activos": "/compromisos",
};

// ─── Operational Dashboard ──────────────────────────────────────────────────

function OperationalDashboard() {
  const [data, setData] = useState<ExecutiveDashboardData | null>(null);
  const [chartData, setChartData] = useState<ChartDataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { user: authUser } = useAuth();

  const isExecutive = authUser && ["ADMIN_REGIONAL", "ADMIN_SISTEMA", "GOBERNADOR", "SECRETARIO_EJECUTIVO"].includes(authUser.role_code);

  useEffect(() => {
    const endpoint = isExecutive ? "/api/dashboard/ejecutivo" : "/api/dashboard";
    Promise.all([
      api.get<ExecutiveDashboardData>(endpoint),
      api.get<ChartDataResponse>("/api/dashboard/chart-data"),
    ])
      .then(([dashData, charts]) => {
        setData(dashData);
        setChartData(charts);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [isExecutive]);

  const handleAttend = async (id: string) => {
    try {
      await api.post(`/api/alertas/${id}/atender`, {});
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          alerts: prev.alerts.filter((a) => a.id !== id),
        };
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al atender alerta");
    }
  };

  const handleViewSubject = (type: string, subjectId: string) => {
    if (type === "core.ipr" || type === "ipr") {
      router.push(`/ipr/${subjectId}`);
    }
  };

  const commitmentColumns = [
    { key: "description", label: "Descripción" },
    {
      key: "ipr_codigo_bip",
      label: "BIP",
      render: (value: unknown) => (
        <span className="text-xs text-muted-foreground">{String(value ?? "-")}</span>
      ),
    },
    { key: "responsible_name", label: "Responsable" },
    {
      key: "due_date",
      label: "Vence",
      render: (_: unknown, row: unknown) => {
        const r = row as CompromisoListItem;
        return <TemporalIndicator daysRemaining={r.days_remaining} state={r.state} />;
      },
    },
    {
      key: "state",
      label: "Estado",
      render: (value: unknown) => <StatusBadge status={String(value ?? "")} size="sm" />,
    },
  ];

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive">
          Error al cargar el dashboard: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Panel de Control</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Resumen operativo del Gobierno Regional de Ñuble
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
            <KpiCard
              key={i}
              label={kpi.label}
              value={kpi.value}
              sublabel={kpi.sublabel}
              color={kpi.color}
              onClick={DRILLDOWNS[kpi.label] ? () => router.push(DRILLDOWNS[kpi.label]) : undefined}
            />
          ))}
        </div>
      )}

      {/* Semáforo DGI (solo ejecutivos) */}
      {!isLoading && isExecutive && data?.semaforo && data.semaforo.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Semáforo Institucional</h2>
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
            {data.semaforo.map((s) => (
              <SemaforoCard
                key={s.dimension}
                dimension={s.dimension}
                label={s.label}
                signal={s.signal}
                indicatorCount={s.indicator_count}
              />
            ))}
          </div>
        </div>
      )}

      {/* Charts */}
      {!isLoading && chartData && (
        <div className={`grid gap-4 ${isExecutive ? "grid-cols-1 lg:grid-cols-3" : "grid-cols-1 lg:grid-cols-2"}`}>
          {isExecutive && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Ejecución Presupuestaria</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <ExecutionBarChart data={chartData.budget_by_division} />
              </CardContent>
            </Card>
          )}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Compromisos por Estado</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <CommitmentDonut data={chartData.commitments_by_state} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Alertas por Severidad</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <AlertsBySeverity data={chartData.alerts_by_severity} />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Compromisos */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Compromisos Recientes</h2>
        <DataTable
          columns={commitmentColumns}
          data={data?.commitments ?? []}
          page={1}
          totalPages={1}
          total={data?.commitments.length ?? 0}
          onPageChange={() => {}}
          isLoading={isLoading}
        />
      </div>

      {/* Division breakdown for executives */}
      {isExecutive && data?.divisions && data.divisions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Desglose por División</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.divisions.map((div) => (
                <div
                  key={div.division_name}
                  className="flex items-center justify-between py-2 border-b last:border-0"
                >
                  <span className="font-medium text-sm">{div.division_name}</span>
                  <div className="flex gap-2 items-center">
                    {div.vencidos > 0 && (
                      <Badge variant="destructive" className="text-xs">
                        {div.vencidos} vencidos
                      </Badge>
                    )}
                    <Badge variant="outline" className="text-xs">
                      {div.total_compromisos} compromisos
                    </Badge>
                    {div.problemas_abiertos > 0 && (
                      <Badge variant="outline" className="text-xs border-orange-400 text-orange-600">
                        {div.problemas_abiertos} problemas
                      </Badge>
                    )}
                    <Badge
                      variant="secondary"
                      className={`text-xs ${
                        div.ejecucion_pct >= 70
                          ? "bg-green-100 text-green-800"
                          : div.ejecucion_pct >= 40
                          ? "bg-amber-100 text-amber-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {div.ejecucion_pct}% ejec.
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Alertas */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Alertas Activas</h2>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
            ))}
          </div>
        ) : data?.alerts.length === 0 ? (
          <EmptyState compact title="No hay alertas activas." />
        ) : (
          <div className="space-y-3">
            {data?.alerts.map((alert: AlertaListItem) => (
              <AlertCard
                key={alert.id}
                alert={alert}
                onAttend={handleAttend}
                onViewSubject={handleViewSubject}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── DGI Cockpit Loader ─────────────────────────────────────────────────────

function DGICockpit() {
  const { user } = useAuth();
  const [cockpit, setCockpit] = useState<DGICockpitData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<unknown>("/api/dgi/cockpit")
      .then((raw) => {
        if (!user) return;
        const role = user.role_code;
        if (role === "JEFE_DGI") {
          setCockpit({ role: "JEFE_DGI", data: raw as CockpitJefeDGI });
        } else if (role === "ESP_CONTROL_GESTION") {
          setCockpit({ role: "ESP_CONTROL_GESTION", data: raw as CockpitControlGestion });
        } else if (role === "ESP_PROCESOS") {
          setCockpit({ role: "ESP_PROCESOS", data: raw as CockpitProcesos });
        } else if (role === "ESP_TD") {
          setCockpit({ role: "ESP_TD", data: raw as CockpitTD });
        }
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [user]);

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        {/* Skeleton header */}
        <div className="space-y-2">
          <div className="h-8 w-64 rounded bg-muted animate-pulse" />
          <div className="h-4 w-48 rounded bg-muted animate-pulse" />
        </div>
        {/* Skeleton semaforo row */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-24 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
        {/* Skeleton cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-48 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive">
          Error al cargar el cockpit DGI: {error}
        </div>
      </div>
    );
  }

  if (!cockpit) {
    return (
      <div className="p-6">
        <div className="rounded-md bg-muted px-4 py-3 text-sm text-muted-foreground">
          No hay datos de cockpit disponibles para tu rol.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {cockpit.role === "JEFE_DGI" && <CockpitJefeDGIView data={cockpit.data} />}
      {cockpit.role === "ESP_CONTROL_GESTION" && (
        <CockpitControlGestionView data={cockpit.data} />
      )}
      {cockpit.role === "ESP_PROCESOS" && <CockpitProcesosView data={cockpit.data} />}
      {cockpit.role === "ESP_TD" && <CockpitTDView data={cockpit.data} />}
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-48 rounded bg-muted animate-pulse" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (user?.population === "dgi") {
    return <DGICockpit />;
  }

  return <OperationalDashboard />;
}

