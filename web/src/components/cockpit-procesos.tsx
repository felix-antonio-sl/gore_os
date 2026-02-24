"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { GitBranch, FileCode, CalendarDays } from "lucide-react";
import { KanbanCard } from "@/components/kanban-card";
import { cn } from "@/lib/utils";
import type { CockpitProcesos, DGIBPMNModel } from "@/types";

interface Props {
  data: CockpitProcesos;
}

type DmaicGroup = "Define-Measure" | "Analyze-Improve" | "Verify";

const dmaicGroupMap: Record<string, DmaicGroup> = {
  DEFINE: "Define-Measure",
  MEASURE: "Define-Measure",
  ANALYZE: "Analyze-Improve",
  IMPROVE: "Analyze-Improve",
  CONTROL: "Verify",
};

const bpmnStatusBadge: Record<
  DGIBPMNModel["status"],
  { label: string; className: string }
> = {
  BORRADOR: { label: "Borrador", className: "border-gray-400 text-gray-600" },
  REVISION: { label: "Revisión", className: "bg-amber-100 text-amber-700 border-amber-300" },
  VALIDADO: { label: "Validado", className: "bg-green-100 text-green-700 border-green-300" },
};

const KANBAN_GROUPS: { key: DmaicGroup; label: string }[] = [
  { key: "Define-Measure", label: "Define · Measure" },
  { key: "Analyze-Improve", label: "Analyze · Improve" },
  { key: "Verify", label: "Verify (Control)" },
];

export function CockpitProcesosView({ data }: Props) {
  const { initiatives, bpmn_models, today_agenda, portfolio_stats } = data;

  const byGroup = (group: DmaicGroup) =>
    initiatives.filter((i) => dmaicGroupMap[i.dmaic_phase ?? ""] === group);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Cockpit Especialista en Procesos</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Portafolio DMAIC, modelos BPMN y agenda del día
        </p>
      </div>

      {/* Portfolio stats */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="rounded-lg border bg-blue-50 border-blue-200 px-4 py-2">
          <p className="text-xs text-muted-foreground">Activas</p>
          <p className="text-xl font-bold text-blue-700">{portfolio_stats.active}</p>
        </div>
        <div className="rounded-lg border bg-green-50 border-green-200 px-4 py-2">
          <p className="text-xs text-muted-foreground">Completadas</p>
          <p className="text-xl font-bold text-green-700">{portfolio_stats.completed}</p>
        </div>
        <div className="rounded-lg border bg-gray-50 border-gray-200 px-4 py-2">
          <p className="text-xs text-muted-foreground">Meta anual</p>
          <p className="text-xl font-bold text-gray-700">{portfolio_stats.target}</p>
        </div>
      </div>

      {/* Kanban DMAIC */}
      <section>
        <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
          <GitBranch className="size-4 text-purple-600" />
          Portafolio DMAIC
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {KANBAN_GROUPS.map((group) => {
            const items = byGroup(group.key);
            return (
              <div key={group.key} className="flex flex-col gap-3">
                <div className="flex items-center gap-2 px-1">
                  <h3 className="text-sm font-semibold">{group.label}</h3>
                  <Badge variant="outline" className="border-gray-300 text-gray-600">
                    {items.length}
                  </Badge>
                </div>
                <div className="min-h-[100px] rounded-xl bg-gray-50 border border-gray-200 p-2 space-y-2">
                  {items.length === 0 ? (
                    <p className="text-xs text-muted-foreground text-center py-6 italic">
                      Sin iniciativas
                    </p>
                  ) : (
                    items.map((ini) => (
                      <KanbanCard key={ini.id} initiative={ini} />
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Row: Agenda + BPMN */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Agenda Hoy */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <CalendarDays className="size-4 text-blue-600" />
              Agenda de Hoy
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {today_agenda.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">Sin actividades programadas.</p>
            ) : (
              <div className="space-y-2">
                {today_agenda.map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className="text-xs font-mono text-muted-foreground w-12 shrink-0 mt-0.5">
                      {item.time}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{item.activity}</p>
                      <p className="text-xs text-muted-foreground truncate">{item.process}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Modelos BPMN Recientes */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <FileCode className="size-4 text-gray-600" />
              Modelos BPMN Recientes
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {bpmn_models.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">Sin modelos recientes.</p>
            ) : (
              <div className="space-y-2">
                {bpmn_models.map((model) => {
                  const statusConfig =
                    bpmnStatusBadge[model.status as DGIBPMNModel["status"]] ?? {
                      label: model.status,
                      className: "border-gray-300 text-gray-600",
                    };
                  return (
                    <div key={model.id} className="flex items-center justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{model.process_name}</p>
                        <p className="text-xs text-muted-foreground">
                          v{model.version}
                          {model.code && ` · ${model.code}`}
                        </p>
                      </div>
                      <Badge
                        variant="outline"
                        className={cn("text-[10px] px-1.5 py-0 border shrink-0", statusConfig.className)}
                      >
                        {statusConfig.label}
                      </Badge>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
