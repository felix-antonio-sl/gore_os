"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { TimelineHistory } from "@/components/timeline-history";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ComboboxAsync, type ComboboxOption } from "@/components/combobox-async";
import { Plus, Download, UserCheck } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import { formatDate } from "@/lib/format";
import type { PaginatedResponse, CompromisoListItem, HistoryEntry } from "@/types";

const CSV_COLUMNS = [
  { key: "code", label: "Código" },
  { key: "description", label: "Descripción" },
  { key: "responsible_name", label: "Responsable" },
  { key: "state", label: "Estado" },
  { key: "due_date", label: "Fecha Límite" },
  { key: "days_remaining", label: "Días Restantes" },
];

const ESTADO_OPTIONS = [
  { value: "PENDIENTE", label: "Pendiente" },
  { value: "EN_PROGRESO", label: "En Progreso" },
  { value: "COMPLETADO", label: "Completado" },
  { value: "VERIFICADO", label: "Verificado" },
  { value: "VENCIDO", label: "Vencido" },
  { value: "CANCELADO", label: "Cancelado" },
];

const DIVISION_OPTIONS: { value: string; label: string }[] = [];

interface CompromisoDetail extends CompromisoListItem {
  observations?: string | null;
  history?: HistoryEntry[];
  notes?: string;
}

