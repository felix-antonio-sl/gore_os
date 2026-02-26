"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { StatusBadge } from "@/components/status-badge";
import { DataTable } from "@/components/data-table";
import { AlertCard } from "@/components/alert-card";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { DrawerPanel } from "@/components/drawer-panel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowLeft, Plus, UserPlus, Pencil } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PaginatedResponse, CompromisoListItem, ProblemaListItem, AlertaListItem, ConvenioListItem } from "@/types";

interface IprDetail {
  id: string;
  codigo_bip: string;
  name: string;
  description?: string;
  ipr_type?: string;
  status?: string;
  investment_sector?: string;
  funding_source?: string;
  fund_category?: string;
  fund_category_label?: string;
  mechanism?: string;
  mechanism_label?: string;
  mcd_phase?: string;
  mcd_phase_label?: string;
  alert_level?: string;
  executor_name?: string;
  formulator_name?: string;
  total_budget?: number;
  start_date?: string;
  end_date?: string;
}

interface ProgressReport {
  id: string;
  report_number: number;
  report_date: string;
  physical_progress: number | null;
  financial_progress: number | null;
  description: string | null;
  issues_detected: string | null;
  reported_by_name: string | null;
  created_at: string;
}

interface UserOption {
  id: string;
  nombre: string;
  apellido_paterno: string;
  division_name: string | null;
}

const alertBorderMap: Record<string, string> = {
  CRITICO: "border-l-red-600",
  ALTO: "border-l-orange-500",
  ATENCION: "border-l-amber-400",
  INFO: "border-l-blue-500",
};

const mechanismColors: Record<string, string> = {
  SNI: "bg-indigo-100 text-indigo-800 border-indigo-200",
  C33: "bg-violet-100 text-violet-800 border-violet-200",
  FRIL: "bg-emerald-100 text-emerald-800 border-emerald-200",
  GLOSA06: "bg-sky-100 text-sky-800 border-sky-200",
  TRANSFER: "bg-amber-100 text-amber-800 border-amber-200",
  SUBV8: "bg-rose-100 text-rose-800 border-rose-200",
  FRPD: "bg-teal-100 text-teal-800 border-teal-200",
};

