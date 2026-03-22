"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { AlertTriangle, Users, FileText, CheckSquare, Receipt, ShieldAlert, Timer } from "lucide-react";
import { useRouter } from "next/navigation";
import { SemaforoCard } from "@/components/semaforo-card";
import { cn } from "@/lib/utils";
import { formatCLP } from "@/lib/format";
import { api } from "@/lib/api";
import type { CockpitJefeDGI, EscalationStats, SLADashboardSummary } from "@/types";

interface CockpitJefeDGIProps {
  data: CockpitJefeDGI;
}

const severityBg: Record<string, string> = {
  CRITICO: "bg-red-50 border-red-200",
  ALTO: "bg-orange-50 border-orange-200",
  ATENCION: "bg-amber-50 border-amber-200",
};

const reportStatusBadge: Record<string, { label: string; className: string }> = {
  BORRADOR: { label: "Borrador", className: "border-gray-400 text-gray-600" },
  EN_REVISION: { label: "En Revisión", className: "bg-amber-500 text-white border-transparent" },
  LISTO: { label: "Listo", className: "bg-green-500 text-white border-transparent" },
  ENVIADO: { label: "Enviado", className: "bg-blue-600 text-white border-transparent" },
};

export function CockpitJefeDGIView({ data }: CockpitJefeDGIProps) {
  const router = useRouter();
  const { semaforo, decisions_pending, decision_items, team_status, critical_alerts, report_status, rendition_summary } = data;

  const [escalationStats, setEscalationStats] = useState<EscalationStats | null>(null);
  const [slaSummary, setSlaSummary] = useState<SLADashboardSummary | null>(null);

  useEffect(() => {
    api.get<EscalationStats>("/api/dgi/escalations/stats").then(setEscalationStats).catch(() => {});
    api.get<SLADashboardSummary>("/api/dgi/services/sla-dashboard").then(setSlaSummary).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold">Cockpit Jefe DGI</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Vista integrada del estado institucional
        </p>
      </div>

      {/* Semáforo institucional */}
      <section>
        <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-blue-600" />
          Semáforo Institucional
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {semaforo.map((dim) => (
            <SemaforoCard
              key={dim.dimension}
              dimension={dim.dimension}
              label={dim.label}
              signal={dim.signal}
              indicatorCount={dim.indicator_count}
              onClick={() => {
                switch (dim.dimension) {
                  case "CARTERA_IPR":
                    router.push(dim.signal === "VERDE" ? "/cartera" : `/cartera?health_signal=${dim.signal}`);
                    break;
                  case "PRESUPUESTO":
                    router.push("/presupuesto");
                    break;
                  case "CONVENIOS":
                    router.push("/convenios");
                    break;
                  case "TDE":
                    router.push("/datos");
                    break;
                  case "RIESGOS":
                    router.push("/alertas");
                    break;
                }
              }}
            />
          ))}
        </div>
      </section>

      {/* Row: Decisiones + Equipo */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Requieren Mi Decisión */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <CheckSquare className="size-4 text-orange-600" />
              Requieren Mi Decisión
              {decisions_pending > 0 && (
                <Badge className="bg-orange-600 text-white ml-auto">
                  {decisions_pending}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {decisions_pending === 0 ? (
              <p className="text-sm text-muted-foreground italic">Sin pendientes. Todo al día.</p>
            ) : (
              <div className="space-y-1.5">
                {(decision_items ?? []).slice(0, 5).map((item) => (
                  <div
                    key={`${item.source}-${item.id}`}
                    className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm hover:bg-muted/50 cursor-pointer"
                    role="button"
                    tabIndex={0}
                    onClick={() => {
                      if (item.source === "alert") router.push("/alertas");
                      else if (item.source === "rendition") router.push("/datos?dominio=rendiciones");
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        if (item.source === "alert") router.push("/alertas");
                        else if (item.source === "rendition") router.push("/datos?dominio=rendiciones");
                      }
                    }}
                  >
                    <span className={cn(
                      "inline-block h-2 w-2 rounded-full shrink-0",
                      item.severity === "CRITICO" || item.severity === "VENCIDA" ? "bg-red-500" : "bg-orange-500"
                    )} />
                    <span className="truncate flex-1">{item.title}</span>
                    <Badge variant="outline" className="text-[10px] px-1.5 py-0 shrink-0">
                      {item.source === "alert" ? "Alerta" : "Rendición"}
                    </Badge>
                  </div>
                ))}
                {decisions_pending > (decision_items ?? []).length && (
                  <p className="text-xs text-muted-foreground pl-1">
                    +{decisions_pending - (decision_items ?? []).length} más
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Equipo DGI Hoy */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Users className="size-4 text-blue-600" />
              Equipo DGI Hoy
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {team_status.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">Sin datos del equipo.</p>
            ) : (
              <div className="space-y-2">
                {team_status.map((member, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{member.name}</p>
                      <p className="text-xs text-muted-foreground truncate">{member.activity}</p>
                    </div>
                    <Badge variant="outline" className="text-[10px] px-1.5 py-0 shrink-0">
                      {member.role}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Escalamientos + SLA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Escalamientos Activos */}
        <Card className="cursor-pointer hover:border-orange-300 transition-colors" onClick={() => router.push("/escalamiento")}>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <ShieldAlert className="size-4 text-orange-600" />
              Escalamientos Activos
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {escalationStats ? (
              <div className="flex items-baseline gap-4">
                <span className="text-3xl font-bold tabular-nums">{escalationStats.total_active}</span>
                <div className="flex gap-2">
                  {(escalationStats.by_level ?? []).map((item) => (
                    item.count > 0 && (
                      <Badge key={item.level} variant="outline" className={cn(
                        "text-[10px] px-1.5 py-0",
                        item.level === "NIVEL_4" ? "border-red-400 text-red-600" :
                        item.level === "NIVEL_3" ? "border-orange-400 text-orange-600" :
                        item.level === "NIVEL_2" ? "border-amber-400 text-amber-600" :
                        "border-blue-400 text-blue-600"
                      )}>
                        {item.level.replace("NIVEL_", "N")}: {item.count}
                      </Badge>
                    )
                  ))}
                </div>
              </div>
            ) : (
              <div className="h-8 w-16 bg-muted animate-pulse rounded" />
            )}
          </CardContent>
        </Card>

        {/* SLA Cumplimiento */}
        <Card className="cursor-pointer hover:border-blue-300 transition-colors" onClick={() => router.push("/servicios")}>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Timer className="size-4 text-blue-600" />
              SLA Cumplimiento
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {slaSummary ? (
              <div className="flex items-baseline gap-4">
                <span className={cn(
                  "text-3xl font-bold tabular-nums",
                  slaSummary.global_completion_rate >= 90 ? "text-green-600" :
                  slaSummary.global_completion_rate >= 70 ? "text-amber-600" : "text-red-600"
                )}>
                  {slaSummary.global_completion_rate}%
                </span>
                <div className="flex gap-3 text-xs text-muted-foreground">
                  <span>{slaSummary.active_requests} activas</span>
                  {slaSummary.avg_satisfaction != null && (
                    <span>{slaSummary.avg_satisfaction}/5 satisfacción</span>
                  )}
                </div>
              </div>
            ) : (
              <div className="h-8 w-16 bg-muted animate-pulse rounded" />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Alertas Críticas */}
      {critical_alerts.length > 0 && (
        <section>
          <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="size-4 text-red-600" />
            Alertas Críticas
          </h2>
          <div className="space-y-2">
            {critical_alerts.map((alert) => (
              <div
                key={alert.id}
                className={cn(
                  "flex items-start justify-between gap-3 rounded-lg border px-4 py-3",
                  severityBg[alert.severity] ?? "bg-red-50 border-red-200"
                )}
              >
                <div className="flex items-start gap-2 flex-1 min-w-0">
                  <AlertTriangle className="size-4 text-red-600 mt-0.5 shrink-0" />
                  <p className="text-sm text-red-800">{alert.message}</p>
                </div>
                <div className="flex gap-2 shrink-0">
                  <Button size="sm" variant="outline" className="h-7 text-xs border-red-300 text-red-700 hover:bg-red-100"
                    onClick={() => router.push("/alertas")}>
                    Escalar
                  </Button>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button size="sm" variant="ghost" className="h-7 text-xs text-red-600">
                          Playbook
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Procedimiento de escalamiento según protocolo institucional</TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Informe Semanal */}
      {report_status && (
        <section>
          <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
            <FileText className="size-4 text-gray-600" />
            Informe Semanal
          </h2>
          <Card>
            <CardContent className="px-6 py-4">
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{report_status.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Vence: {report_status.due}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <Badge
                    variant="outline"
                    className={
                      reportStatusBadge[report_status.status]?.className ??
                      "border-gray-400 text-gray-600"
                    }
                  >
                    {reportStatusBadge[report_status.status]?.label ?? report_status.status}
                  </Badge>
                  <Button size="sm" variant="outline" className="h-7 text-xs">
                    Generar borrador
                  </Button>
                </div>
              </div>
              {/* Status progress bar */}
              <div className="mt-3">
                <Separator className="mb-3" />
                <div className="flex items-center gap-2">
                  {["BORRADOR", "EN_REVISION", "LISTO", "ENVIADO"].map((step, i) => {
                    const statusOrder = ["BORRADOR", "EN_REVISION", "LISTO", "ENVIADO"];
                    const currentIdx = statusOrder.indexOf(report_status.status);
                    const isActive = i <= currentIdx;
                    return (
                      <div key={step} className="flex items-center gap-2 flex-1">
                        <div
                          className={cn(
                            "h-1.5 flex-1 rounded-full transition-colors",
                            isActive ? "bg-blue-500" : "bg-gray-200"
                          )}
                        />
                        {i === 3 && (
                          <span
                            className={cn(
                              "text-xs font-medium",
                              isActive ? "text-blue-600" : "text-gray-400"
                            )}
                          >
                            Enviado
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      )}

      {/* Rendiciones — Art. 18 CGR */}
      {rendition_summary && rendition_summary.total > 0 && (
        <section>
          <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
            <Receipt className="size-4 text-purple-600" />
            Rendiciones
            <Badge variant="outline" className="text-xs">
              {rendition_summary.total} total
            </Badge>
            {rendition_summary.by_state.some((s) => s.code === "PENDIENTE" && s.count > 0) && (
              <Badge className="bg-red-600 text-white text-xs">
                {rendition_summary.by_state.find((s) => s.code === "PENDIENTE")?.count ?? 0} pendientes
              </Badge>
            )}
            <Button size="sm" variant="outline" className="ml-auto h-7 text-xs" onClick={() => router.push("/datos?dominio=rendiciones")}>
              Ver rendiciones
            </Button>
          </h2>
          <Card>
            <CardContent className="px-6 py-4">
              <div className="flex flex-wrap gap-2 mb-3">
                {rendition_summary.by_state.map((s) => {
                  const colorMap: Record<string, string> = {
                    PENDIENTE: "bg-gray-100 text-gray-700 border-gray-300",
                    EN_REVISION: "bg-amber-50 text-amber-700 border-amber-300",
                    OBSERVADA: "bg-orange-50 text-orange-700 border-orange-300",
                    APROBADA: "bg-green-50 text-green-700 border-green-300",
                    RECHAZADA: "bg-red-50 text-red-700 border-red-300",
                  };
                  return (
                    <Badge
                      key={s.code}
                      variant="outline"
                      className={cn("text-xs", colorMap[s.code] ?? "border-gray-300")}
                    >
                      {s.label}: {s.count}
                    </Badge>
                  );
                })}
              </div>
              {rendition_summary.amount_at_risk != null && (
                <div className="flex items-center gap-2 text-sm">
                  <AlertTriangle className="size-3.5 text-amber-600 shrink-0" />
                  <span className="text-muted-foreground">Monto en riesgo:</span>
                  <span className="font-mono font-semibold tabular-nums text-amber-700">
                    {formatCLP(rendition_summary.amount_at_risk)}
                  </span>
                </div>
              )}
              {rendition_summary.by_state.some((s) => s.code === "PENDIENTE" && s.count > 0) && (
                <p className="mt-2 text-xs text-red-600 font-medium">
                  Art. 18 Res. 30 CGR: Transferencias bloqueadas hasta aprobar rendiciones pendientes
                </p>
              )}
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  );
}
