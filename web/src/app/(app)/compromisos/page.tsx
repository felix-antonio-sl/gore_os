"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DrawerPanel } from "@/components/drawer-panel";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { TimelineHistory } from "@/components/timeline-history";
import { Button } from "@/components/ui/button";
import { ComboboxAsync } from "@/components/combobox-async";
import { CompromisoCreateDrawer } from "@/components/compromiso-create-drawer";
import { searchUsers } from "@/lib/catalog-search";
import { toast } from "sonner";
import { Plus, UserCheck } from "lucide-react";
import { formatDate } from "@/lib/format";
import { PageHeader } from "@/components/page-header";
import { CompromisosWorkView } from "./compromisos-work-view";
import { CompromisosListView } from "./compromisos-list-view";
import type { CompromisoListItem, HistoryEntry } from "@/types";

interface CompromisoDetail extends CompromisoListItem {
  observations?: string | null;
  history?: HistoryEntry[];
  commitment_type_label?: string;
  verified_by_name?: string | null;
  created_at?: string;
}

type ViewMode = "work" | "list";

export default function CompromisosPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  // --- View mode ---
  const role = user?.role_code;
  const mine = searchParams.get("mine") === "true";
  const detailIdParam = searchParams.get("id");
  const isPersonalScope = role && ["ANALISTA", "RTF", "ASESOR_JURIDICO"].includes(role);
  const viewMode: ViewMode = mine || isPersonalScope ? "work" : "list";

  // --- Shared state ---
  const [refreshKey, setRefreshKey] = useState(0);
  const onRefresh = () => setRefreshKey((k) => k + 1);

  // --- Drawer state ---
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CompromisoDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [returnReason, setReturnReason] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [editObs, setEditObs] = useState("");
  const [obsEditing, setObsEditing] = useState(false);
  const [obsSaving, setObsSaving] = useState(false);
  const [reassigning, setReassigning] = useState(false);
  const [reassignUser, setReassignUser] = useState("");
  const [reassignLoading, setReassignLoading] = useState(false);

  const openDetailById = useCallback((id: string) => {
    setSelectedId(id);
    setDetail(null);
    setDetailError(null);
    setReturnReason("");
    setDetailLoading(true);
    setReassigning(false);
    setReassignUser("");
    api
      .get<CompromisoDetail>(`/api/compromisos/${id}`)
      .then((det) => {
        setDetail(det);
        setEditObs(det.observations ?? "");
        setObsEditing(false);
      })
      .catch((err) => setDetailError(err instanceof Error ? err.message : "No se pudo cargar el compromiso"))
      .finally(() => setDetailLoading(false));
  }, []);

  useEffect(() => {
    if (detailIdParam) openDetailById(detailIdParam);
  }, [detailIdParam, openDetailById]);

  const openDetail = (item: CompromisoListItem) => openDetailById(item.id);

  const closeDetail = () => {
    setSelectedId(null);
    if (detailIdParam) {
      const params = new URLSearchParams(searchParams.toString());
      params.delete("id");
      router.replace(`/compromisos${params.size ? `?${params}` : ""}`);
    }
  };

  const handleAction = async (action: "completar" | "verificar" | "devolver") => {
    if (!selectedId) return;
    if (action === "devolver" && !returnReason.trim()) {
      toast.error("Indica el motivo de devolución");
      return;
    }
    setActionLoading(true);
    try {
      await api.post(`/api/compromisos/${selectedId}/${action}`, action === "devolver" ? { observations: returnReason.trim() } : {});
      closeDetail();
      onRefresh();
      toast.success(action === "completar" ? "Compromiso completado, pendiente de verificación" : action === "verificar" ? "Compromiso verificado" : "Compromiso devuelto al responsable");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al actualizar estado");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReassign = async () => {
    if (!selectedId || !reassignUser) return;
    setReassignLoading(true);
    try {
      await api.patch(`/api/compromisos/${selectedId}`, { responsible_id: reassignUser });
      setReassigning(false);
      setReassignUser("");
      setSelectedId(null);
      onRefresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al reasignar");
    } finally {
      setReassignLoading(false);
    }
  };

  const saveObservations = async () => {
    if (!selectedId) return;
    setObsSaving(true);
    try {
      await api.patch(`/api/compromisos/${selectedId}`, { observations: editObs });
      setDetail((prev) => (prev ? { ...prev, observations: editObs } : prev));
      setObsEditing(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar observaciones");
    } finally {
      setObsSaving(false);
    }
  };

  // Assignment/role and canonical transitions are resolved by the backend.
  const actions = detail?.allowed_actions ?? [];
  const canComplete = actions.includes("completar");
  const canVerify = actions.includes("verificar");
  const canReturn = actions.includes("devolver");
  const canReassign = actions.includes("reasignar");
  const canEditObservations = actions.includes("editar_observaciones");
  const canCreate =
    user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);

  const [createOpen, setCreateOpen] = useState(false);

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Compromisos"
        description={
          viewMode === "work"
            ? "Mis compromisos operativos"
            : "Gestión de compromisos operativos"
        }
        accentColor="amber"
        actions={
          canCreate ? (
            <Button onClick={() => setCreateOpen(true)} size="sm">
              <Plus className="size-4 mr-1" />
              Nuevo Compromiso
            </Button>
          ) : undefined
        }
      />

      {viewMode === "work" && (
        <CompromisosWorkView
          onItemClick={openDetail}
          refreshKey={refreshKey}
          onRefresh={onRefresh}
          mine={mine}
        />
      )}
      {viewMode === "list" && (
        <CompromisosListView
          onItemClick={openDetail}
          refreshKey={refreshKey}
          onRefresh={onRefresh}
        />
      )}

      {/* Shared Detail Drawer */}
      <DrawerPanel
        open={!!selectedId}
        onClose={closeDetail}
        title="Detalle de Compromiso"
      >
        {detailLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-8 rounded bg-muted animate-pulse" />
            ))}
          </div>
        ) : detail ? (
          <div className="space-y-5">
            {/* Metadata */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <StatusBadge status={detail.state} />
                <TemporalIndicator daysRemaining={detail.days_remaining} state={detail.state} />
              </div>
              <p className="font-medium">{detail.description}</p>
              {detail.ipr_codigo_bip && (
                <p className="text-xs text-muted-foreground">
                  IPR:{" "}
                  {detail.ipr_id ? (
                    <button
                      type="button"
                      className="font-mono text-blue-600 hover:underline cursor-pointer"
                      onClick={() => {
                        setSelectedId(null);
                        router.push(`/ipr/${detail.ipr_id}`);
                      }}
                    >
                      {detail.ipr_codigo_bip}
                    </button>
                  ) : (
                    <span className="font-mono">{detail.ipr_codigo_bip}</span>
                  )}
                  {detail.ipr_name && ` — ${detail.ipr_name}`}
                </p>
              )}
              <p className="text-sm">
                <span className="text-muted-foreground">Responsable: </span>
                {detail.responsible_name ?? "-"}
              </p>
              <p className="text-sm">
                <span className="text-muted-foreground">División: </span>
                {detail.division_name ?? "-"}
              </p>
              <p className="text-sm">
                <span className="text-muted-foreground">Vencimiento: </span>
                {detail.due_date ? formatDate(detail.due_date) : "-"}
              </p>
              {detail.completed_at && (
                <p className="text-sm">
                  <span className="text-muted-foreground">Completado: </span>
                  {formatDate(detail.completed_at)}
                </p>
              )}
              {detail.verified_at && (
                <p className="text-sm">
                  <span className="text-muted-foreground">Verificado: </span>
                  {formatDate(detail.verified_at)}
                </p>
              )}
            </div>

            {/* Reasignación */}
            {canReassign && (
              <div className="pt-2 border-t">
                {!reassigning ? (
                  <Button variant="outline" size="sm" onClick={() => setReassigning(true)}>
                    <UserCheck className="size-4 mr-1" />
                    Reasignar
                  </Button>
                ) : (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Reasignar a:</p>
                    <ComboboxAsync
                      value={reassignUser}
                      onChange={setReassignUser}
                      searchFn={searchUsers}
                      placeholder="Buscar usuario..."
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={handleReassign}
                        disabled={!reassignUser || reassignLoading}
                      >
                        {reassignLoading ? "Reasignando..." : "Confirmar"}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setReassigning(false);
                          setReassignUser("");
                        }}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Observaciones */}
            <div className="pt-2 border-t">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">Observaciones</h3>
                {!obsEditing && canEditObservations ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 text-xs"
                    onClick={() => setObsEditing(true)}
                  >
                    Editar
                  </Button>
                ) : obsEditing ? (
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 text-xs"
                      onClick={() => {
                        setObsEditing(false);
                        setEditObs(detail.observations ?? "");
                      }}
                    >
                      Cancelar
                    </Button>
                    <Button
                      size="sm"
                      className="h-6 text-xs"
                      onClick={saveObservations}
                      disabled={obsSaving}
                    >
                      {obsSaving ? "Guardando..." : "Guardar"}
                    </Button>
                  </div>
                ) : null}
              </div>
              {obsEditing ? (
                <textarea
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm min-h-[80px] resize-y focus:outline-none focus:ring-2 focus:ring-ring"
                  value={editObs}
                  onChange={(e) => setEditObs(e.target.value)}
                  placeholder="Agregar observaciones..."
                />
              ) : (
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {detail.observations || "Sin observaciones"}
                </p>
              )}
            </div>

            {/* Actions */}
            {canReturn && (
              <div className="flex flex-col gap-2">
                <label htmlFor="return-reason" className="text-sm font-medium">Motivo de devolución</label>
                <textarea id="return-reason" value={returnReason} onChange={(event) => setReturnReason(event.target.value)}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm" placeholder="Indica qué debe corregir el responsable" />
              </div>
            )}
            {(canComplete || canVerify || canReturn) && (
              <div className="flex gap-2 flex-wrap pt-2 border-t">
                {canComplete && (
                  <Button
                    size="sm"
                    onClick={() => handleAction("completar")}
                    disabled={actionLoading}
                  >
                    Completar
                  </Button>
                )}
                {canVerify && (
                  <Button
                    size="sm"
                    className="bg-green-600 hover:bg-green-700"
                    onClick={() => handleAction("verificar")}
                    disabled={actionLoading}
                  >
                    Verificar
                  </Button>
                )}
                {canReturn && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleAction("devolver")}
                    disabled={actionLoading || !returnReason.trim()}
                  >
                    Devolver
                  </Button>
                )}
              </div>
            )}

            {/* Timeline */}
            {detail.history && detail.history.length > 0 && (
              <div className="pt-2 border-t">
                <h3 className="text-sm font-semibold mb-3">Historial</h3>
                <TimelineHistory entries={detail.history} />
              </div>
            )}
          </div>
        ) : (
          <p role="alert" className="text-muted-foreground text-sm">{detailError ?? "No se pudo cargar el detalle."}</p>
        )}
      </DrawerPanel>

      <CompromisoCreateDrawer open={createOpen} onClose={() => setCreateOpen(false)} onCreated={onRefresh} />
    </div>
  );
}
