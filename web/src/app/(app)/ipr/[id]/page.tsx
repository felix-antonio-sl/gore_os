"use client";

import { useEffect, useState, Suspense, Fragment } from "react";
import { useParams, useRouter, usePathname } from "next/navigation";
import { useTabParam } from "@/hooks/use-tab-param";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DrawerPanel } from "@/components/drawer-panel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowLeft } from "lucide-react";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";
import type { IprTransition, TrackInfo, HistoryEntry } from "@/types";
import { WRITE_OPERATIONAL_ROLES, TRANSITION_ROLES } from "@/types";
import { TrackCard } from "../components/track-card";
import { IprHeroCard } from "../components/ipr-hero-card";
import { IprPhaseStepper } from "../components/ipr-phase-stepper";
import { IprTransitionPanel } from "../components/ipr-transition-panel";
import { IprHistorySection } from "../components/ipr-history-section";
import type { IprDetail } from "../components/ipr-constants";
import { TAB_GROUPS, TAB_LABELS, STATUS_TO_PHASE, MCD_PHASES } from "../components/ipr-constants";
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
import { TabModificaciones } from "../components/tab-modificaciones";
import { TabCierre } from "../components/tab-cierre";
import { TabEvaluacionExpost } from "../components/tab-evaluacion-expost";

interface UserOption {
  id: string;
  nombre: string;
  apellido_paterno: string;
  division_name: string | null;
}

function IprDetailPageInner() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
  const id = params.id as string;
  const [activeTab, setActiveTab] = useTabParam("tab", "compromisos");

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

  // Transition history (H20)
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  // Refresh key — increment to remount tab components after drawer saves
  const [refreshKey, setRefreshKey] = useState(0);

  const canAssign = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "GOBERNADOR"].includes(user.role_code);
  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"].includes(user.role_code);
  const canTransition = user && TRANSITION_ROLES.includes(user.role_code);
  const canCreateCompromiso = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "ANALISTA", "ENCARGADO"].includes(user.role_code);
  const canCreateProblema = user && WRITE_OPERATIONAL_ROLES.includes(user.role_code);
  const canCreateConvenio = user && WRITE_OPERATIONAL_ROLES.includes(user.role_code);
  const canManageChildren = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "ANALISTA"].includes(user.role_code);

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
    api
      .get<HistoryEntry[]>(`/api/ipr/${id}/historial`)
      .then(setHistory)
      .catch(() => setHistory([]));
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
      const updated = await api.get<IprDetail>(`/api/ipr/${id}`);
      setIpr(updated);
      setTransitions(null);
      setSelectedTransition("");
      loadTransitions();
      api.get<HistoryEntry[]>(`/api/ipr/${id}/historial`).then(setHistory).catch(() => setHistory([]));
      setRefreshKey((k) => k + 1);
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
      setRefreshKey((k) => k + 1);
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
      setRefreshKey((k) => k + 1);
    } catch (err) {
      setAssigneeError(err instanceof Error ? err.message : "Error al asignar responsable");
    } finally {
      setAssigneeSubmitting(false);
    }
  };

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
      <Breadcrumb items={buildBreadcrumbs(pathname, ipr?.codigo_bip)} />
      <Button variant="ghost" size="sm" onClick={() => router.back()}>
        <ArrowLeft className="size-4 mr-2" />
        Volver a IPR
      </Button>

      <IprHeroCard
        ipr={ipr}
        canEdit={!!canEdit}
        canAssign={!!canAssign}
        onEdit={openEditDrawer}
        onAssign={openAssigneeDrawer}
      />

      {(ipr.status || ipr.mcd_phase) && (
        <IprPhaseStepper
          currentPhase={ipr.status ? (STATUS_TO_PHASE[ipr.status] ?? ipr.mcd_phase ?? "F0") : (ipr.mcd_phase ?? "F0")}
          currentPhaseLabel={MCD_PHASES.find(p => p.code === (ipr.status ? STATUS_TO_PHASE[ipr.status] : ipr.mcd_phase))?.label}
          phaseEnteredAt={ipr.phase_entered_at}
        />
      )}

      {history.length > 0 && <IprHistorySection history={history} />}

      {canTransition && (
        <IprTransitionPanel
          transitions={transitions ?? []}
          loading={transLoading}
          selectedTransition={selectedTransition}
          onSelectTransition={setSelectedTransition}
          submitting={transSubmitting}
          onTransition={handleTransition}
          error={transError}
          currentPhase={STATUS_TO_PHASE[ipr.status ?? ""] ?? ipr.mcd_phase}
        />
      )}

      {/* Track Card (Poly-Switch) */}
      {trackInfo && trackInfo.mechanism && (
        <TrackCard track={trackInfo} />
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="flex-wrap">
          {TAB_GROUPS.map((group, gi) => (
            <Fragment key={group.label}>
              {gi > 0 && <div className="w-px h-5 bg-muted-foreground/30 mx-1.5 shrink-0 self-center" />}
              {group.tabs.map((tab) => (
                <TabsTrigger key={tab} value={tab}>
                  {TAB_LABELS[tab] ?? tab}
                </TabsTrigger>
              ))}
            </Fragment>
          ))}
        </TabsList>

        <TabsContent value="compromisos" className="mt-4">
          <TabCompromisos key={refreshKey} iprId={id} canCreate={!!canCreateCompromiso} />
        </TabsContent>

        <TabsContent value="problemas" className="mt-4">
          <TabProblemas key={refreshKey} iprId={id} canCreate={!!canCreateProblema} />
        </TabsContent>

        <TabsContent value="alertas" className="mt-4">
          <TabAlertas key={refreshKey} iprId={id} />
        </TabsContent>

        <TabsContent value="convenios" className="mt-4">
          <TabConvenios key={refreshKey} iprId={id} canCreate={!!canCreateConvenio} />
        </TabsContent>

        <TabsContent value="cdps" className="mt-4">
          <TabCdps key={refreshKey} iprId={id} />
        </TabsContent>

        <TabsContent value="avances" className="mt-4">
          <TabAvances key={refreshKey} iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="partes" className="mt-4">
          <TabPartes key={refreshKey} iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="territorio" className="mt-4">
          <TabTerritorio key={refreshKey} iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="hitos" className="mt-4">
          <TabHitos key={refreshKey} iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="resoluciones" className="mt-4">
          <TabResoluciones key={refreshKey} iprId={id} />
        </TabsContent>

        <TabsContent value="evaluaciones" className="mt-4">
          <TabEvaluaciones key={refreshKey} iprId={id} canManage={!!canManageChildren} mechanismCode={ipr?.mechanism} />
        </TabsContent>

        <TabsContent value="parentesco" className="mt-4">
          <TabParentesco key={refreshKey} iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="admisibilidad" className="mt-4">
          <TabAdmisibilidad key={refreshKey} iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="modificaciones" className="mt-4">
          <TabModificaciones key={refreshKey} iprId={id} canManage={!!canManageChildren} />
        </TabsContent>

        <TabsContent value="cierre" className="mt-4">
          <TabCierre key={refreshKey} iprId={id} canManage={!!canManageChildren} iprStatus={ipr?.status} />
        </TabsContent>

        <TabsContent value="evaluacion-expost" className="mt-4">
          <TabEvaluacionExpost key={refreshKey} iprId={id} canManage={!!canManageChildren} />
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

export default function IprDetailPage() {
  return (
    <Suspense>
      <IprDetailPageInner />
    </Suspense>
  );
}
