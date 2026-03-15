"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import {
  AlertTriangle,
  Bell,
  ShieldAlert,
  FileText,
  CalendarClock,
  Clock,
  Shield,
} from "lucide-react";
import { formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { PageGuard } from "@/components/page-guard";
import { PageSkeleton } from "@/components/page-skeleton";
import type { CommandCenterSummary, PaginatedResponse, TimelineEvent, RoleCode } from "@/types";

const ALLOWED_ROLES: RoleCode[] = ["ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA", "JEFE_DGI"];

const CATEGORY_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  ESCALATION: { label: "Escalamiento", icon: <AlertTriangle className="size-4" />, color: "bg-orange-100 text-orange-700" },
  ALERT: { label: "Alerta", icon: <Bell className="size-4" />, color: "bg-red-100 text-red-700" },
  RISK: { label: "Riesgo", icon: <ShieldAlert className="size-4" />, color: "bg-amber-100 text-amber-700" },
  DECISION: { label: "Decisión", icon: <FileText className="size-4" />, color: "bg-blue-100 text-blue-700" },
  MEETING: { label: "Reunión", icon: <CalendarClock className="size-4" />, color: "bg-purple-100 text-purple-700" },
};

export default function CentroMandoPage() {
  return (
    <PageGuard allowedRoles={ALLOWED_ROLES} skeleton={<PageSkeleton variant="dashboard" />}>
      <CentroMandoContent />
    </PageGuard>
  );
}

function CentroMandoContent() {
  const router = useRouter();
  const { user } = useAuth();

  const [summary, setSummary] = useState<CommandCenterSummary | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get<CommandCenterSummary>("/api/command-center/summary"),
      api.get<PaginatedResponse<TimelineEvent>>("/api/command-center/timeline?days=7&page_size=15"),
    ])
      .then(([s, t]) => {
        setSummary(s);
        setTimeline(t.items);
      })
      .catch(() => toast.error("Error al cargar centro de mando"))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !summary) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-64 bg-muted animate-pulse rounded" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-32 bg-muted animate-pulse rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  const kpiCards = [
    {
      title: "Escalamientos Activos",
      count: summary.escalations.active,
      icon: <AlertTriangle className="size-5" />,
      href: "/escalamiento",
      threshold: 3,
      detail: summary.escalations.by_level.map((l) => `${l.label}: ${l.count}`).join(" | ") || "Sin escalamientos",
    },
    {
      title: "Alertas Críticas",
      count: summary.alerts.critical + summary.alerts.high,
      icon: <Bell className="size-5" />,
      href: "/alertas",
      threshold: 5,
      detail: `${summary.alerts.critical} Críticas, ${summary.alerts.high} Altas`,
    },
    {
      title: "Riesgos Altos",
      count: summary.risks.high_count,
      icon: <ShieldAlert className="size-5" />,
      href: "/riesgos",
      threshold: 3,
      detail: `${summary.risks.total_active} activos en total`,
    },
    {
      title: "Decisiones Pendientes",
      count: summary.decisions.pending,
      icon: <FileText className="size-5" />,
      href: "/coordinacion",
      threshold: 5,
      detail: summary.decisions.top.length > 0
        ? `Próxima: ${summary.decisions.top[0].description?.slice(0, 40)}...`
        : "Sin decisiones pendientes",
    },
    {
      title: "SLA Vencidos",
      count: summary.sla_breaches.count,
      icon: <Clock className="size-5" />,
      href: "/servicios",
      threshold: 2,
      detail: summary.sla_breaches.count > 0
        ? `${summary.sla_breaches.count} solicitudes fuera de plazo`
        : "Todos los SLAs al día",
    },
  ];

  const getSemaforo = (count: number, threshold: number) => {
    if (count === 0) return "border-l-green-500";
    if (count <= threshold) return "border-l-amber-500";
    return "border-l-red-500";
  };

  // Relative time
  const relativeTime = (iso: string) => {
    const diff = Date.now() - new Date(iso).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours < 1) return "Hace minutos";
    if (hours < 24) return `Hace ${hours}h`;
    const days = Math.floor(hours / 24);
    return `Hace ${days}d`;
  };

  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Centro de Mando"
        description="Vista consolidada de crisis y contingencias"
        accentColor="rose"
        actions={
          <div className="flex items-center gap-2">
            <Shield className="size-5 text-muted-foreground" />
          </div>
        }
      />

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {kpiCards.map((card, idx) => (
          <Card
            key={card.title}
            className={`cursor-pointer hover:shadow-md transition-shadow border-l-4 ${getSemaforo(card.count, card.threshold)} animate-in fade-in duration-200`}
            style={{ animationDelay: `${idx * 75}ms`, animationFillMode: "both" }}
            onClick={() => router.push(card.href)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {card.title}
                </CardTitle>
                {card.icon}
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{card.count}</div>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{card.detail}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Eventos Recientes (7 días)</CardTitle>
        </CardHeader>
        <CardContent>
          {timeline.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Sin eventos recientes
            </p>
          ) : (
            <div className="space-y-3">
              {timeline.map((event, idx) => {
                const config = CATEGORY_CONFIG[event.category] || CATEGORY_CONFIG.ALERT;
                return (
                  <div
                    key={`${event.category}-${event.ref_code}-${idx}`}
                    className="flex items-start gap-3 py-2 border-b last:border-0 cursor-pointer hover:bg-accent/50 rounded-md px-1 -mx-1 transition-colors"
                    onClick={() => {
                      const routes: Record<string, string> = {
                        ESCALATION: "/escalamiento",
                        ALERT: "/alertas",
                        RISK: "/riesgos",
                        DECISION: "/coordinacion",
                        MEETING: "/reuniones",
                      };
                      const base = routes[event.category] ?? "/";
                      router.push(event.entity_id ? `${base}/${event.entity_id}` : base);
                    }}
                  >
                    <Badge variant="outline" className={`${config.color} shrink-0`}>
                      {config.icon}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-muted-foreground">
                          {config.label}
                        </span>
                        <span className="font-mono text-xs">{event.ref_code}</span>
                        {event.detail && (
                          <Badge variant="outline" className="text-[10px]">
                            {event.detail}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm line-clamp-1">{event.description}</p>
                    </div>
                    <span className="text-xs text-muted-foreground whitespace-nowrap shrink-0">
                      {relativeTime(event.event_time)}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
