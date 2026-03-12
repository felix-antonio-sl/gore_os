"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";
import { ArrowLeft, Plus, Clock, CheckCircle2, Star } from "lucide-react";
import { formatDate, formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { DGI_ROLES } from "@/types";
import type { DGIService, ServiceRequest, SLADefinition, PaginatedResponse } from "@/types";

const AREA_LABELS: Record<string, string> = {
  CG: "Control de Gestión",
  MP: "Mejora de Procesos",
  TD: "Transformación Digital",
  KC: "Gestión del Conocimiento",
};

const REQ_STATUS_COLORS: Record<string, string> = {
  RECIBIDA: "bg-slate-50 text-slate-700 border-slate-200",
  EN_EVALUACION: "bg-blue-50 text-blue-700 border-blue-200",
  ACEPTADA: "bg-cyan-50 text-cyan-700 border-cyan-200",
  EN_EJECUCION: "bg-amber-50 text-amber-700 border-amber-200",
  COMPLETADA: "bg-green-50 text-green-700 border-green-200",
  RECHAZADA: "bg-red-50 text-red-700 border-red-200",
};

interface ServiceDetailData extends DGIService {
  slas: SLADefinition[];
}

export default function ServiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
  const isJefeDGI = user?.role_code === "JEFE_DGI";
  const isDGI = user && DGI_ROLES.includes(user.role_code);

  const [service, setService] = useState<ServiceDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [requests, setRequests] = useState<PaginatedResponse<ServiceRequest> | null>(null);
  const [reqLoading, setReqLoading] = useState(true);

  // SLA form
  const [slaForm, setSlaForm] = useState({ product_type: "INFORME_FLASH", target_days: "5", description: "" });
  const [creatingSla, setCreatingSla] = useState(false);

  const fetchService = () => {
    setLoading(true);
    api
      .get<ServiceDetailData>(`/api/dgi/services/${params.id}`)
      .then(setService)
      .catch(() => toast.error("Error al cargar servicio"))
      .finally(() => setLoading(false));
  };

  const fetchRequests = () => {
    setReqLoading(true);
    api
      .get<PaginatedResponse<ServiceRequest>>(`/api/dgi/services/requests?service_id=${params.id}&page=1&page_size=50`)
      .then(setRequests)
      .catch(() => {})
      .finally(() => setReqLoading(false));
  };

  useEffect(() => {
    fetchService();
    fetchRequests();
  }, [params.id]);

  const handleCreateSla = async () => {
    if (!service) return;
    setCreatingSla(true);
    try {
      await api.post(`/api/dgi/services/${service.id}/slas`, {
        product_type: slaForm.product_type,
        target_days: parseInt(slaForm.target_days),
        description: slaForm.description || undefined,
      });
      toast.success("SLA creado");
      setSlaForm({ product_type: "INFORME_FLASH", target_days: "5", description: "" });
      fetchService();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear SLA");
    } finally {
      setCreatingSla(false);
    }
  };

  if (loading) {
    return <div className="p-6"><div className="h-64 bg-muted animate-pulse rounded-xl" /></div>;
  }

  if (!service) {
    return (
      <div className="p-6">
        <Button variant="ghost" onClick={() => router.push("/servicios")}>
          <ArrowLeft className="size-4 mr-1" /> Volver
        </Button>
        <p className="mt-4 text-muted-foreground">Servicio no encontrado</p>
      </div>
    );
  }

  // KPIs
  const completedReqs = requests?.items.filter((r) => r.status === "COMPLETADA") ?? [];
  const totalReqs = requests?.total ?? 0;
  const completionRate = totalReqs > 0 ? Math.round((completedReqs.length / totalReqs) * 100) : 0;
  const avgSatisfaction = completedReqs.length > 0
    ? (completedReqs.reduce((sum, r) => sum + (r.satisfaction_score ?? 0), 0) / completedReqs.filter(r => r.satisfaction_score).length || 0).toFixed(1)
    : "-";

  const reqColumns = [
    { key: "code", label: "Código", render: (v: unknown) => <span className="font-mono text-xs">{String(v)}</span> },
    {
      key: "status", label: "Estado",
      render: (_v: unknown, row: unknown) => {
        const r = row as ServiceRequest;
        return <Badge variant="outline" className={`text-xs ${REQ_STATUS_COLORS[r.status] ?? ""}`}>{r.status_label}</Badge>;
      },
    },
    { key: "requester_name", label: "Solicitante", render: (v: unknown) => <span className="text-sm">{String(v)}</span> },
    { key: "urgency", label: "Urgencia", render: (v: unknown) => <span className="text-xs">{String(v)}</span> },
    {
      key: "days_elapsed", label: "Días",
      render: (v: unknown, row: unknown) => {
        const r = row as ServiceRequest;
        const color = r.is_overdue ? "text-red-600 font-semibold" : "";
        return <span className={`text-xs ${color}`}>{v != null ? `${Number(v).toFixed(0)}d` : "-"}</span>;
      },
    },
    {
      key: "satisfaction_score", label: "Satisfacción",
      render: (v: unknown) => v ? <span className="text-xs flex items-center gap-0.5"><Star className="size-3 text-amber-500" />{String(v)}/5</span> : <span className="text-xs text-muted-foreground">-</span>,
    },
    { key: "created_at", label: "Creado", render: (v: unknown) => <span className="text-xs">{formatDate(v as string)}</span> },
  ];

  return (
    <div className="p-6 space-y-6">
      <Breadcrumb items={buildBreadcrumbs(pathname, service?.name)} />
      <Button variant="ghost" size="sm" onClick={() => router.push("/servicios")}>
        <ArrowLeft className="size-4 mr-1" /> Volver
      </Button>

      {/* Hero */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs text-muted-foreground">{service.code}</span>
            <Badge variant="outline">{AREA_LABELS[service.area] ?? service.area}</Badge>
            <Badge variant="outline">{service.status_label}</Badge>
          </div>
          <h1 className="text-xl font-bold">{service.name}</h1>
        </div>
        {service.sla_days && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Clock className="size-4" /> SLA: {service.sla_days} días
          </div>
        )}
      </div>

      {/* KPI cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-4">
            <p className="text-xs text-muted-foreground">Solicitudes</p>
            <p className="text-2xl font-bold">{totalReqs}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-xs text-muted-foreground">Cumplimiento SLA</p>
            <p className="text-2xl font-bold">{completionRate}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-xs text-muted-foreground">Satisfacción</p>
            <p className="text-2xl font-bold">{avgSatisfaction}</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="info">
        <TabsList>
          <TabsTrigger value="info">Información</TabsTrigger>
          <TabsTrigger value="slas">SLAs ({service.slas.length})</TabsTrigger>
          <TabsTrigger value="requests">Solicitudes ({totalReqs})</TabsTrigger>
        </TabsList>

        <TabsContent value="info" className="mt-4 space-y-4">
          {service.description && (
            <Card>
              <CardHeader><CardTitle className="text-base">Descripción</CardTitle></CardHeader>
              <CardContent><p className="text-sm whitespace-pre-wrap">{service.description}</p></CardContent>
            </Card>
          )}
          {service.how_to_request && (
            <Card>
              <CardHeader><CardTitle className="text-base">Cómo Solicitar</CardTitle></CardHeader>
              <CardContent><p className="text-sm whitespace-pre-wrap">{service.how_to_request}</p></CardContent>
            </Card>
          )}
          {service.deliverables && (
            <Card>
              <CardHeader><CardTitle className="text-base">Entregables</CardTitle></CardHeader>
              <CardContent><p className="text-sm whitespace-pre-wrap">{service.deliverables}</p></CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="slas" className="mt-4 space-y-4">
          {service.slas.length === 0 ? (
            <EmptyState compact title="Sin SLAs" description="No hay SLAs definidos para este servicio" />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {service.slas.map((sla) => (
                <Card key={sla.id}>
                  <CardContent className="pt-4 space-y-1">
                    <p className="font-medium text-sm">{sla.product_type_label}</p>
                    {sla.description && <p className="text-xs text-muted-foreground">{sla.description}</p>}
                    <p className="text-xs">
                      <Clock className="size-3 inline mr-1" />
                      {sla.target_days} días
                      {sla.target_hour && ` — ${sla.target_hour}`}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
          {isJefeDGI && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Agregar SLA</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Producto</Label>
                    <Select value={slaForm.product_type} onValueChange={(v) => setSlaForm({ ...slaForm, product_type: v })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="INFORME_FLASH">Informe Flash</SelectItem>
                        <SelectItem value="INFORME_SEMANAL">Informe Semanal</SelectItem>
                        <SelectItem value="INFORME_MENSUAL">Informe Mensual</SelectItem>
                        <SelectItem value="LEVANTAMIENTO_PROCESO">Levantamiento Proceso</SelectItem>
                        <SelectItem value="ANALISIS_INDICADOR">Análisis Indicador</SelectItem>
                        <SelectItem value="EVALUACION_CARTERA">Evaluación Cartera</SelectItem>
                        <SelectItem value="SOPORTE_TD">Soporte TD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Días</Label>
                    <Input type="number" value={slaForm.target_days} onChange={(e) => setSlaForm({ ...slaForm, target_days: e.target.value })} />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Descripción</Label>
                    <Input value={slaForm.description} onChange={(e) => setSlaForm({ ...slaForm, description: e.target.value })} />
                  </div>
                </div>
                <Button size="sm" onClick={handleCreateSla} disabled={creatingSla}>
                  <Plus className="size-4 mr-1" />{creatingSla ? "Creando..." : "Agregar SLA"}
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="requests" className="mt-4">
          <DataTable
            columns={reqColumns}
            data={requests?.items ?? []}
            page={1}
            totalPages={1}
            total={totalReqs}
            onPageChange={() => {}}
            isLoading={reqLoading}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
