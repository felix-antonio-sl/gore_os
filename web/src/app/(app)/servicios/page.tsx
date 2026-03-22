"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DrawerPanel } from "@/components/drawer-panel";
import { toast } from "sonner";
import { Plus, Clock, Send, Star, CheckCircle2 } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { DGI_AREA_COLORS } from "@/lib/status-colors";
import { formatDate } from "@/lib/format";
import type { DGIService, ServiceRequest, SLADefinition, PaginatedResponse } from "@/types";

const AREA_LABELS: Record<string, string> = {
  CG: "Control de Gestión",
  MP: "Mejora de Procesos",
  TD: "Transformación Digital",
  KC: "Gestión del Conocimiento",
};

const AREAS = ["TODOS", "CG", "MP", "TD", "KC"];

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

export default function ServiciosPage() {
  const { user } = useAuth();
  const isJefeDGI = user?.role_code === "JEFE_DGI";

  // ---------- List state ----------
  const [services, setServices] = useState<DGIService[]>([]);
  const [loading, setLoading] = useState(true);
  const [areaFilter, setAreaFilter] = useState("TODOS");
  const [refreshKey, setRefreshKey] = useState(0);

  // ---------- Create service drawer ----------
  const [createOpen, setCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: "",
    description: "",
    area: "CG",
    sla_days: "",
    how_to_request: "",
    deliverables: "",
  });

  // ---------- Request drawer ----------
  const [requestOpen, setRequestOpen] = useState(false);
  const [requestSubmitting, setRequestSubmitting] = useState(false);
  const [requestSubmitted, setRequestSubmitted] = useState(false);
  const [requestResultCode, setRequestResultCode] = useState("");
  const [activeServices, setActiveServices] = useState<DGIService[]>([]);
  const [activeServicesLoading, setActiveServicesLoading] = useState(false);
  const [requestForm, setRequestForm] = useState({
    service_id: "",
    description: "",
    urgency: "NORMAL",
  });

  // ---------- Detail drawer ----------
  const [detailId, setDetailId] = useState<string | null>(null);
  const [detailService, setDetailService] = useState<ServiceDetailData | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailRequests, setDetailRequests] = useState<PaginatedResponse<ServiceRequest> | null>(null);
  const [detailReqLoading, setDetailReqLoading] = useState(false);

  // SLA form (inside detail drawer)
  const [slaForm, setSlaForm] = useState({ product_type: "INFORME_FLASH", target_days: "5", description: "" });
  const [creatingSla, setCreatingSla] = useState(false);

  // ---------- Fetch services list ----------
  const fetchServices = () => {
    setLoading(true);
    const areaParam = areaFilter !== "TODOS" ? `?area=${areaFilter}` : "";
    api
      .get<DGIService[]>(`/api/dgi/services${areaParam}`)
      .then(setServices)
      .catch(() => toast.error("Error al cargar servicios"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchServices();
  }, [areaFilter, refreshKey]);

  // ---------- Fetch active services for request drawer ----------
  const fetchActiveServices = () => {
    setActiveServicesLoading(true);
    api
      .get<DGIService[]>("/api/dgi/services?status=ACTIVO")
      .then(setActiveServices)
      .catch(() => toast.error("Error al cargar servicios"))
      .finally(() => setActiveServicesLoading(false));
  };

  // ---------- Fetch detail ----------
  useEffect(() => {
    if (!detailId) {
      setDetailService(null);
      setDetailRequests(null);
      return;
    }
    setDetailLoading(true);
    setDetailReqLoading(true);
    api
      .get<ServiceDetailData>(`/api/dgi/services/${detailId}`)
      .then(setDetailService)
      .catch(() => toast.error("Error al cargar servicio"))
      .finally(() => setDetailLoading(false));
    api
      .get<PaginatedResponse<ServiceRequest>>(`/api/dgi/services/requests?service_id=${detailId}&page=1&page_size=50`)
      .then(setDetailRequests)
      .catch(() => {})
      .finally(() => setDetailReqLoading(false));
  }, [detailId]);

  // ---------- Handlers ----------
  const handleCreateService = async () => {
    if (!createForm.name.trim()) {
      toast.error("El nombre es obligatorio");
      return;
    }
    setCreating(true);
    try {
      const result = await api.post<DGIService>("/api/dgi/services", {
        name: createForm.name,
        description: createForm.description || undefined,
        area: createForm.area,
        sla_days: createForm.sla_days ? parseInt(createForm.sla_days) : undefined,
        how_to_request: createForm.how_to_request || undefined,
        deliverables: createForm.deliverables || undefined,
      });
      toast.success(`Servicio ${result.code} creado`);
      setCreateOpen(false);
      setCreateForm({ name: "", description: "", area: "CG", sla_days: "", how_to_request: "", deliverables: "" });
      setRefreshKey((k) => k + 1);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear servicio");
    } finally {
      setCreating(false);
    }
  };

  const handleSubmitRequest = async () => {
    if (!requestForm.service_id) {
      toast.error("Seleccione un servicio");
      return;
    }
    if (!requestForm.description.trim()) {
      toast.error("La descripción es obligatoria");
      return;
    }
    setRequestSubmitting(true);
    try {
      const result = await api.post<{ id: string; code: string }>("/api/dgi/services/requests", {
        service_id: requestForm.service_id,
        description: requestForm.description,
        urgency: requestForm.urgency,
      });
      setRequestResultCode(result.code);
      setRequestSubmitted(true);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al enviar solicitud");
    } finally {
      setRequestSubmitting(false);
    }
  };

  const handleCloseRequestDrawer = () => {
    setRequestOpen(false);
    setRequestSubmitted(false);
    setRequestResultCode("");
    setRequestForm({ service_id: "", description: "", urgency: "NORMAL" });
  };

  const handleOpenRequestDrawer = () => {
    setRequestSubmitted(false);
    setRequestResultCode("");
    setRequestForm({ service_id: "", description: "", urgency: "NORMAL" });
    fetchActiveServices();
    setRequestOpen(true);
  };

  const handleCreateSla = async () => {
    if (!detailService) return;
    setCreatingSla(true);
    try {
      await api.post(`/api/dgi/services/${detailService.id}/slas`, {
        product_type: slaForm.product_type,
        target_days: parseInt(slaForm.target_days),
        description: slaForm.description || undefined,
      });
      toast.success("SLA creado");
      setSlaForm({ product_type: "INFORME_FLASH", target_days: "5", description: "" });
      // Refresh detail
      api.get<ServiceDetailData>(`/api/dgi/services/${detailService.id}`).then(setDetailService);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear SLA");
    } finally {
      setCreatingSla(false);
    }
  };

  // ---------- Detail KPIs ----------
  const completedReqs = detailRequests?.items.filter((r) => r.status === "COMPLETADA") ?? [];
  const totalReqs = detailRequests?.total ?? 0;
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
      <PageHeader
        title="Catálogo de Servicios DGI"
        description="Servicios disponibles para todas las divisiones del GORE"
        accentColor="teal"
        actions={
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={handleOpenRequestDrawer}>
              <Send className="size-4 mr-1" />
              Solicitar Servicio
            </Button>
            {isJefeDGI && (
              <Button size="sm" onClick={() => setCreateOpen(true)}>
                <Plus className="size-4 mr-1" />
                Nuevo Servicio
              </Button>
            )}
          </div>
        }
      />

      {/* Area filter */}
      <div className="flex gap-1 flex-wrap">
        {AREAS.map((area) => (
          <Button
            key={area}
            variant={areaFilter === area ? "default" : "outline"}
            size="sm"
            onClick={() => setAreaFilter(area)}
          >
            {area === "TODOS" ? "Todos" : AREA_LABELS[area] ?? area}
          </Button>
        ))}
      </div>

      {/* Services grid */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-44 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : services.length === 0 ? (
        <EmptyState title="Sin servicios" description="El catálogo de servicios DGI aparecerá aquí" />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((svc) => (
            <Card
              key={svc.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setDetailId(svc.id)}
            >
              <CardContent className="pt-5 space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className={`text-xs ${DGI_AREA_COLORS[svc.area] ?? ""}`}>
                    {AREA_LABELS[svc.area] ?? svc.area}
                  </Badge>
                  <span className="font-mono text-xs text-muted-foreground">{svc.code}</span>
                </div>
                <h3 className="font-semibold text-sm">{svc.name}</h3>
                {svc.description && (
                  <p className="text-xs text-muted-foreground line-clamp-2">{svc.description}</p>
                )}
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  {svc.sla_days && (
                    <span className="flex items-center gap-1">
                      <Clock className="size-3" />
                      SLA: {svc.sla_days}d
                    </span>
                  )}
                  <Badge variant="outline" className="text-xs">
                    {svc.status_label}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* ========== Create Service Drawer ========== */}
      <DrawerPanel open={createOpen} onClose={() => setCreateOpen(false)} title="Nuevo Servicio">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Nombre *</Label>
            <Input
              value={createForm.name}
              onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
              placeholder="Nombre del servicio"
            />
          </div>
          <div className="space-y-2">
            <Label>Área</Label>
            <Select value={createForm.area} onValueChange={(v) => setCreateForm({ ...createForm, area: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="CG">Control de Gestión</SelectItem>
                <SelectItem value="MP">Mejora de Procesos</SelectItem>
                <SelectItem value="TD">Transformación Digital</SelectItem>
                <SelectItem value="KC">Gestión del Conocimiento</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Descripción</Label>
            <Textarea
              value={createForm.description}
              onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
              rows={2}
            />
          </div>
          <div className="space-y-2">
            <Label>SLA (días)</Label>
            <Input
              type="number"
              value={createForm.sla_days}
              onChange={(e) => setCreateForm({ ...createForm, sla_days: e.target.value })}
              placeholder="5"
            />
          </div>
          <div className="space-y-2">
            <Label>Cómo solicitar</Label>
            <Textarea
              value={createForm.how_to_request}
              onChange={(e) => setCreateForm({ ...createForm, how_to_request: e.target.value })}
              rows={2}
            />
          </div>
          <div className="space-y-2">
            <Label>Entregables</Label>
            <Textarea
              value={createForm.deliverables}
              onChange={(e) => setCreateForm({ ...createForm, deliverables: e.target.value })}
              rows={2}
            />
          </div>
          <Button className="w-full" onClick={handleCreateService} disabled={creating}>
            {creating ? "Creando..." : "Crear Servicio"}
          </Button>
        </div>
      </DrawerPanel>

      {/* ========== Request Service Drawer ========== */}
      <DrawerPanel open={requestOpen} onClose={handleCloseRequestDrawer} title="Solicitar Servicio">
        {requestSubmitted ? (
          <div className="text-center space-y-4 py-8">
            <CheckCircle2 className="size-12 text-green-500 mx-auto" />
            <h2 className="text-xl font-bold">Solicitud Enviada</h2>
            <p className="text-muted-foreground">
              Su solicitud <span className="font-mono font-semibold">{requestResultCode}</span> ha sido
              registrada. El equipo DGI la evaluará a la brevedad.
            </p>
            <Button variant="outline" onClick={handleCloseRequestDrawer}>
              Cerrar
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Servicio *</Label>
              <Select
                value={requestForm.service_id}
                onValueChange={(v) => setRequestForm({ ...requestForm, service_id: v })}
                disabled={activeServicesLoading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar servicio" />
                </SelectTrigger>
                <SelectContent>
                  {activeServices.map((svc) => (
                    <SelectItem key={svc.id} value={svc.id}>
                      {svc.name} ({svc.area})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Descripción *</Label>
              <Textarea
                value={requestForm.description}
                onChange={(e) => setRequestForm({ ...requestForm, description: e.target.value })}
                placeholder="Describa lo que necesita"
                rows={4}
              />
            </div>

            <div className="space-y-2">
              <Label>Urgencia</Label>
              <Select value={requestForm.urgency} onValueChange={(v) => setRequestForm({ ...requestForm, urgency: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="BAJA">Baja</SelectItem>
                  <SelectItem value="NORMAL">Normal</SelectItem>
                  <SelectItem value="ALTA">Alta</SelectItem>
                  <SelectItem value="CRITICA">Crítica</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button className="w-full" onClick={handleSubmitRequest} disabled={requestSubmitting}>
              {requestSubmitting ? "Enviando..." : "Enviar Solicitud"}
            </Button>
          </div>
        )}
      </DrawerPanel>

      {/* ========== Service Detail Drawer ========== */}
      <DrawerPanel
        open={!!detailId}
        onClose={() => { setDetailId(null); setSlaForm({ product_type: "INFORME_FLASH", target_days: "5", description: "" }); }}
        title="Detalle del Servicio"
      >
        {detailLoading ? (
          <div className="space-y-4">
            <div className="h-16 bg-muted animate-pulse rounded-lg" />
            <div className="h-24 bg-muted animate-pulse rounded-lg" />
            <div className="h-32 bg-muted animate-pulse rounded-lg" />
          </div>
        ) : !detailService ? (
          <p className="text-muted-foreground">Servicio no encontrado</p>
        ) : (
          <div className="space-y-6">
            {/* Hero */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-muted-foreground">{detailService.code}</span>
                <Badge variant="outline">{AREA_LABELS[detailService.area] ?? detailService.area}</Badge>
                <Badge variant="outline">{detailService.status_label}</Badge>
              </div>
              <h2 className="text-lg font-bold">{detailService.name}</h2>
              {detailService.sla_days && (
                <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                  <Clock className="size-4" /> SLA: {detailService.sla_days} días
                </div>
              )}
            </div>

            {/* KPI cards */}
            <div className="grid gap-3 grid-cols-3">
              <Card>
                <CardContent className="pt-3 pb-3">
                  <p className="text-xs text-muted-foreground">Solicitudes</p>
                  <p className="text-xl font-bold">{totalReqs}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-3 pb-3">
                  <p className="text-xs text-muted-foreground">SLA</p>
                  <p className="text-xl font-bold">{completionRate}%</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-3 pb-3">
                  <p className="text-xs text-muted-foreground">Satisfacción</p>
                  <p className="text-xl font-bold">{avgSatisfaction}</p>
                </CardContent>
              </Card>
            </div>

            <Tabs defaultValue="info">
              <TabsList>
                <TabsTrigger value="info">Información</TabsTrigger>
                <TabsTrigger value="slas">SLAs ({detailService.slas.length})</TabsTrigger>
                <TabsTrigger value="requests">Solicitudes ({totalReqs})</TabsTrigger>
              </TabsList>

              <TabsContent value="info" className="mt-4 space-y-4">
                {detailService.description && (
                  <Card>
                    <CardHeader><CardTitle className="text-base">Descripción</CardTitle></CardHeader>
                    <CardContent><p className="text-sm whitespace-pre-wrap">{detailService.description}</p></CardContent>
                  </Card>
                )}
                {detailService.how_to_request && (
                  <Card>
                    <CardHeader><CardTitle className="text-base">Cómo Solicitar</CardTitle></CardHeader>
                    <CardContent><p className="text-sm whitespace-pre-wrap">{detailService.how_to_request}</p></CardContent>
                  </Card>
                )}
                {detailService.deliverables && (
                  <Card>
                    <CardHeader><CardTitle className="text-base">Entregables</CardTitle></CardHeader>
                    <CardContent><p className="text-sm whitespace-pre-wrap">{detailService.deliverables}</p></CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="slas" className="mt-4 space-y-4">
                {detailService.slas.length === 0 ? (
                  <EmptyState compact title="Sin SLAs" description="No hay SLAs definidos para este servicio" />
                ) : (
                  <div className="grid gap-3">
                    {detailService.slas.map((sla) => (
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
                      <div className="space-y-3">
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
                  data={detailRequests?.items ?? []}
                  page={1}
                  totalPages={1}
                  total={totalReqs}
                  onPageChange={() => {}}
                  isLoading={detailReqLoading}
                />
              </TabsContent>
            </Tabs>
          </div>
        )}
      </DrawerPanel>
    </div>
  );
}
