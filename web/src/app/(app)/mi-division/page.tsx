"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { KpiCard } from "@/components/kpi-card";
import { DataTable } from "@/components/data-table";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { KPICardData, CompromisoListItem } from "@/types";

interface TeamMember {
  user_id: string;
  name: string;
  pendientes: number;
  en_progreso: number;
  completados: number;
  vencidos: number;
  total: number;
}

interface MiDivisionData {
  kpis: KPICardData[];
  team: TeamMember[];
  commitments: CompromisoListItem[];
}

export default function MiDivisionPage() {
  const { user } = useAuth();
  const [data, setData] = useState<MiDivisionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [teamSort, setTeamSort] = useState<"name" | "vencidos" | "total">("vencidos");
  const [vencidosPage, setVencidosPage] = useState(1);

  useEffect(() => {
    api
      .get<MiDivisionData>("/api/dashboard/mi-division")
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, []);

  const VENCIDOS_PAGE_SIZE = 10;

  const sortedTeam = data?.team ? [...data.team].sort((a, b) => {
    if (teamSort === "vencidos") return b.vencidos - a.vencidos;
    if (teamSort === "total") return b.total - a.total;
    return a.name.localeCompare(b.name);
  }) : [];

  const vencidosTotalPages = Math.max(Math.ceil((data?.commitments.length ?? 0) / VENCIDOS_PAGE_SIZE), 1);
  const vencidosPaged = data?.commitments.slice((vencidosPage - 1) * VENCIDOS_PAGE_SIZE, vencidosPage * VENCIDOS_PAGE_SIZE) ?? [];

  if (!user || user.role_code !== "JEFE_DIVISION") {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">Solo disponible para Jefe de División.</p>
      </div>
    );
  }

  const commitmentColumns = [
    {
      key: "days_remaining",
      label: "Urgencia",
      render: (_: unknown, row: unknown) => {
        const r = row as CompromisoListItem;
        return <TemporalIndicator daysRemaining={r.days_remaining} state={r.state} />;
      },
    },
    {
      key: "description",
      label: "Descripción",
      render: (v: unknown) => (
        <span className="font-medium line-clamp-1 max-w-xs">{String(v ?? "")}</span>
      ),
    },
    { key: "responsible_name", label: "Responsable" },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Mi División</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Estado del equipo y compromisos de la división
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
            <KpiCard key={i} label={kpi.label} value={kpi.value} sublabel={kpi.sublabel} color={kpi.color} />
          ))}
        </div>
      )}

      {/* Carga por persona */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Carga por Persona</CardTitle>
            <div className="flex gap-1">
              {(["vencidos", "total", "name"] as const).map((key) => (
                <Button
                  key={key}
                  size="sm"
                  variant={teamSort === key ? "default" : "outline"}
                  className="h-7 text-xs"
                  onClick={() => setTeamSort(key)}
                >
                  {key === "vencidos" ? "Vencidos" : key === "total" ? "Total" : "Nombre"}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-12 rounded bg-muted animate-pulse" />
              ))}
            </div>
          ) : !data?.team.length ? (
            <p className="text-sm text-muted-foreground">Sin datos de equipo.</p>
          ) : (
            <div className="space-y-2">
              {sortedTeam.map((member) => (
                <div
                  key={member.user_id}
                  className="flex items-center justify-between py-2 border-b last:border-0"
                >
                  <span className="font-medium text-sm">{member.name}</span>
                  <div className="flex gap-2">
                    {member.vencidos > 0 && (
                      <Badge variant="destructive" className="text-xs">
                        {member.vencidos} vencidos
                      </Badge>
                    )}
                    <Badge variant="outline" className="text-xs">
                      {member.pendientes} pendientes
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      {member.en_progreso} en progreso
                    </Badge>
                    <Badge className="text-xs bg-green-100 text-green-800 hover:bg-green-100">
                      {member.completados} completados
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Compromisos vencidos */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Compromisos Vencidos</h2>
        <DataTable
          columns={commitmentColumns}
          data={vencidosPaged}
          page={vencidosPage}
          totalPages={vencidosTotalPages}
          total={data?.commitments.length ?? 0}
          onPageChange={setVencidosPage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
