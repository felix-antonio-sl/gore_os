"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { AlertTriangle, Users, FileText, CheckSquare } from "lucide-react";
import { SemaforoCard } from "@/components/semaforo-card";
import { SemaforoGauge } from "@/components/charts/semaforo-gauge";
import { cn } from "@/lib/utils";
import type { CockpitJefeDGI } from "@/types";

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
  const { semaforo, decisions_pending, team_status, critical_alerts, report_status } = data;

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
            />
          ))}
        </div>
        {/* Gauge visual row */}
        <div className="mt-4 flex items-center justify-center gap-6 flex-wrap">
          {semaforo.map((dim) => (
            <SemaforoGauge
              key={dim.dimension}
              signal={dim.signal}
              label={dim.label}
              dimension={dim.dimension}
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
              <div className="space-y-2">
                {Array.from({ length: Math.min(decisions_pending, 4) }).map((_, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between gap-3 rounded-md border px-3 py-2 bg-orange-50"
                  >
                    <span className="text-sm text-muted-foreground">
                      Decisión pendiente #{i + 1}
                    </span>
                    <Button size="sm" variant="outline" className="h-7 text-xs shrink-0">
                      Decidir
                    </Button>
                  </div>
                ))}
                {decisions_pending > 4 && (
                  <p className="text-xs text-muted-foreground text-center pt-1">
                    +{decisions_pending - 4} más pendientes
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
                  <Button size="sm" variant="outline" className="h-7 text-xs border-red-300 text-red-700 hover:bg-red-100">
                    Escalar
                  </Button>
                  <Button size="sm" variant="ghost" className="h-7 text-xs text-red-600">
                    Playbook
                  </Button>
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
    </div>
  );
}
