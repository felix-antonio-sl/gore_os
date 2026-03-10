"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ShieldCheck, BookOpen, CalendarDays, AlertTriangle } from "lucide-react";
import { ProgressBarIndicator } from "@/components/progress-bar-indicator";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";
import type { CockpitTD } from "@/types";

interface Props {
  data: CockpitTD;
}

const decreeBadge: Record<string, { label: string; fullLabel: string; className: string }> = {
  VIGENTE: { label: "VIG", fullLabel: "Vigente", className: "bg-green-100 text-green-700 border-green-300" },
  PARCIAL: { label: "PAR", fullLabel: "Parcial", className: "bg-amber-100 text-amber-700 border-amber-300" },
  PENDIENTE: { label: "PEN", fullLabel: "Pendiente", className: "bg-red-100 text-red-700 border-red-300" },
};

export function CockpitTDView({ data }: Props) {
  const router = useRouter();
  const { compliance_bars, velocity, decrees, kb_stats, committee, normative_alerts } = data;

  return (
    <TooltipProvider>
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Cockpit Transformación Digital</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Cumplimiento Ley 21.180, normativas y base de conocimiento
        </p>
      </div>

      {/* Cumplimiento Ley 21.180 */}
      <section>
        <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
          <ShieldCheck className="size-4 text-blue-600" />
          Cumplimiento Ley 21.180
        </h2>
        <Card>
          <CardContent className="px-6 py-5">
            <div className="space-y-5">
              {compliance_bars.length === 0 ? (
                <p className="text-sm text-muted-foreground italic">Sin datos de cumplimiento.</p>
              ) : (
                compliance_bars.map((ind) => (
                  <ProgressBarIndicator
                    key={ind.id}
                    label={ind.name}
                    value={ind.current_value ?? 0}
                    target={ind.target_value ?? 100}
                    unit={ind.unit || "%"}
                    trend={ind.trend ?? undefined}
                  />
                ))
              )}
            </div>

            {/* Velocidad de avance */}
            <Separator className="my-4" />
            <p className="text-xs font-semibold text-muted-foreground mb-2">Velocidad de avance</p>
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-lg border bg-blue-50 border-blue-200 px-3 py-2.5 text-center">
                <p className="text-lg font-bold font-mono text-blue-700">+{velocity.current}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">pp/mes actual</p>
              </div>
              <div className="rounded-lg border bg-blue-50 border-blue-200 px-3 py-2.5 text-center">
                <p className="text-lg font-bold font-mono text-blue-700">+{velocity.required}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">pp/mes requerida</p>
              </div>
              <div className={cn(
                "rounded-lg border px-3 py-2.5 text-center",
                velocity.months_remaining <= 3 ? "bg-red-50 border-red-200" :
                velocity.months_remaining <= 6 ? "bg-amber-50 border-amber-200" :
                "bg-blue-50 border-blue-200"
              )}>
                <p className={cn(
                  "text-lg font-bold font-mono",
                  velocity.months_remaining <= 3 ? "text-red-700" :
                  velocity.months_remaining <= 6 ? "text-amber-700" :
                  "text-blue-700"
                )}>
                  {velocity.months_remaining}
                </p>
                <p className="text-[10px] text-muted-foreground mt-0.5">meses restantes</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Row: Decretos + KB Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Decretos DS7-DS12 */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold">Decretos DS7-DS12</CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            {decrees.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">Sin decretos configurados.</p>
            ) : (
              <div className="space-y-2">
                {decrees.map((decree, i) => {
                  const badgeConfig =
                    decreeBadge[decree.status] ?? {
                      label: decree.status,
                      className: "border-gray-300 text-gray-600",
                    };
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-[10px] px-1.5 py-0 w-10 justify-center shrink-0 border font-bold",
                              badgeConfig.className
                            )}
                          >
                            {badgeConfig.label}
                          </Badge>
                        </TooltipTrigger>
                        <TooltipContent>{badgeConfig.fullLabel}</TooltipContent>
                      </Tooltip>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-mono text-muted-foreground">{decree.code}</p>
                        <p className="text-sm truncate">{decree.name}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Base de Conocimiento */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <BookOpen className="size-4 text-green-600" />
              Base de Conocimiento
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-3 px-6">
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="rounded-lg border bg-amber-50 border-amber-200 py-3 cursor-pointer hover:shadow-md transition-shadow"
                role="button" tabIndex={0}
                onClick={() => router.push("/datos")}
                onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); router.push("/datos"); } }}>
                <p className="text-2xl font-bold text-amber-700">
                  {kb_stats.pending_publication}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Pendientes</p>
              </div>
              <div className="rounded-lg border bg-blue-50 border-blue-200 py-3 cursor-pointer hover:shadow-md transition-shadow"
                role="button" tabIndex={0}
                onClick={() => router.push("/datos")}
                onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); router.push("/datos"); } }}>
                <p className="text-2xl font-bold text-blue-700">
                  {kb_stats.recently_updated}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Actualizados</p>
              </div>
              <div className="rounded-lg border bg-gray-50 border-gray-200 py-3 cursor-pointer hover:shadow-md transition-shadow"
                role="button" tabIndex={0}
                onClick={() => router.push("/datos")}
                onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); router.push("/datos"); } }}>
                <p className="text-2xl font-bold text-gray-700">
                  {kb_stats.total}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Total</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Comité TD */}
      {committee && (
        <section>
          <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
            <CalendarDays className="size-4 text-blue-600" />
            Próximo Comité TD
          </h2>
          <Card>
            <CardContent className="px-6 py-4">
              <div className="flex items-center justify-between gap-4 mb-3">
                <p className="text-sm font-semibold">
                  Sesión: {formatDate(committee.session_date)}
                </p>
                <Badge variant="outline" className="border-gray-300 text-gray-600">
                  {committee.status}
                </Badge>
              </div>
              {committee.agenda.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1.5 uppercase tracking-wide">
                    Agenda
                  </p>
                  <ul className="space-y-1">
                    {committee.agenda.map((a, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className="text-muted-foreground mt-0.5 shrink-0">{i + 1}.</span>
                        <span>{a.item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </section>
      )}

      {/* Alertas Normativas */}
      {normative_alerts.length > 0 && (
        <section>
          <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="size-4 text-amber-600" />
            Alertas Normativas
          </h2>
          <div className="space-y-2">
            {normative_alerts.map((alert, i) => (
              <div
                key={i}
                className={cn(
                  "flex items-start justify-between gap-3 rounded-lg border px-4 py-3",
                  alert.days_until <= 7
                    ? "bg-red-50 border-red-200"
                    : alert.days_until <= 30
                    ? "bg-amber-50 border-amber-200"
                    : "bg-blue-50 border-blue-200"
                )}
              >
                <p className="text-sm flex-1">{alert.message}</p>
                <Badge
                  variant="outline"
                  className={cn(
                    "shrink-0 border font-medium",
                    alert.days_until <= 7
                      ? "bg-red-100 text-red-700 border-red-300"
                      : alert.days_until <= 30
                      ? "bg-amber-100 text-amber-700 border-amber-300"
                      : "bg-blue-100 text-blue-700 border-blue-300"
                  )}
                >
                  {alert.days_until}d
                </Badge>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
    </TooltipProvider>
  );
}
