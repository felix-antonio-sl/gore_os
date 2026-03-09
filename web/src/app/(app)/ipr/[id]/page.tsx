"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { StatusBadge } from "@/components/status-badge";
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
import { ArrowLeft, UserPlus, Pencil, CheckCircle2, ShieldCheck, ShieldX, ChevronRight, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { IprTransition, TrackInfo } from "@/types";
import { WRITE_OPERATIONAL_ROLES } from "@/types";
import { formatDate, formatCurrency } from "@/lib/format";
import { TrackCard } from "../components/track-card";
import { TabCompromisos } from "../components/tab-compromisos";
import { TabProblemas } from "../components/tab-problemas";
import { TabAlertas } from "../components/tab-alertas";
import { TabConvenios } from "../components/tab-convenios";
import { TabCdps } from "../components/tab-cdps";
import { TabAvances } from "../components/tab-avances";
import { TabPartes } from "../components/tab-partes";
import { TabTerritorio } from "../components/tab-territorio";
import { TabHitos } from "../components/tab-hitos";
import { TabResoluciones } from "../components/tab-resoluciones";
import { TabEvaluaciones } from "../components/tab-evaluaciones";
import { TabParentesco } from "../components/tab-parentesco";
import { TabAdmisibilidad } from "../components/tab-admisibilidad";

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

export default function IprDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const id = params.id as string;

  const [ipr, setIpr] = useState<IprDetail | null>(null);
  const [iprLoading, setIprLoading] = useState(true);

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

  // Transitions state
  const [transitions, setTransitions] = useState<IprTransition[] | null>(null);
  const [transLoading, setTransLoading] = useState(false);
  const [selectedTransition, setSelectedTransition] = useState("");
  const [transSubmitting, setTransSubmitting] = useState(false);
  const [transError, setTransError] = useState<string | null>(null);

  // Track info state (Poly-Switch)
  const [trackInfo, setTrackInfo] = useState<TrackInfo | null>(null);

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
    api
      .get<TrackInfo>(`/api/ipr/${id}/track-info`)
      .then(setTrackInfo)
      .catch(() => setTrackInfo(null));
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

      {/* Track Card (Poly-Switch) */}
      {trackInfo && trackInfo.mechanism && (
        <TrackCard track={trackInfo} />
      )}

      {/* Tabs */}
      <Tabs defaultValue="compromisos">
        <TabsList className="flex-wrap">
          <TabsTrigger value="compromisos">Compromisos</TabsTrigger>
          <TabsTrigger value="problemas">Problemas</TabsTrigger>
          <TabsTrigger value="alertas">Alertas</TabsTrigger>
          <TabsTrigger value="convenios">Convenios</TabsTrigger>
          <TabsTrigger value="cdps">CDPs</TabsTrigger>
          <TabsTrigger value="avances">Avances</TabsTrigger>
          <TabsTrigger value="partes">Partes</TabsTrigger>
          <TabsTrigger value="territorio">Territorio</TabsTrigger>
          <TabsTrigger value="hitos">Hitos</TabsTrigger>
          <TabsTrigger value="resoluciones">Resoluciones</TabsTrigger>
          <TabsTrigger value="evaluaciones">Evaluación</TabsTrigger>
          <TabsTrigger value="parentesco">Parentesco</TabsTrigger>
          <TabsTrigger value="admisibilidad">Admisibilidad</TabsTrigger>
        </TabsList>

        <TabsContent value="compromisos" className="mt-4">
          <TabCompromisos iprId={id} canCreate={!!canCreateCompromiso} />
        </TabsContent>

        <TabsContent value="problemas" className="mt-4">
          <TabProblemas iprId={id} canCreate={!!canCreateProblema} />
        </TabsContent>

        <TabsContent value="alertas" className="mt-4">
          <TabAlertas iprId={id} />
        </TabsContent>

        <TabsContent value="convenios" className="mt-4">
          <TabConvenios iprId={id} canCreate={!!canCreateConvenio} />
        </TabsContent>

        <TabsContent value="cdps" className="mt-4">
          <TabCdps iprId={id} />
        </TabsContent>

        <TabsContent value="avances" className="mt-4">
          <TabAvances iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="partes" className="mt-4">
          <TabPartes iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="territorio" className="mt-4">
          <TabTerritorio iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="hitos" className="mt-4">
          <TabHitos iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="resoluciones" className="mt-4">
          <TabResoluciones iprId={id} />
        </TabsContent>

        <TabsContent value="evaluaciones" className="mt-4">
          <TabEvaluaciones iprId={id} canManage={!!canManageChildren} mechanismCode={ipr?.mechanism} />
        </TabsContent>

        <TabsContent value="parentesco" className="mt-4">
          <TabParentesco iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="admisibilidad" className="mt-4">
          <TabAdmisibilidad iprId={id} canManage={!!canManageChildren} />
        </TabsContent>
      </Tabs>

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
