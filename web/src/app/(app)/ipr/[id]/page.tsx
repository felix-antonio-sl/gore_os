"use client";

import { useEffect, useState, Suspense } from "react";
import { useParams, useRouter } from "next/navigation";
import { useTabParam } from "@/hooks/use-tab-param";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DrawerPanel } from "@/components/drawer-panel";
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
import type { IprTransition, TrackInfo, HistoryEntry } from "@/types";
import { WRITE_OPERATIONAL_ROLES, TRANSITION_ROLES } from "@/types";
import { IprStickyHeader } from "../components/ipr-sticky-header";
import { IprSidebarNav } from "../components/ipr-sidebar-nav";
import { TabResumen } from "../components/tab-resumen";
import type { IprDetail } from "../components/ipr-constants";
import { TAB_LABELS } from "../components/ipr-constants";
import { TabCompromisos } from "../components/tab-compromisos";
import { TabProblemas } from "../components/tab-problemas";
import { TabAlertas } from "../components/tab-alertas";
import { TabConvenios } from "../components/tab-convenios";
import { TabCdps } from "../components/tab-cdps";
import { TabAvances } from "../components/tab-avances";
import { TabPartes } from "../components/tab-partes";
import { TabTerritorio } from "../components/tab-territorio";
import { TabHitos } from "../components/tab-hitos";
import { TabRendiciones } from "../components/tab-rendiciones";
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
  const { user } = useAuth();
  const id = params.id as string;
  const [activeTab, setActiveTab] = useTabParam("tab", "resumen");

  const [ipr, setIpr] = useState<IprDetail | null>(null);
  const [iprLoading, setIprLoading] = useState(true);

  const [showAssignee, setShowAssignee] = useState(false);
  const [usersList, setUsersList] = useState<UserOption[]>([]);
  const [selectedAssignee, setSelectedAssignee] = useState("");
  const [assigneeSubmitting, setAssigneeSubmitting] = useState(false);
  const [assigneeError, setAssigneeError] = useState<string | null>(null);

  const [showEdit, setShowEdit] = useState(false);
  const [editName, setEditName] = useState("");
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  const [transitions, setTransitions] = useState<IprTransition[] | null>(null);
  const [transLoading, setTransLoading] = useState(false);
  const [selectedTransition, setSelectedTransition] = useState("");
  const [transSubmitting, setTransSubmitting] = useState(false);
  const [transError, setTransError] = useState<string | null>(null);

  const [trackInfo, setTrackInfo] = useState<TrackInfo | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);

  const canAssign = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "GOBERNADOR"].includes(user.role_code);
  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"].includes(user.role_code);
  const canTransition = user && TRANSITION_ROLES.includes(user.role_code);
  const canCreateCompromiso = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "ANALISTA", "ENCARGADO"].includes(user.role_code);
  const canCreateProblema = user && WRITE_OPERATIONAL_ROLES.includes(user.role_code);
  const canCreateConvenio = user && WRITE_OPERATIONAL_ROLES.includes(user.role_code);
  const canManageChildren = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "ANALISTA"].includes(user.role_code);

  useEffect(() => {
    api.get<IprDetail>(`/api/ipr/${id}`).then(setIpr).catch(() => setIpr(null)).finally(() => setIprLoading(false));
    api.get<TrackInfo>(`/api/ipr/${id}/track-info`).then(setTrackInfo).catch(() => setTrackInfo(null));
    api.get<HistoryEntry[]>(`/api/ipr/${id}/historial`).then(setHistory).catch(() => setHistory([]));
  }, [id]);

  const loadTransitions = () => {
    if (!canTransition) return;
    setTransLoading(true);
    api.get<IprTransition[]>(`/api/ipr/${id}/transiciones`).then(setTransitions).catch(() => setTransitions(null)).finally(() => setTransLoading(false));
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

  const openEditDrawer = () => { setEditName(ipr?.name ?? ""); setEditError(null); setShowEdit(true); };
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editName.trim()) { setEditError("El nombre es requerido."); return; }
    setEditSubmitting(true); setEditError(null);
    try {
      await api.patch(`/api/ipr/${id}`, { name: editName.trim() });
      setShowEdit(false); setRefreshKey((k) => k + 1);
      api.get<IprDetail>(`/api/ipr/${id}`).then(setIpr).catch(() => {});
    } catch (err) { setEditError(err instanceof Error ? err.message : "Error al actualizar IPR"); }
    finally { setEditSubmitting(false); }
  };

  const openAssigneeDrawer = () => { setShowAssignee(true); setAssigneeError(null); setSelectedAssignee(""); api.get<UserOption[]>("/api/catalogs/users").then(setUsersList).catch(() => {}); };
  const handleAssigneeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAssignee) { setAssigneeError("Seleccione un usuario."); return; }
    setAssigneeSubmitting(true); setAssigneeError(null);
    try {
      await api.patch(`/api/ipr/${id}`, { assignee_id: selectedAssignee });
      setShowAssignee(false); setRefreshKey((k) => k + 1);
    } catch (err) { setAssigneeError(err instanceof Error ? err.message : "Error al asignar responsable"); }
    finally { setAssigneeSubmitting(false); }
  };

  if (iprLoading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-12 w-full rounded bg-muted animate-pulse" />
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (!ipr) {
    return (
      <div className="p-6">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="size-4 mr-2" /> Volver
        </Button>
        <p className="mt-4 text-muted-foreground">IPR no encontrado.</p>
      </div>
    );
  }

  const tabContent = (
    <>
      {activeTab === "resumen" && (
        <TabResumen
          ipr={ipr}
          transitions={transitions}
          transLoading={transLoading}
          trackInfo={trackInfo}
          history={history}
          canTransition={!!canTransition}
          selectedTransition={selectedTransition}
          onSelectTransition={setSelectedTransition}
          onTransition={handleTransition}
          transSubmitting={transSubmitting}
          transError={transError}
        />
      )}
      {activeTab === "compromisos" && <TabCompromisos key={refreshKey} iprId={id} canCreate={!!canCreateCompromiso} />}
      {activeTab === "problemas" && <TabProblemas key={refreshKey} iprId={id} canCreate={!!canCreateProblema} />}
      {activeTab === "alertas" && <TabAlertas key={refreshKey} iprId={id} />}
      {activeTab === "convenios" && <TabConvenios key={refreshKey} iprId={id} canCreate={!!canCreateConvenio} />}
      {activeTab === "rendiciones" && <TabRendiciones key={refreshKey} iprId={id} />}
      {activeTab === "cdps" && <TabCdps key={refreshKey} iprId={id} />}
      {activeTab === "avances" && <TabAvances key={refreshKey} iprId={id} canManage={!!canManageChildren} />}
      {activeTab === "partes" && <TabPartes key={refreshKey} iprId={id} canManage={!!canManageChildren} />}
      {activeTab === "territorio" && <TabTerritorio key={refreshKey} iprId={id} canManage={!!canManageChildren} />}
      {activeTab === "hitos" && <TabHitos key={refreshKey} iprId={id} canManage={!!canManageChildren} />}
      {activeTab === "resoluciones" && <TabResoluciones key={refreshKey} iprId={id} />}
      {activeTab === "evaluaciones" && <TabEvaluaciones key={refreshKey} iprId={id} canManage={!!canManageChildren} mechanismCode={ipr?.mechanism} />}
      {activeTab === "parentesco" && <TabParentesco key={refreshKey} iprId={id} canManage={!!canManageChildren} />}
      {activeTab === "admisibilidad" && <TabAdmisibilidad key={refreshKey} iprId={id} canManage={!!canManageChildren} />}
      {activeTab === "modificaciones" && <TabModificaciones key={refreshKey} iprId={id} canManage={!!canManageChildren} />}
      {activeTab === "cierre" && <TabCierre key={refreshKey} iprId={id} canManage={!!canManageChildren} iprStatus={ipr?.status} />}
      {activeTab === "evaluacion-expost" && <TabEvaluacionExpost key={refreshKey} iprId={id} canManage={!!canManageChildren} />}
    </>
  );

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)]">
      <IprStickyHeader
        ipr={ipr}
        canEdit={!!canEdit}
        canAssign={!!canAssign}
        onEdit={openEditDrawer}
        onAssign={openAssigneeDrawer}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar — hidden on mobile */}
        <aside className="hidden md:block w-52 border-r overflow-y-auto shrink-0 bg-background">
          <IprSidebarNav activeTab={activeTab} onTabChange={setActiveTab} />
        </aside>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* Mobile tab selector */}
          <div className="md:hidden mb-4">
            <Select value={activeTab} onValueChange={setActiveTab}>
              <SelectTrigger className="w-full">
                <SelectValue>{TAB_LABELS[activeTab] ?? activeTab}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="resumen">Resumen</SelectItem>
                <SelectItem value="compromisos">Compromisos</SelectItem>
                <SelectItem value="problemas">Problemas</SelectItem>
                <SelectItem value="hitos">Hitos</SelectItem>
                <SelectItem value="avances">Avances</SelectItem>
                <SelectItem value="alertas">Alertas</SelectItem>
                <SelectItem value="cdps">Presupuesto</SelectItem>
                <SelectItem value="convenios">Convenios</SelectItem>
                <SelectItem value="rendiciones">Rendiciones</SelectItem>
                <SelectItem value="resoluciones">Resoluciones</SelectItem>
                <SelectItem value="partes">Partes</SelectItem>
                <SelectItem value="territorio">Territorio</SelectItem>
                <SelectItem value="evaluaciones">Evaluación</SelectItem>
                <SelectItem value="parentesco">Parentesco</SelectItem>
                <SelectItem value="admisibilidad">Admisibilidad</SelectItem>
                <SelectItem value="modificaciones">Modificaciones</SelectItem>
                <SelectItem value="cierre">Cierre</SelectItem>
                <SelectItem value="evaluacion-expost">Eval. Posterior</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {tabContent}
        </main>
      </div>

      {/* Drawers */}
      <DrawerPanel open={showAssignee} onClose={() => setShowAssignee(false)} title="Asignar Responsable">
        <form onSubmit={handleAssigneeSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Responsable *</label>
            <Select value={selectedAssignee} onValueChange={setSelectedAssignee}>
              <SelectTrigger><SelectValue placeholder="Seleccione usuario" /></SelectTrigger>
              <SelectContent>
                {usersList.map((u) => (
                  <SelectItem key={u.id} value={u.id}>
                    {u.nombre} {u.apellido_paterno}{u.division_name ? ` (${u.division_name})` : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {assigneeError && <p className="text-sm text-red-600">{assigneeError}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={assigneeSubmitting}>{assigneeSubmitting ? "Asignando..." : "Asignar"}</Button>
            <Button type="button" variant="outline" onClick={() => setShowAssignee(false)}>Cancelar</Button>
          </div>
        </form>
      </DrawerPanel>

      <DrawerPanel open={showEdit} onClose={() => setShowEdit(false)} title="Editar IPR">
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Nombre *</label>
            <Input value={editName} onChange={(e) => setEditName(e.target.value)} placeholder="Nombre del IPR" />
          </div>
          {editError && <p className="text-sm text-red-600">{editError}</p>}
          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={editSubmitting}>{editSubmitting ? "Guardando..." : "Guardar"}</Button>
            <Button type="button" variant="outline" onClick={() => setShowEdit(false)}>Cancelar</Button>
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