const mcdPhaseColors: Record<string, string> = {
  F0: "bg-slate-100 text-slate-700 border-slate-200",
  F1: "bg-blue-100 text-blue-700 border-blue-200",
  F2: "bg-cyan-100 text-cyan-700 border-cyan-200",
  F3: "bg-amber-100 text-amber-700 border-amber-200",
  F4: "bg-green-100 text-green-700 border-green-200",
  F5: "bg-gray-100 text-gray-700 border-gray-200",
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
  const { user } = useAuth();
  const id = params.id as string;

  const [ipr, setIpr] = useState<IprDetail | null>(null);
  const [iprLoading, setIprLoading] = useState(true);

  const [compromisos, setCompromisos] = useState<PaginatedResponse<CompromisoListItem> | null>(null);
  const [compLoading, setCompLoading] = useState(false);

  const [problemas, setProblemas] = useState<PaginatedResponse<ProblemaListItem> | null>(null);
  const [probLoading, setProbLoading] = useState(false);

  const [alertas, setAlertas] = useState<PaginatedResponse<AlertaListItem> | null>(null);
  const [alertLoading, setAlertLoading] = useState(false);

  const [convenios, setConvenios] = useState<PaginatedResponse<ConvenioListItem> | null>(null);
  const [convLoading, setConvLoading] = useState(false);

  // Avances state
  const [avances, setAvances] = useState<ProgressReport[] | null>(null);
  const [avancesLoading, setAvancesLoading] = useState(false);

  // Avance form drawer
  const [showAvanceForm, setShowAvanceForm] = useState(false);
  const [avanceDate, setAvanceDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [avancePhysical, setAvancePhysical] = useState("");
  const [avanceFinancial, setAvanceFinancial] = useState("");
  const [avanceDesc, setAvanceDesc] = useState("");
  const [avanceIssues, setAvanceIssues] = useState("");
  const [avanceSubmitting, setAvanceSubmitting] = useState(false);
  const [avanceError, setAvanceError] = useState<string | null>(null);

  // Assignee drawer
  const [showAssignee, setShowAssignee] = useState(false);
  const [usersList, setUsersList] = useState<UserOption[]>([]);
  const [selectedAssignee, setSelectedAssignee] = useState("");
  const [assigneeSubmitting, setAssigneeSubmitting] = useState(false);
  const [assigneeError, setAssigneeError] = useState<string | null>(null);

  // Edit IPR drawer
  const [showEdit, setShowEdit] = useState(false);
  const [editName, setEditName] = useState("");
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  const canAssign = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);
  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);

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

  const loadConvenios = () => {
    if (convenios) return;
    setConvLoading(true);
    api
      .get<PaginatedResponse<ConvenioListItem>>(`/api/convenios?ipr_id=${id}&page_size=50`)
      .then(setConvenios)
      .catch(() => setConvenios(null))
      .finally(() => setConvLoading(false));
  };

  const loadAvances = (force = false) => {
    if (avances && !force) return;
    setAvancesLoading(true);
    api
      .get<ProgressReport[]>(`/api/ipr/${id}/avances`)
      .then(setAvances)
      .catch(() => setAvances(null))
      .finally(() => setAvancesLoading(false));
  };

  const handleAvanceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!avanceDate) {
      setAvanceError("La fecha es requerida.");
      return;
    }
    setAvanceSubmitting(true);
    setAvanceError(null);
    try {
      await api.post(`/api/ipr/${id}/avances`, {
        report_date: avanceDate,
        physical_progress: avancePhysical ? parseFloat(avancePhysical) : null,
        financial_progress: avanceFinancial ? parseFloat(avanceFinancial) : null,
        description: avanceDesc || null,
        issues_detected: avanceIssues || null,
      });
      setShowAvanceForm(false);
      setAvanceDate(new Date().toISOString().split("T")[0]);
      setAvancePhysical("");
      setAvanceFinancial("");
      setAvanceDesc("");
      setAvanceIssues("");
      setAvances(null);
      loadAvances(true);
    } catch (err) {
      setAvanceError(err instanceof Error ? err.message : "Error al registrar avance");
    } finally {
      setAvanceSubmitting(false);
    }
  };

  const openEditDrawer = () => {
    setEditName(ipr?.name ?? "");
    setEditError(null);
    setShowEdit(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editName.trim()) {
      setEditError("El nombre es requerido.");
      return;
    }
    setEditSubmitting(true);
    setEditError(null);
    try {
      await api.patch(`/api/ipr/${id}`, { name: editName.trim() });
      setShowEdit(false);
      // Refresh IPR data
      api.get<IprDetail>(`/api/ipr/${id}`).then(setIpr).catch(() => {});
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Error al actualizar IPR");
    } finally {
      setEditSubmitting(false);
    }
  };

  const openAssigneeDrawer = () => {
    setShowAssignee(true);
    setAssigneeError(null);
    setSelectedAssignee("");
    api.get<UserOption[]>("/api/catalogs/users").then(setUsersList).catch(() => {});
  };

  const handleAssigneeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAssignee) {
      setAssigneeError("Seleccione un usuario.");
      return;
    }
    setAssigneeSubmitting(true);
    setAssigneeError(null);
    try {
      await api.patch(`/api/ipr/${id}`, { assignee_id: selectedAssignee });
      setShowAssignee(false);
    } catch (err) {
      setAssigneeError(err instanceof Error ? err.message : "Error al asignar responsable");
    } finally {
      setAssigneeSubmitting(false);
    }
  };

  const compromisoColumns = [
    { key: "description", label: "Descripcion" },
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
      label: "Dias abierto",
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

  const avanceColumns = [
    {
      key: "report_number",
      label: "#",
      render: (v: unknown) => <span className="font-mono text-xs">{String(v)}</span>,
    },
    {
      key: "report_date",
      label: "Fecha",
      render: (v: unknown) => <span className="text-xs">{v ? formatDate(String(v)) : "-"}</span>,
    },
    {
      key: "physical_progress",
      label: "% Fisico",
      render: (v: unknown) => (
        <span className="text-xs tabular-nums">{v != null ? `${Number(v).toFixed(1)}%` : "-"}</span>
      ),
    },
    {
      key: "financial_progress",
      label: "% Financiero",
      render: (v: unknown) => (
        <span className="text-xs tabular-nums">{v != null ? `${Number(v).toFixed(1)}%` : "-"}</span>
      ),
    },
    {
      key: "description",
      label: "Descripcion",
      render: (v: unknown) => (
        <span className="text-xs line-clamp-1 max-w-xs">{String(v ?? "-")}</span>
      ),
    },
    { key: "reported_by_name", label: "Reportado por" },
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
          <div className="flex flex-col items-end gap-2 shrink-0">
            <div className="text-right">
              <p className="text-2xl font-bold">{formatCurrency(ipr.total_budget)}</p>
              <p className="text-xs text-muted-foreground">Presupuesto total</p>
            </div>
            <div className="flex gap-2">
              {canEdit && (
                <Button size="sm" variant="outline" onClick={openEditDrawer}>
                  <Pencil className="size-4 mr-1" />
                  Editar
                </Button>
              )}
              {canAssign && (
                <Button size="sm" variant="outline" onClick={openAssigneeDrawer}>
                  <UserPlus className="size-4 mr-1" />
                  Asignar Responsable
                </Button>
              )}
            </div>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {ipr.mechanism && (
            <div className="flex items-center gap-1.5">
              <span className="text-muted-foreground">Mecanismo:</span>
              <Badge variant="outline" className={cn("text-xs", mechanismColors[ipr.mechanism])}>
                {ipr.mechanism}
              </Badge>
              {ipr.mechanism_label && (
                <span className="text-xs text-muted-foreground">{ipr.mechanism_label}</span>
              )}
            </div>
          )}
          {ipr.funding_source && (
            <div className="flex items-center gap-1.5">
              <span className="text-muted-foreground">Fuente:</span>
              <span className="font-medium">{ipr.fund_category_label || ipr.funding_source}</span>
            </div>
          )}
          {ipr.mcd_phase && (
            <div className="flex items-center gap-1.5">
              <span className="text-muted-foreground">Fase MCD:</span>
              <Badge variant="outline" className={cn("text-xs", mcdPhaseColors[ipr.mcd_phase])}>
                {ipr.mcd_phase}
              </Badge>
              {ipr.mcd_phase_label && (
                <span className="text-xs text-muted-foreground">{ipr.mcd_phase_label}</span>
              )}
            </div>
          )}
          {ipr.executor_name && (
            <div>
              <span className="text-muted-foreground">Ejecutor: </span>
              <span className="font-medium">{ipr.executor_name}</span>
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
              <span className="text-muted-foreground">Termino: </span>
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
        if (tab === "convenios") loadConvenios();
        if (tab === "avances") loadAvances();
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
          <TabsTrigger value="convenios" onClick={loadConvenios}>
            Convenios
          </TabsTrigger>
          <TabsTrigger value="avances" onClick={() => loadAvances()}>
            Avances
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

        <TabsContent value="convenios" className="mt-4">
          {convLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : !convenios || convenios.items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay convenios para este IPR.</p>
          ) : (
            <DataTable
              columns={[
                {
                  key: "agreement_number",
                  label: "N Convenio",
                  render: (v: unknown) => <span className="font-mono text-xs">{String(v ?? "-")}</span>,
                },
                {
                  key: "agreement_type_label",
                  label: "Tipo",
                  render: (v: unknown) => <Badge variant="outline" className="text-xs">{String(v ?? "-")}</Badge>,
                },
                {
                  key: "total_amount",
                  label: "Monto",
                  render: (v: unknown) => (
                    <span className="font-mono text-xs tabular-nums">
                      {v != null ? new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", notation: "compact", maximumFractionDigits: 1 }).format(Number(v)) : "-"}
                    </span>
                  ),
                },
                {
                  key: "state",
                  label: "Estado",
                  render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
                },
                {
                  key: "installment_count",
                  label: "Cuotas",
                  render: (_: unknown, row: unknown) => {
                    const r = row as ConvenioListItem;
                    return <span className="text-xs">{r.paid_installments}/{r.installment_count}</span>;
                  },
                },
              ]}
              data={convenios.items}
              page={1}
              totalPages={1}
              total={convenios.total}
              onPageChange={() => {}}
              isLoading={convLoading}
            />
          )}
        </TabsContent>

        <TabsContent value="avances" className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {avances ? `${avances.length} reportes de avance` : ""}
            </p>
            <Button size="sm" onClick={() => setShowAvanceForm(true)}>
              <Plus className="size-4 mr-1" />
              Registrar Avance
            </Button>
          </div>
          {avancesLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-12 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : !avances || avances.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay reportes de avance para este IPR.</p>
          ) : (
            <DataTable
              columns={avanceColumns}
              data={avances}
              page={1}
              totalPages={1}
              total={avances.length}
              onPageChange={() => {}}
              isLoading={avancesLoading}
            />
          )}
        </TabsContent>
      </Tabs>

      {/* Avance Form Drawer */}
      <DrawerPanel
        open={showAvanceForm}
        onClose={() => setShowAvanceForm(false)}
        title="Registrar Avance"
      >
        <form onSubmit={handleAvanceSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Fecha del reporte *</label>
            <Input
              type="date"
              value={avanceDate}
              onChange={(e) => setAvanceDate(e.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Avance fisico (%)</label>
            <Input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={avancePhysical}
              onChange={(e) => setAvancePhysical(e.target.value)}
              placeholder="0 - 100"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Avance financiero (%)</label>
            <Input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={avanceFinancial}
              onChange={(e) => setAvanceFinancial(e.target.value)}
              placeholder="0 - 100"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripcion</label>
            <textarea
              className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={avanceDesc}
              onChange={(e) => setAvanceDesc(e.target.value)}
              placeholder="Descripcion del avance..."
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Problemas detectados</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={avanceIssues}
              onChange={(e) => setAvanceIssues(e.target.value)}
              placeholder="Problemas o riesgos detectados..."
            />
          </div>

          {avanceError && (
            <p className="text-sm text-red-600">{avanceError}</p>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={avanceSubmitting}>
              {avanceSubmitting ? "Guardando..." : "Guardar Avance"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowAvanceForm(false)}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>

      {/* Assignee Drawer */}
      <DrawerPanel
        open={showAssignee}
        onClose={() => setShowAssignee(false)}
        title="Asignar Responsable"
      >
        <form onSubmit={handleAssigneeSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Responsable *</label>
            <Select value={selectedAssignee} onValueChange={setSelectedAssignee}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione usuario" />
              </SelectTrigger>
              <SelectContent>
                {usersList.map((u) => (
                  <SelectItem key={u.id} value={u.id}>
                    {u.nombre} {u.apellido_paterno}
                    {u.division_name ? ` (${u.division_name})` : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {assigneeError && (
            <p className="text-sm text-red-600">{assigneeError}</p>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={assigneeSubmitting}>
              {assigneeSubmitting ? "Asignando..." : "Asignar"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowAssignee(false)}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>

      {/* Edit IPR Drawer */}
      <DrawerPanel
        open={showEdit}
        onClose={() => setShowEdit(false)}
        title="Editar IPR"
      >
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Nombre *</label>
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder="Nombre del IPR"
            />
          </div>

          {editError && (
            <p className="text-sm text-red-600">{editError}</p>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={editSubmitting}>
              {editSubmitting ? "Guardando..." : "Guardar"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowEdit(false)}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>
    </div>
  );
}
