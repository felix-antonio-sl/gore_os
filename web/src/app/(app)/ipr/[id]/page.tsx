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
import { ArrowLeft, Plus, UserPlus, Pencil, Trash2, MapPin, Flag, Building2, CheckCircle2, ShieldCheck, ShieldX, ChevronRight, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ComboboxAsync, type ComboboxOption } from "@/components/combobox-async";
import { IprCompromisoDrawer } from "@/components/ipr-compromiso-drawer";
import { IprProblemaDrawer } from "@/components/ipr-problema-drawer";
import { IprConvenioDrawer } from "@/components/ipr-convenio-drawer";
import type {
  PaginatedResponse, CompromisoListItem, ProblemaListItem, AlertaListItem,
  ConvenioListItem, BudgetCommitmentItem, IprPartyItem, IprTerritoryItem,
  IprMilestoneItem, CategoryRef, TerritoryOption, IprTransition, ActoListItem,
} from "@/types";
import { WRITE_OPERATIONAL_ROLES } from "@/types";

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

const MCD_PHASES = [
  { code: "F0", label: "Formulación" },
  { code: "F1", label: "Admisibilidad" },
  { code: "F2", label: "Evaluación" },
  { code: "F3", label: "Priorización" },
  { code: "F4", label: "Ejecución" },
  { code: "F5", label: "Cierre" },
];

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

  // CDPs state
  const [cdps, setCdps] = useState<BudgetCommitmentItem[] | null>(null);
  const [cdpsLoading, setCdpsLoading] = useState(false);

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

  // Inline creation drawers
  const [showCompromisoDrawer, setShowCompromisoDrawer] = useState(false);
  const [showProblemaDrawer, setShowProblemaDrawer] = useState(false);
  const [showConvenioDrawer, setShowConvenioDrawer] = useState(false);

  // Partes state
  const [partes, setPartes] = useState<IprPartyItem[] | null>(null);
  const [partesLoading, setPartesLoading] = useState(false);
  const [showParteForm, setShowParteForm] = useState(false);
  const [parteOrgId, setParteOrgId] = useState("");
  const [parteRoleId, setParteRoleId] = useState("");
  const [parteRoles, setParteRoles] = useState<CategoryRef[]>([]);
  const [parteSubmitting, setParteSubmitting] = useState(false);
  const [parteError, setParteError] = useState<string | null>(null);

  // Territorio state
  const [territorios, setTerritorios] = useState<IprTerritoryItem[] | null>(null);
  const [terrLoading, setTerrLoading] = useState(false);
  const [showTerrForm, setShowTerrForm] = useState(false);
  const [terrTerritoryId, setTerrTerritoryId] = useState("");
  const [terrImpactId, setTerrImpactId] = useState("");
  const [terrOptions, setTerrOptions] = useState<TerritoryOption[]>([]);
  const [terrImpactTypes, setTerrImpactTypes] = useState<CategoryRef[]>([]);
  const [terrSubmitting, setTerrSubmitting] = useState(false);
  const [terrError, setTerrError] = useState<string | null>(null);

  // Hitos state
  const [hitos, setHitos] = useState<IprMilestoneItem[] | null>(null);
  const [hitosLoading, setHitosLoading] = useState(false);

  // Resoluciones state
  const [resoluciones, setResoluciones] = useState<ActoListItem[] | null>(null);
  const [resolucionesLoading, setResolucionesLoading] = useState(false);
  const [showHitoForm, setShowHitoForm] = useState(false);
  const [hitoTypeId, setHitoTypeId] = useState("");
  const [hitoPlannedDate, setHitoPlannedDate] = useState("");
  const [hitoDesc, setHitoDesc] = useState("");
  const [hitoTypes, setHitoTypes] = useState<CategoryRef[]>([]);
  const [hitoSubmitting, setHitoSubmitting] = useState(false);
  const [hitoError, setHitoError] = useState<string | null>(null);

  // Transitions state
  const [transitions, setTransitions] = useState<IprTransition[] | null>(null);
  const [transLoading, setTransLoading] = useState(false);
  const [selectedTransition, setSelectedTransition] = useState("");
  const [transSubmitting, setTransSubmitting] = useState(false);
  const [transError, setTransError] = useState<string | null>(null);

  const canAssign = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);
  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);
  const canTransition = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);
  const canCreateCompromiso = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);
  const canCreateProblema = user && WRITE_OPERATIONAL_ROLES.includes(user.role_code);
  const canCreateConvenio = user && WRITE_OPERATIONAL_ROLES.includes(user.role_code);
  const canManageChildren = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);

  useEffect(() => {
    api
      .get<IprDetail>(`/api/ipr/${id}`)
      .then(setIpr)
      .catch(() => setIpr(null))
      .finally(() => setIprLoading(false));
  }, [id]);

  const loadTransitions = () => {
    if (!canTransition) return;
    setTransLoading(true);
    api
      .get<IprTransition[]>(`/api/ipr/${id}/transiciones`)
      .then(setTransitions)
      .catch(() => setTransitions(null))
      .finally(() => setTransLoading(false));
  };

  useEffect(() => {
    if (canTransition && !iprLoading && ipr) loadTransitions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canTransition, iprLoading]);

  const handleTransition = async () => {
    if (!selectedTransition) return;
    setTransSubmitting(true);
    setTransError(null);
    try {
      await api.patch(`/api/ipr/${id}`, { status_id: selectedTransition });
      // Refresh IPR data and transitions
      const updated = await api.get<IprDetail>(`/api/ipr/${id}`);
      setIpr(updated);
      setTransitions(null);
      setSelectedTransition("");
      loadTransitions();
    } catch (err) {
      setTransError(err instanceof Error ? err.message : "Error al transicionar");
    } finally {
      setTransSubmitting(false);
    }
  };

  const loadCompromisos = (force = false) => {
    if (compromisos && !force) return;
    setCompLoading(true);
    api
      .get<PaginatedResponse<CompromisoListItem>>(`/api/compromisos?ipr_id=${id}&page_size=50`)
      .then(setCompromisos)
      .catch(() => setCompromisos(null))
      .finally(() => setCompLoading(false));
  };

  const loadProblemas = (force = false) => {
    if (problemas && !force) return;
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

  const loadConvenios = (force = false) => {
    if (convenios && !force) return;
    setConvLoading(true);
    api
      .get<PaginatedResponse<ConvenioListItem>>(`/api/convenios?ipr_id=${id}&page_size=50`)
      .then(setConvenios)
      .catch(() => setConvenios(null))
      .finally(() => setConvLoading(false));
  };

  const loadCdps = () => {
    if (cdps) return;
    setCdpsLoading(true);
    api
      .get<BudgetCommitmentItem[]>(`/api/presupuesto/cdps-por-ipr/${id}`)
      .then(setCdps)
      .catch(() => setCdps(null))
      .finally(() => setCdpsLoading(false));
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

  const loadPartes = (force = false) => {
    if (partes && !force) return;
    setPartesLoading(true);
    api
      .get<IprPartyItem[]>(`/api/ipr/${id}/partes`)
      .then(setPartes)
      .catch(() => setPartes(null))
      .finally(() => setPartesLoading(false));
  };

  const loadTerritorios = (force = false) => {
    if (territorios && !force) return;
    setTerrLoading(true);
    api
      .get<IprTerritoryItem[]>(`/api/ipr/${id}/territorio`)
      .then(setTerritorios)
      .catch(() => setTerritorios(null))
      .finally(() => setTerrLoading(false));
  };

  const loadHitos = (force = false) => {
    if (hitos && !force) return;
    setHitosLoading(true);
    api
      .get<IprMilestoneItem[]>(`/api/ipr/${id}/hitos`)
      .then(setHitos)
      .catch(() => setHitos(null))
      .finally(() => setHitosLoading(false));
  };

  const loadResoluciones = () => {
    if (resoluciones) return;
    setResolucionesLoading(true);
    api
      .get<{ items: ActoListItem[] }>(`/api/actos?ipr_id=${id}&page_size=100`)
      .then((data) => setResoluciones(data.items))
      .catch(() => setResoluciones(null))
      .finally(() => setResolucionesLoading(false));
  };

  const openParteForm = () => {
    setParteOrgId("");
    setParteRoleId("");
    setParteError(null);
    setShowParteForm(true);
    if (parteRoles.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/ipr_party_role").then(setParteRoles).catch(() => {});
    }
  };

  const handleParteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!parteOrgId || !parteRoleId) {
      setParteError("Organizacion y rol son requeridos.");
      return;
    }
    setParteSubmitting(true);
    setParteError(null);
    try {
      await api.post(`/api/ipr/${id}/partes`, {
        organization_id: parteOrgId,
        party_role_id: parteRoleId,
      });
      setShowParteForm(false);
      loadPartes(true);
    } catch (err) {
      setParteError(err instanceof Error ? err.message : "Error al agregar parte");
    } finally {
      setParteSubmitting(false);
    }
  };

  const handleDeleteParty = async (partyId: string) => {
    try {
      await api.delete(`/api/ipr/${id}/partes/${partyId}`);
      loadPartes(true);
    } catch {
      // silent
    }
  };

  const openTerrForm = () => {
    setTerrTerritoryId("");
    setTerrImpactId("");
    setTerrError(null);
    setShowTerrForm(true);
    if (terrOptions.length === 0) {
      api.get<TerritoryOption[]>("/api/catalogs/territories").then(setTerrOptions).catch(() => {});
    }
    if (terrImpactTypes.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/territory_impact").then(setTerrImpactTypes).catch(() => {});
    }
  };

  const handleTerrSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!terrTerritoryId || !terrImpactId) {
      setTerrError("Territorio y tipo de impacto son requeridos.");
      return;
    }
    setTerrSubmitting(true);
    setTerrError(null);
    try {
      await api.post(`/api/ipr/${id}/territorio`, {
        territory_id: terrTerritoryId,
        impact_type_id: terrImpactId,
      });
      setShowTerrForm(false);
      loadTerritorios(true);
    } catch (err) {
      setTerrError(err instanceof Error ? err.message : "Error al agregar territorio");
    } finally {
      setTerrSubmitting(false);
    }
  };

  const handleDeleteTerritory = async (recordId: string) => {
    try {
      await api.delete(`/api/ipr/${id}/territorio/${recordId}`);
      loadTerritorios(true);
    } catch {
      // silent
    }
  };

  const openHitoForm = () => {
    setHitoTypeId("");
    setHitoPlannedDate("");
    setHitoDesc("");
    setHitoError(null);
    setShowHitoForm(true);
    if (hitoTypes.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/milestone_type").then(setHitoTypes).catch(() => {});
    }
  };

  const handleHitoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!hitoTypeId || !hitoPlannedDate) {
      setHitoError("Tipo de hito y fecha planificada son requeridos.");
      return;
    }
    setHitoSubmitting(true);
    setHitoError(null);
    try {
      await api.post(`/api/ipr/${id}/hitos`, {
        milestone_type_id: hitoTypeId,
        planned_date: hitoPlannedDate,
        description: hitoDesc || null,
      });
      setShowHitoForm(false);
      loadHitos(true);
    } catch (err) {
      setHitoError(err instanceof Error ? err.message : "Error al crear hito");
    } finally {
      setHitoSubmitting(false);
    }
  };

  const handleCompleteHito = async (hitoId: string) => {
    try {
      await api.patch(`/api/ipr/${id}/hitos/${hitoId}`, {
        actual_date: new Date().toISOString().split("T")[0],
      });
      loadHitos(true);
    } catch {
      // silent
    }
  };

  const searchOrganizations = async (query: string): Promise<ComboboxOption[]> => {
    const data = await api.get<{ id: string; name: string; code: string }[]>(
      `/api/catalogs/organizations?search=${encodeURIComponent(query)}`
    );
    return data.map((o) => ({ value: o.id, label: `${o.name} (${o.code})` }));
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

      {/* Phase Stepper */}
      {ipr.mcd_phase && (
        <div className="rounded-xl border bg-card p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-muted-foreground">Ciclo de Vida MCD</h3>
            {ipr.mcd_phase && (
              <Badge variant="outline" className={cn("text-xs", mcdPhaseColors[ipr.mcd_phase])}>
                {ipr.mcd_phase} — {ipr.mcd_phase_label}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-0">
            {MCD_PHASES.map((phase, idx) => {
              const currentIdx = MCD_PHASES.findIndex(p => p.code === ipr.mcd_phase);
              const isActive = idx === currentIdx;
              const isPast = idx < currentIdx;
              return (
                <div key={phase.code} className="flex items-center flex-1 min-w-0">
                  <div className="flex flex-col items-center flex-1">
                    <div
                      className={cn(
                        "size-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors",
                        isActive && "bg-primary text-primary-foreground border-primary",
                        isPast && "bg-primary/20 text-primary border-primary/40",
                        !isActive && !isPast && "bg-muted text-muted-foreground border-border",
                      )}
                    >
                      {isPast ? <CheckCircle2 className="size-4" /> : phase.code}
                    </div>
                    <span className={cn(
                      "text-[10px] mt-1 text-center leading-tight",
                      isActive ? "font-semibold text-foreground" : "text-muted-foreground",
                    )}>
                      {phase.label}
                    </span>
                  </div>
                  {idx < MCD_PHASES.length - 1 && (
                    <div className={cn(
                      "h-0.5 flex-1 min-w-2",
                      idx < currentIdx ? "bg-primary/40" : "bg-border",
                    )} />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Transition Section */}
      {canTransition && transitions && transitions.length > 0 && (
        <div className="rounded-xl border bg-card p-4">
          <h3 className="text-sm font-medium mb-3">Avanzar Estado</h3>
          <div className="flex items-end gap-3 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <Select value={selectedTransition} onValueChange={setSelectedTransition}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Seleccionar estado destino..." />
                </SelectTrigger>
                <SelectContent>
                  {transitions.map((t) => (
                    <SelectItem key={t.id} value={t.id} disabled={t.blocked}>
                      <span className="flex items-center gap-2">
                        <span>{t.label}</span>
                        {t.target_phase && (
                          <Badge variant="outline" className={cn("text-[10px] py-0", mcdPhaseColors[t.target_phase] || "")}>
                            {t.target_phase}
                          </Badge>
                        )}
                        {t.phase_change && !t.blocked && (
                          <ChevronRight className="size-3 text-green-600" />
                        )}
                        {t.blocked && (
                          <ShieldX className="size-3 text-red-500" />
                        )}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              size="sm"
              disabled={!selectedTransition || transSubmitting}
              onClick={handleTransition}
            >
              {transSubmitting && <Loader2 className="size-4 mr-1 animate-spin" />}
              Transicionar
            </Button>
          </div>
          {/* Gate details for selected transition */}
          {selectedTransition && (() => {
            const sel = transitions.find(t => t.id === selectedTransition);
            if (!sel || sel.gates.length === 0) return null;
            return (
              <div className="mt-3 space-y-1">
                <p className="text-xs font-medium text-muted-foreground">
                  Gates para {ipr.mcd_phase} → {sel.target_phase}:
                </p>
                {sel.gates.map((g) => (
                  <div key={g.name} className="flex items-center gap-2 text-xs">
                    {g.met ? (
                      <ShieldCheck className="size-3.5 text-green-600 shrink-0" />
                    ) : (
                      <ShieldX className="size-3.5 text-red-500 shrink-0" />
                    )}
                    <span className={g.met ? "text-muted-foreground" : "text-red-600 font-medium"}>
                      {g.detail}
                    </span>
                  </div>
                ))}
              </div>
            );
          })()}
          {transError && (
            <p className="text-xs text-red-600 mt-2">{transError}</p>
          )}
        </div>
      )}
      {canTransition && transLoading && (
        <div className="rounded-xl border bg-card p-4">
          <div className="h-8 rounded bg-muted animate-pulse" />
        </div>
      )}

      {/* Tabs */}
      <Tabs defaultValue="compromisos" onValueChange={(tab) => {
        if (tab === "compromisos") loadCompromisos();
        if (tab === "problemas") loadProblemas();
        if (tab === "alertas") loadAlertas();
        if (tab === "convenios") loadConvenios();
        if (tab === "cdps") loadCdps();
        if (tab === "avances") loadAvances();
        if (tab === "partes") loadPartes();
        if (tab === "territorio") loadTerritorios();
        if (tab === "hitos") loadHitos();
      }}>
        <TabsList className="flex-wrap">
          <TabsTrigger value="compromisos" onClick={() => loadCompromisos()}>
            Compromisos
          </TabsTrigger>
          <TabsTrigger value="problemas" onClick={() => loadProblemas()}>
            Problemas
          </TabsTrigger>
          <TabsTrigger value="alertas" onClick={loadAlertas}>
            Alertas
          </TabsTrigger>
          <TabsTrigger value="convenios" onClick={() => loadConvenios()}>
            Convenios
          </TabsTrigger>
          <TabsTrigger value="cdps" onClick={loadCdps}>
            CDPs
          </TabsTrigger>
          <TabsTrigger value="avances" onClick={() => loadAvances()}>
            Avances
          </TabsTrigger>
          <TabsTrigger value="partes" onClick={() => loadPartes()}>
            Partes
          </TabsTrigger>
          <TabsTrigger value="territorio" onClick={() => loadTerritorios()}>
            Territorio
          </TabsTrigger>
          <TabsTrigger value="hitos" onClick={() => loadHitos()}>
            Hitos
          </TabsTrigger>
          <TabsTrigger value="resoluciones" onClick={() => loadResoluciones()}>
            Resoluciones
          </TabsTrigger>
        </TabsList>

        <TabsContent value="compromisos" className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {compromisos ? `${compromisos.total} compromisos` : ""}
            </p>
            {canCreateCompromiso && (
              <Button size="sm" onClick={() => setShowCompromisoDrawer(true)}>
                <Plus className="size-4 mr-1" />
                Nuevo Compromiso
              </Button>
            )}
          </div>
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
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {problemas ? `${problemas.total} problemas` : ""}
            </p>
            {canCreateProblema && (
              <Button size="sm" onClick={() => setShowProblemaDrawer(true)}>
                <Plus className="size-4 mr-1" />
                Nuevo Problema
              </Button>
            )}
          </div>
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
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onViewSubject={(type, subjectId) => {
                    if (type === "core.ipr") router.push(`/ipr/${subjectId}`);
                    else if (type === "core.agreement") router.push("/convenios");
                    else if (type === "core.operational_commitment") router.push("/compromisos");
                    else if (type === "core.ipr_problem") router.push("/problemas");
                  }}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="convenios" className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {convenios ? `${convenios.total} convenios` : ""}
            </p>
            {canCreateConvenio && (
              <Button size="sm" onClick={() => setShowConvenioDrawer(true)}>
                <Plus className="size-4 mr-1" />
                Agregar Convenio
              </Button>
            )}
          </div>
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
              onRowClick={() => {
                router.push("/convenios");
              }}
              isLoading={convLoading}
            />
          )}
        </TabsContent>

        <TabsContent value="cdps" className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {cdps ? `${cdps.length} CDPs vinculados` : ""}
            </p>
          </div>
          {cdpsLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : !cdps || cdps.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay CDPs vinculados a este IPR.</p>
          ) : (
            <div className="space-y-2">
              {cdps.map((cdp) => (
                <div key={cdp.id} className="rounded-md border px-3 py-2 text-sm">
                  <div className="flex justify-between">
                    <span className="font-mono text-xs">{cdp.commitment_number}</span>
                    {cdp.status_label && <StatusBadge status={cdp.status_label} size="sm" />}
                  </div>
                  <div className="flex justify-between mt-1">
                    <span className="text-muted-foreground text-xs">
                      {cdp.issued_at ? formatDate(cdp.issued_at) : "-"}
                      {cdp.expires_at ? ` → ${formatDate(cdp.expires_at)}` : ""}
                    </span>
                    <span className="font-mono text-xs">{formatCurrency(cdp.amount)}</span>
                  </div>
                </div>
              ))}
            </div>
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

        {/* Partes Tab */}
        <TabsContent value="partes" className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {partes ? `${partes.length} partes involucradas` : ""}
            </p>
            {canManageChildren && (
              <Button size="sm" onClick={openParteForm}>
                <Plus className="size-4 mr-1" />
                Agregar Parte
              </Button>
            )}
          </div>
          {partesLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : !partes || partes.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay partes registradas para este IPR.</p>
          ) : (
            <div className="space-y-2">
              {partes.map((p) => (
                <div key={p.id} className="rounded-md border px-4 py-3 text-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Building2 className="size-4 text-muted-foreground" />
                      <span className="font-medium">{p.organization_name}</span>
                      {p.organization_code && (
                        <span className="font-mono text-xs text-muted-foreground">{p.organization_code}</span>
                      )}
                      {p.is_primary && (
                        <Badge variant="default" className="text-xs">Principal</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">{p.role_label}</Badge>
                      {canManageChildren && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="size-7 p-0 text-muted-foreground hover:text-red-600"
                          onClick={() => handleDeleteParty(p.id)}
                        >
                          <Trash2 className="size-3.5" />
                        </Button>
                      )}
                    </div>
                  </div>
                  {(p.contact_person || p.contact_email || p.agreement_number) && (
                    <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                      {p.contact_person && <span>Contacto: {p.contact_person}</span>}
                      {p.contact_email && <span>{p.contact_email}</span>}
                      {p.agreement_number && <span>Convenio: {p.agreement_number}</span>}
                      {p.valid_from && <span>Desde: {formatDate(p.valid_from)}</span>}
                      {p.valid_to && <span>Hasta: {formatDate(p.valid_to)}</span>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Territorio Tab */}
        <TabsContent value="territorio" className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {territorios ? `${territorios.length} territorios vinculados` : ""}
            </p>
            {canManageChildren && (
              <Button size="sm" onClick={openTerrForm}>
                <Plus className="size-4 mr-1" />
                Agregar Territorio
              </Button>
            )}
          </div>
          {terrLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : !territorios || territorios.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay territorios vinculados a este IPR.</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {territorios.map((t) => (
                <div key={t.id} className="rounded-lg border p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <MapPin className="size-4 text-muted-foreground shrink-0" />
                      <div>
                        <p className="font-medium text-sm">{t.territory_name}</p>
                        {t.territory_code && (
                          <p className="text-xs text-muted-foreground font-mono">{t.territory_code}</p>
                        )}
                      </div>
                    </div>
                    {canManageChildren && (
                      <Button
                        size="sm"
                        variant="ghost"
                        className="size-7 p-0 text-muted-foreground hover:text-red-600"
                        onClick={() => handleDeleteTerritory(t.id)}
                      >
                        <Trash2 className="size-3.5" />
                      </Button>
                    )}
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">{t.impact_type_label}</Badge>
                    {t.is_primary && <Badge variant="default" className="text-xs">Principal</Badge>}
                  </div>
                  {t.notes && <p className="mt-2 text-xs text-muted-foreground">{t.notes}</p>}
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Hitos Tab */}
        <TabsContent value="hitos" className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {hitos ? `${hitos.length} hitos` : ""}
            </p>
            {canManageChildren && (
              <Button size="sm" onClick={openHitoForm}>
                <Plus className="size-4 mr-1" />
                Nuevo Hito
              </Button>
            )}
          </div>
          {hitosLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : !hitos || hitos.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay hitos registrados para este IPR.</p>
          ) : (
            <div className="space-y-3">
              {hitos.map((h) => {
                const today = new Date().toISOString().split("T")[0];
                const isCompleted = !!h.actual_date;
                const isOverdue = !isCompleted && h.planned_date < today;
                const isFuture = !isCompleted && h.planned_date >= today;
                const borderColor = isCompleted
                  ? (h.deviation_days != null && h.deviation_days > 0 ? "border-l-amber-500" : "border-l-green-500")
                  : isOverdue
                  ? "border-l-red-500"
                  : "border-l-gray-300";

                return (
                  <div
                    key={h.id}
                    className={cn("rounded-md border border-l-4 px-4 py-3 text-sm", borderColor)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Flag className="size-4 text-muted-foreground" />
                        <span className="font-medium">{h.milestone_type_label}</span>
                        {h.deviation_days != null && (
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-xs",
                              h.deviation_days > 0
                                ? "text-red-600 border-red-200"
                                : h.deviation_days < 0
                                ? "text-green-600 border-green-200"
                                : "text-gray-600"
                            )}
                          >
                            {h.deviation_days > 0
                              ? `+${h.deviation_days}d atraso`
                              : h.deviation_days < 0
                              ? `${h.deviation_days}d adelanto`
                              : "A tiempo"}
                          </Badge>
                        )}
                        {isOverdue && (
                          <Badge variant="outline" className="text-xs text-red-600 border-red-200">
                            Vencido
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        {isCompleted ? (
                          <Badge variant="default" className="text-xs bg-green-600">Completado</Badge>
                        ) : canManageChildren ? (
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-xs h-7"
                            onClick={() => handleCompleteHito(h.id)}
                          >
                            <CheckCircle2 className="size-3.5 mr-1" />
                            Completar
                          </Button>
                        ) : isFuture ? (
                          <Badge variant="outline" className="text-xs">Pendiente</Badge>
                        ) : null}
                      </div>
                    </div>
                    <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                      <span>Planificado: {formatDate(h.planned_date)}</span>
                      {h.actual_date && <span>Completado: {formatDate(h.actual_date)}</span>}
                      {h.completed_by_name && <span>Por: {h.completed_by_name}</span>}
                    </div>
                    {h.description && (
                      <p className="mt-1 text-xs text-muted-foreground">{h.description}</p>
                    )}
                    {h.verification_notes && (
                      <p className="mt-1 text-xs italic text-muted-foreground">Notas: {h.verification_notes}</p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </TabsContent>

        <TabsContent value="resoluciones" className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              {resoluciones ? `${resoluciones.length} resoluciones vinculadas` : ""}
            </p>
          </div>
          {resolucionesLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : !resoluciones || resoluciones.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay resoluciones vinculadas a este IPR.</p>
          ) : (
            <div className="space-y-2">
              {resoluciones.map((acto) => (
                <div
                  key={acto.id}
                  className="rounded-md border px-3 py-2 text-sm cursor-pointer hover:bg-muted/50"
                  onClick={() => router.push(`/actos?search=${encodeURIComponent(acto.act_number)}`)}
                >
                  <div className="flex justify-between">
                    <span className="font-mono text-xs">{acto.act_number}</span>
                    <StatusBadge status={acto.state} size="sm" />
                  </div>
                  <p className="text-xs line-clamp-1 mt-1">{acto.subject}</p>
                  <div className="flex justify-between mt-1">
                    <span className="text-muted-foreground text-xs">
                      {acto.resolution_type_label ?? acto.act_type_label}
                    </span>
                    {acto.budget_amount !== null && acto.budget_amount !== undefined && (
                      <span className="font-mono text-xs">{formatCurrency(acto.budget_amount)}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
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

      {/* Parte Form Drawer */}
      <DrawerPanel
        open={showParteForm}
        onClose={() => setShowParteForm(false)}
        title="Agregar Parte"
      >
        <form onSubmit={handleParteSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Organizacion *</label>
            <ComboboxAsync
              value={parteOrgId}
              onChange={setParteOrgId}
              searchFn={searchOrganizations}
              placeholder="Buscar organizacion..."
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Rol *</label>
            <Select value={parteRoleId} onValueChange={setParteRoleId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione rol" />
              </SelectTrigger>
              <SelectContent>
                {parteRoles.map((r) => (
                  <SelectItem key={r.id} value={r.id}>
                    {r.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {parteError && <p className="text-sm text-red-600">{parteError}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={parteSubmitting}>
              {parteSubmitting ? "Guardando..." : "Agregar Parte"}
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowParteForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>

      {/* Territorio Form Drawer */}
      <DrawerPanel
        open={showTerrForm}
        onClose={() => setShowTerrForm(false)}
        title="Agregar Territorio"
      >
        <form onSubmit={handleTerrSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Territorio *</label>
            <Select value={terrTerritoryId} onValueChange={setTerrTerritoryId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione territorio" />
              </SelectTrigger>
              <SelectContent>
                {terrOptions.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.name} ({t.territory_type})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Tipo de impacto *</label>
            <Select value={terrImpactId} onValueChange={setTerrImpactId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione tipo de impacto" />
              </SelectTrigger>
              <SelectContent>
                {terrImpactTypes.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {terrError && <p className="text-sm text-red-600">{terrError}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={terrSubmitting}>
              {terrSubmitting ? "Guardando..." : "Agregar Territorio"}
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowTerrForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>

      {/* Hito Form Drawer */}
      <DrawerPanel
        open={showHitoForm}
        onClose={() => setShowHitoForm(false)}
        title="Nuevo Hito"
      >
        <form onSubmit={handleHitoSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Tipo de hito *</label>
            <Select value={hitoTypeId} onValueChange={setHitoTypeId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione tipo" />
              </SelectTrigger>
              <SelectContent>
                {hitoTypes.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Fecha planificada *</label>
            <Input
              type="date"
              value={hitoPlannedDate}
              onChange={(e) => setHitoPlannedDate(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripcion</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={hitoDesc}
              onChange={(e) => setHitoDesc(e.target.value)}
              placeholder="Descripcion del hito..."
            />
          </div>
          {hitoError && <p className="text-sm text-red-600">{hitoError}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={hitoSubmitting}>
              {hitoSubmitting ? "Guardando..." : "Crear Hito"}
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowHitoForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>

      {/* Inline creation drawers */}
      <IprCompromisoDrawer
        open={showCompromisoDrawer}
        onClose={() => setShowCompromisoDrawer(false)}
        iprId={id}
        onCreated={() => loadCompromisos(true)}
      />
      <IprProblemaDrawer
        open={showProblemaDrawer}
        onClose={() => setShowProblemaDrawer(false)}
        iprId={id}
        onCreated={() => loadProblemas(true)}
      />
      <IprConvenioDrawer
        open={showConvenioDrawer}
        onClose={() => setShowConvenioDrawer(false)}
        iprId={id}
        onCreated={() => loadConvenios(true)}
      />
    </div>
  );
}
