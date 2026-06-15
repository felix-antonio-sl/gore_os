"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DateField } from "@/components/date-field";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import {
  CalendarDays,
  Users,
  Gavel,
  AlertTriangle,
  Clock,
  Video,
} from "lucide-react";
import { formatDate, formatDateTime } from "@/lib/format";
import type { CalendarEvent } from "@/types";

const DGI_ROLES = ["JEFE_DGI", "ESP_TD", "ESP_CONTROL_GESTION", "ESP_PROCESOS"];

const EVENT_TYPE_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  SESSION: { label: "Sesión", icon: <Video className="size-4" />, color: "bg-blue-100 text-blue-800 border-blue-300" },
  INTERACTION: { label: "Interacción", icon: <Users className="size-4" />, color: "bg-purple-100 text-purple-800 border-purple-300" },
  DECISION: { label: "Decisión AR", icon: <Gavel className="size-4" />, color: "bg-amber-100 text-amber-800 border-amber-300" },
  ESCALATION: { label: "Escalamiento", icon: <AlertTriangle className="size-4" />, color: "bg-red-100 text-red-800 border-red-300" },
  SLA: { label: "SLA", icon: <Clock className="size-4" />, color: "bg-orange-100 text-orange-800 border-orange-300" },
};

const SEVERITY_CLASSES: Record<string, string> = {
  rojo: "border-l-red-500",
  amber: "border-l-amber-500",
  verde: "border-l-green-500",
};

function groupByDate(events: CalendarEvent[]): Map<string, CalendarEvent[]> {
  const groups = new Map<string, CalendarEvent[]>();
  for (const e of events) {
    const dateKey = e.event_date.slice(0, 10);
    if (!groups.has(dateKey)) groups.set(dateKey, []);
    groups.get(dateKey)!.push(e);
  }
  return groups;
}

export default function CalendarioPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const typeFilter = searchParams.get("type") ?? "";
  const fromParam = searchParams.get("from") ?? new Date().toISOString().slice(0, 10);
  const toParam = searchParams.get("to") ?? new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);

  const isDGI = user && DGI_ROLES.includes(user.role_code);

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) params.delete(k);
        else params.set(k, String(v));
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams();
    params.set("from", fromParam);
    params.set("to", toParam);
    if (typeFilter) params.set("type", typeFilter);

    api
      .get<CalendarEvent[]>(`/api/dgi/coordination/calendar?${params.toString()}`)
      .then(setEvents)
      .catch(() => setEvents([]))
      .finally(() => setIsLoading(false));
  }, [fromParam, toParam, typeFilter]);

  const grouped = groupByDate(events);
  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Calendario DGI"
        description="Agenda consolidada: sesiones, interacciones, plazos, escalamientos y SLAs"
        accentColor="cyan"
      />

      {/* Date range */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2">
          <label className="text-sm text-muted-foreground">Desde</label>
          <DateField
            value={fromParam}
            onChange={(v) => router.push(buildUrl({ from: v }))}
            className="w-40"
          />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-muted-foreground">Hasta</label>
          <DateField
            value={toParam}
            onChange={(v) => router.push(buildUrl({ to: v }))}
            min={fromParam}
            className="w-40"
          />
        </div>
      </div>

      {/* Type filter chips */}
      <div className="flex flex-wrap gap-2">
        {[
          { key: "", label: "Todos" },
          { key: "SESSION", label: "Sesiones" },
          { key: "INTERACTION", label: "Interacciones" },
          { key: "DECISION", label: "Decisiones" },
          { key: "ESCALATION", label: "Escalamientos" },
          { key: "SLA", label: "SLA" },
        ].map(({ key, label }) => (
          <Button
            key={key}
            variant={typeFilter === key ? "default" : "outline"}
            size="sm"
            onClick={() => router.push(buildUrl({ type: key }))}
          >
            {label}
          </Button>
        ))}
      </div>

      {/* Event list */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
      ) : events.length === 0 ? (
        <EmptyState
          title="No hay eventos en el período seleccionado"
          icon={<CalendarDays className="size-10 text-muted-foreground/50" />}
        />
      ) : (
        <div className="space-y-6">
          {Array.from(grouped.entries()).map(([dateKey, dayEvents]) => {
            const isToday = dateKey === today;
            const isPast = dateKey < today;
            return (
              <div key={dateKey}>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className={`text-sm font-semibold ${isToday ? "text-blue-600" : isPast ? "text-muted-foreground" : ""}`}>
                    {formatDate(dateKey)}
                    {isToday && (
                      <Badge variant="default" className="ml-2 text-[10px] px-1.5 py-0 bg-blue-600">
                        Hoy
                      </Badge>
                    )}
                  </h3>
                  <div className="flex-1 border-t border-border" />
                </div>
                <div className="space-y-2">
                  {dayEvents.map((event, idx) => {
                    const config = EVENT_TYPE_CONFIG[event.event_type] ?? EVENT_TYPE_CONFIG.SESSION;
                    const severityClass = SEVERITY_CLASSES[event.severity ?? "verde"] ?? SEVERITY_CLASSES.verde;
                    const drillRoute: Record<string, string> = {
                      ESCALATION: "/escalamiento",
                      DECISION: "/coordinacion",
                      SESSION: "/reuniones",
                      INTERACTION: "/coordinacion/divisiones",
                      SLA: "/servicios",
                    };
                    const href = event.entity_id
                      ? `${drillRoute[event.event_type] ?? "/calendario"}/${event.entity_id}`
                      : drillRoute[event.event_type] ?? "/calendario";
                    return (
                      <div
                        key={`${event.entity_id ?? idx}`}
                        onClick={() => router.push(href)}
                        className={`flex items-start gap-3 p-3 rounded-lg border border-l-4 ${severityClass} bg-card hover:bg-accent/50 transition-colors cursor-pointer`}
                      >
                        <div className={`p-1.5 rounded ${config.color} shrink-0`}>
                          {config.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <span className="text-sm font-medium line-clamp-1">{event.title}</span>
                          {event.description && (
                            <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                              {event.description}
                            </p>
                          )}
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {formatDateTime(event.event_date)}
                          </p>
                        </div>
                        {event.severity === "rojo" && (
                          <Badge variant="destructive" className="text-[10px] shrink-0">
                            Vencido
                          </Badge>
                        )}
                        {event.severity === "amber" && (
                          <Badge variant="outline" className="text-[10px] border-amber-400 text-amber-600 shrink-0">
                            Pronto
                          </Badge>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
