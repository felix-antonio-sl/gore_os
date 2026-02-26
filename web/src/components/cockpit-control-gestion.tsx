"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { BarChart2, AlertCircle, TrendingUp, ClipboardList } from "lucide-react";
import { ProgressBarIndicator } from "@/components/progress-bar-indicator";
import { SparklineIndicator } from "@/components/sparkline-indicator";
import { cn } from "@/lib/utils";
import type { CockpitControlGestion, DGIDataSource } from "@/types";

interface Props {
  data: CockpitControlGestion;
}

const sourceStatusConfig: Record<
  DGIDataSource["status"],
  { label: string; badgeClass: string; extraLabel?: (days: number) => string }
> = {
  OK: {
    label: "OK",
    badgeClass: "bg-green-100 text-green-700 border-green-300",
  },
  ATRASADO: {
    label: "Atrasado",
    badgeClass: "bg-amber-100 text-amber-700 border-amber-300",
    extraLabel: (days) => `${days}d`,
  },
  SIN_DATOS: {
    label: "Sin datos",
    badgeClass: "bg-gray-100 text-gray-600 border-gray-300",
    extraLabel: () => "?",
  },
};

const priorityBadge: Record<string, string> = {
  ALTA: "bg-red-100 text-red-700 border-red-300",
  MEDIA: "bg-amber-100 text-amber-700 border-amber-300",
  BAJA: "bg-gray-100 text-gray-600 border-gray-300",
};

export function CockpitControlGestionView({ data }: Props) {
  const { data_sources, indicators_alert, trends, work_queue } = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Cockpit Control de Gestión</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Estado de datos, indicadores y cola de trabajo
        </p>
      </div>

      {/* Estado de Datos Hoy */}
      <section>
        <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
          <BarChart2 className="size-4 text-blue-600" />
          Estado de Datos Hoy
        </h2>
        <div className="flex flex-wrap gap-2">
          {data_sources.length === 0 ? (
            <p className="text-sm text-muted-foreground italic">Sin fuentes de datos configuradas.</p>
          ) : (
            data_sources.map((source) => {
              const config = sourceStatusConfig[source.status];
              return (
                <div
                  key={source.id}
                  className={cn(
                    "flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium",
                    config.badgeClass
                  )}
                >
                  <span>{source.division_name ?? source.source_name}</span>
                  {config.extraLabel && (
                    <span className="opacity-70">
                      {config.extraLabel(source.days_behind)}
                    </span>
                  )}
                </div>
              );
            })
          )}
        </div>
      </section>

      {/* Row: Indicadores + Tendencias */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Indicadores en Alerta */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <AlertCircle className="size-4 text-red-600" />
              Indicadores en Alerta
              {indicators_alert.length > 0 && (
                <Badge className="bg-red-600 text-white ml-auto">
                  {indicators_alert.length}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {indicators_alert.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">Sin indicadores en alerta.</p>
            ) : (
              <div className="space-y-2">
                {indicators_alert.map((ind) => {
                  const signalBadge: Record<string, string> = {
                    ROJO: "bg-red-100 text-red-700 border-red-300",
                    AMARILLO: "bg-amber-100 text-amber-700 border-amber-300",
                    VERDE: "bg-green-100 text-green-700 border-green-300",
                  };
                  return (
                    <div
                      key={ind.id}
                      className="flex items-center justify-between gap-3 rounded-md border px-3 py-2"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium truncate">{ind.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {ind.current_value ?? "–"}{ind.unit} / meta: {ind.target_value ?? "–"}{ind.unit}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <SparklineIndicator indicatorId={ind.id} days={90} />
                        {ind.signal && (
                          <Badge
                            variant="outline"
                            className={cn("text-[10px] px-1.5 py-0 border", signalBadge[ind.signal])}
                          >
                            {ind.signal}
                          </Badge>
                        )}
                        <Button size="sm" variant="outline" className="h-7 text-xs">
                          Investigar
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tendencias 30 días */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <TrendingUp className="size-4 text-green-600" />
              Tendencias 30 días
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {trends.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">Sin tendencias disponibles.</p>
            ) : (
              <div className="space-y-4">
                {trends.map((ind) => (
                  <ProgressBarIndicator
                    key={ind.id}
                    label={ind.name}
                    value={ind.current_value ?? 0}
                    target={ind.target_value ?? 100}
                    unit={ind.unit}
                    trend={ind.trend ?? undefined}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Mi Cola de Trabajo Hoy */}
      <section>
        <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
          <ClipboardList className="size-4 text-gray-600" />
          Mi Cola de Trabajo Hoy
        </h2>
        {work_queue.length === 0 ? (
          <p className="text-sm text-muted-foreground italic">Cola vacía. Buen trabajo.</p>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-24">Prioridad</TableHead>
                  <TableHead>Tarea</TableHead>
                  <TableHead className="w-28">Estado</TableHead>
                  <TableHead className="w-28">Plazo</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {work_queue.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-[10px] px-1.5 py-0 border",
                          priorityBadge[item.priority] ?? "border-gray-300 text-gray-600"
                        )}
                      >
                        {item.priority}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm">{item.task}</TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                        {item.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {item.deadline}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </section>
    </div>
  );
}
