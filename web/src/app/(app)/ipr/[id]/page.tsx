"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { DataTable } from "@/components/data-table";
import { AlertCard } from "@/components/alert-card";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PaginatedResponse, CompromisoListItem, ProblemaListItem, AlertaListItem } from "@/types";

interface IprDetail {
  id: string;
  codigo_bip: string;
  name: string;
  description?: string;
  ipr_type?: string;
  status?: string;
  investment_sector?: string;
  funding_source?: string;
  alert_level?: string;
  executor_name?: string;
  total_budget?: number;
  start_date?: string;
  end_date?: string;
}

const alertBorderMap: Record<string, string> = {
  CRITICO: "border-l-red-600",
  ALTO: "border-l-orange-500",
  ATENCION: "border-l-amber-400",
  INFO: "border-l-blue-500",
};

function formatDate(dateStr: string): string {
  try {
    return new Intl.DateTimeFormat("es-CL", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return "-";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export default function IprDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [ipr, setIpr] = useState<IprDetail | null>(null);
  const [iprLoading, setIprLoading] = useState(true);

  const [compromisos, setCompromisos] = useState<PaginatedResponse<CompromisoListItem> | null>(null);
  const [compLoading, setCompLoading] = useState(false);

  const [problemas, setProblemas] = useState<PaginatedResponse<ProblemaListItem> | null>(null);
  const [probLoading, setProbLoading] = useState(false);

  const [alertas, setAlertas] = useState<PaginatedResponse<AlertaListItem> | null>(null);
  const [alertLoading, setAlertLoading] = useState(false);

  useEffect(() => {
    api
      .get<IprDetail>(`/api/ipr/${id}`)
      .then(setIpr)
      .catch(() => setIpr(null))
      .finally(() => setIprLoading(false));
  }, [id]);

  const loadCompromisos = () => {
    if (compromisos) return;
    setCompLoading(true);
    api
      .get<PaginatedResponse<CompromisoListItem>>(`/api/compromisos?ipr_id=${id}&page_size=50`)
      .then(setCompromisos)
      .catch(() => setCompromisos(null))
      .finally(() => setCompLoading(false));
  };

  const loadProblemas = () => {
    if (problemas) return;
    setProbLoading(true);
    api
      .get<PaginatedResponse<ProblemaListItem>>(`/api/problemas?ipr_id=${id}&page_size=50`)
      .then(setProblemas)
      .catch(() => setProblemas(null))
      .finally(() => setProbLoading(false));
  };

  const loadAlertas = () => {
    if (alertas) return;
    setAlertLoading(true);
    api
      .get<PaginatedResponse<AlertaListItem>>(`/api/alertas?subject_type=core.ipr&subject_id=${id}&page_size=50`)
      .then(setAlertas)
      .catch(() => setAlertas(null))
      .finally(() => setAlertLoading(false));
  };

  const compromisoColumns = [
    { key: "description", label: "Descripción" },
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
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  const problemaColumns = [
    {
      key: "days_open",
      label: "Días abierto",
      render: (v: unknown) => <span className="text-xs tabular-nums">{String(v ?? 0)}d</span>,
    },
    { key: "problem_type_label", label: "Tipo" },
    {
      key: "impact_label",
      label: "Impacto",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "-")}</Badge>
      ),
    },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  const alertLevel = ipr?.alert_level;
  const borderClass = alertLevel ? alertBorderMap[alertLevel] : "";

  if (iprLoading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-40 rounded bg-muted animate-pulse" />
        <div className="h-32 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (!ipr) {
    return (
      <div className="p-6">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="size-4 mr-2" />
          Volver
        </Button>
        <p className="mt-4 text-muted-foreground">IPR no encontrado.</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <Button variant="ghost" size="sm" onClick={() => router.back()}>
        <ArrowLeft className="size-4 mr-2" />
        Volver a IPR
      </Button>

      {/* Header card */}
      <div
        className={cn(
          "rounded-xl border bg-card p-5 border-l-4",
          borderClass || "border-l-border"
        )}
      >
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="font-mono text-xs text-muted-foreground">{ipr.codigo_bip}</span>
              {ipr.ipr_type && (
                <Badge variant="outline" className="text-xs">{ipr.ipr_type}</Badge>
              )}
              {ipr.status && <StatusBadge status={ipr.status} size="sm" />}
            </div>
            <h1 className="text-xl font-bold">{ipr.name}</h1>
            {ipr.description && (
              <p className="text-sm text-muted-foreground mt-1">{ipr.description}</p>
            )}
          </div>
          <div className="text-right shrink-0">
            <p className="text-2xl font-bold">{formatCurrency(ipr.total_budget)}</p>
            <p className="text-xs text-muted-foreground">Presupuesto total</p>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-1 text-sm">
          {ipr.executor_name && (
            <div>
              <span className="text-muted-foreground">Ejecutor: </span>
              <span className="font-medium">{ipr.executor_name}</span>
            </div>
          )}
          {ipr.funding_source && (
            <div>
              <span className="text-muted-foreground">Fuente: </span>
              <span className="font-medium">{ipr.funding_source}</span>
            </div>
          )}
          {ipr.investment_sector && (
            <div>
              <span className="text-muted-foreground">Sector: </span>
              <span className="font-medium">{ipr.investment_sector}</span>
            </div>
          )}
          {ipr.start_date && (
            <div>
              <span className="text-muted-foreground">Inicio: </span>
              <span className="font-medium">{formatDate(ipr.start_date)}</span>
            </div>
          )}
          {ipr.end_date && (
            <div>
              <span className="text-muted-foreground">Término: </span>
              <span className="font-medium">{formatDate(ipr.end_date)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="compromisos" onValueChange={(tab) => {
        if (tab === "compromisos") loadCompromisos();
        if (tab === "problemas") loadProblemas();
        if (tab === "alertas") loadAlertas();
      }}>
        <TabsList>
          <TabsTrigger value="compromisos" onClick={loadCompromisos}>
            Compromisos
          </TabsTrigger>
          <TabsTrigger value="problemas" onClick={loadProblemas}>
            Problemas
          </TabsTrigger>
          <TabsTrigger value="alertas" onClick={loadAlertas}>
            Alertas
          </TabsTrigger>
        </TabsList>

        <TabsContent value="compromisos" className="mt-4">
          <DataTable
            columns={compromisoColumns}
            data={compromisos?.items ?? []}
            page={1}
            totalPages={1}
            total={compromisos?.total ?? 0}
            onPageChange={() => {}}
            isLoading={compLoading}
          />
        </TabsContent>

        <TabsContent value="problemas" className="mt-4">
          <DataTable
            columns={problemaColumns}
            data={problemas?.items ?? []}
            page={1}
            totalPages={1}
            total={problemas?.total ?? 0}
            onPageChange={() => {}}
            isLoading={probLoading}
          />
        </TabsContent>

        <TabsContent value="alertas" className="mt-4">
          {alertLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : !alertas || alertas.items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay alertas para este IPR.</p>
          ) : (
            <div className="space-y-3">
              {alertas.items.map((alert) => (
                <AlertCard key={alert.id} alert={alert} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