export default function CompromisosPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<CompromisoListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CompromisoDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [editObs, setEditObs] = useState("");
  const [obsEditing, setObsEditing] = useState(false);
  const [obsSaving, setObsSaving] = useState(false);
  const [reassigning, setReassigning] = useState(false);
  const [reassignUser, setReassignUser] = useState("");
  const [reassignLoading, setReassignLoading] = useState(false);

  const page = Number(searchParams.get("page") ?? "1");
  const estado = searchParams.get("estado") ?? "";
  const division = searchParams.get("division") ?? "";
  const soloMios = searchParams.get("solo_mios") === "1";
  const overdue = searchParams.get("overdue") === "true";
  const dateFrom = searchParams.get("date_from") ?? "";
  const dateTo = searchParams.get("date_to") ?? "";

  const filterValues: Record<string, string> = {
    estado,
    division,
  };

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) {
          params.delete(k);
        } else {
          params.set(k, String(v));
        }
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  const handleFilterChange = (key: string, value: string) => {
    router.push(buildUrl({ [key]: value, page: 1 }));
  };

  const handleClear = () => {
    router.push(pathname);
  };

  const handlePageChange = (newPage: number) => {
    router.push(buildUrl({ page: newPage }));
  };

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (estado) params.set("state", estado);
    if (division) params.set("division_id", division);
    if (soloMios && user?.id) params.set("responsible_id", user.id);
    if (overdue) params.set("overdue", "true");
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);

    api
      .get<PaginatedResponse<CompromisoListItem>>(`/api/compromisos?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, estado, division, soloMios, overdue, dateFrom, dateTo, user?.id, refreshKey]);

  const openDetail = (row: unknown) => {
    const compromiso = row as CompromisoListItem;
    setSelectedId(compromiso.id);
    setDetail(null);
    setDetailLoading(true);

    api.get<CompromisoDetail>(`/api/compromisos/${compromiso.id}`)
      .then((det) => {
        setDetail(det);
        setEditObs(det.observations ?? "");
        setObsEditing(false);
      })
      .catch(() => {
        setDetail(compromiso as CompromisoDetail);
      })
      .finally(() => setDetailLoading(false));
  };

  const handleAction = async (action: "completar" | "verificar" | "devolver") => {
    if (!selectedId) return;
    setActionLoading(true);
    try {
      await api.post(`/api/compromisos/${selectedId}/${action}`, {});
      setSelectedId(null);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      console.error("Error al actualizar estado:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const searchUsers = async (query: string): Promise<ComboboxOption[]> => {
    const users = await api.get<{ id: string; nombre: string; apellido_paterno: string; division_name: string | null }[]>(
      `/api/catalogs/users?search=${encodeURIComponent(query)}`
    );
    return users.map((u) => ({
      value: u.id,
      label: `${u.nombre} ${u.apellido_paterno}${u.division_name ? ` (${u.division_name})` : ""}`,
    }));
  };

  const handleReassign = async () => {
    if (!selectedId || !reassignUser) return;
    setReassignLoading(true);
    try {
      await api.patch(`/api/compromisos/${selectedId}`, { responsible_id: reassignUser });
      setReassigning(false);
      setReassignUser("");
      setSelectedId(null);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      console.error("Error al reasignar:", err);
    } finally {
      setReassignLoading(false);
    }
  };

  const saveObservations = async () => {
    if (!selectedId) return;
    setObsSaving(true);
    try {
      await api.patch(`/api/compromisos/${selectedId}`, { observations: editObs });
      setDetail((prev) => prev ? { ...prev, observations: editObs } : prev);
      setObsEditing(false);
    } catch (err) {
      console.error("Error al guardar observaciones:", err);
    } finally {
      setObsSaving(false);
    }
  };

  const canComplete =
    detail &&
    detail.state === "PENDIENTE" &&
    user &&
    (user.role_code === "ENCARGADO" || detail.responsible_id === user.id);

  const canVerify =
    detail &&
    detail.state === "COMPLETADO" &&
    user &&
    ["JEFE_DIVISION", "ADMIN_REGIONAL", "ADMIN_SISTEMA"].includes(user.role_code);

  const canReturn =
    detail &&
    (detail.state === "COMPLETADO" || detail.state === "EN_PROGRESO") &&
    user &&
    ["JEFE_DIVISION", "ADMIN_REGIONAL", "ADMIN_SISTEMA"].includes(user.role_code);

  const canReassign =
    detail &&
    detail.state !== "VERIFICADO" &&
    detail.state !== "CANCELADO" &&
    user &&
    ["JEFE_DIVISION", "ADMIN_REGIONAL", "ADMIN_SISTEMA", "GOBERNADOR", "JEFE_DEPARTAMENTO"].includes(user.role_code);

  const columns = [
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
    {
      key: "ipr_codigo_bip",
      label: "BIP",
      render: (v: unknown) => (
        <span className="text-xs font-mono text-muted-foreground">{String(v ?? "-")}</span>
      ),
    },
    { key: "responsible_name", label: "Responsable" },
    {
      key: "due_date",
      label: "Vence",
      render: (v: unknown) => (
        <span className="text-xs">{v ? formatDate(String(v)) : "-"}</span>
      ),
    },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  const canCreate =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Compromisos</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Gestión de compromisos operativos
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "compromisos")}>
            <Download className="size-4 mr-1" />CSV
          </Button>
          {canCreate && (
            <Button onClick={() => router.push("/compromisos/nuevo")} size="sm">
              <Plus className="size-4 mr-1" />
              Nuevo Compromiso
            </Button>
          )}
        </div>
      </div>

      <FilterBar
        filters={[
          { key: "estado", label: "Estado", options: ESTADO_OPTIONS },
          { key: "division", label: "División", options: DIVISION_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar compromiso..."
      />

      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground whitespace-nowrap">Vencimiento:</span>
        <Input type="date" className="h-8 w-36 text-xs" value={dateFrom} onChange={(e) => router.push(buildUrl({ date_from: e.target.value, page: 1 }))} />
        <span className="text-xs text-muted-foreground">—</span>
        <Input type="date" className="h-8 w-36 text-xs" value={dateTo} onChange={(e) => router.push(buildUrl({ date_to: e.target.value, page: 1 }))} />
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        page={page}
        totalPages={data?.total_pages ?? 1}
        total={data?.total ?? 0}
        onPageChange={handlePageChange}
        onRowClick={openDetail}
        isLoading={isLoading}
      />

      <DrawerPanel
        open={!!selectedId}
        onClose={() => setSelectedId(null)}
        title="Detalle de Compromiso"
      >
        {detailLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
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
                      onClick={() => { setSelectedId(null); router.push(`/ipr/${detail.ipr_id}`); }}
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
                    <UserCheck className="size-4 mr-1" />Reasignar
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
                      <Button size="sm" onClick={handleReassign} disabled={!reassignUser || reassignLoading}>
                        {reassignLoading ? "Reasignando..." : "Confirmar"}
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => { setReassigning(false); setReassignUser(""); }}>
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
                {!obsEditing ? (
                  <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => setObsEditing(true)}>
                    Editar
                  </Button>
                ) : (
                  <div className="flex gap-1">
                    <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => { setObsEditing(false); setEditObs(detail.observations ?? ""); }}>
                      Cancelar
                    </Button>
                    <Button size="sm" className="h-6 text-xs" onClick={saveObservations} disabled={obsSaving}>
                      {obsSaving ? "Guardando..." : "Guardar"}
                    </Button>
                  </div>
                )}
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
                    disabled={actionLoading}
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
          <p className="text-muted-foreground text-sm">No se pudo cargar el detalle.</p>
        )}
      </DrawerPanel>
    </div>
  );
}
