"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Download } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import type { PaginatedResponse, ProblemaListItem, CategoryRef } from "@/types";

const CSV_COLUMNS = [
  { key: "code", label: "Código" },
  { key: "ipr_codigo_bip", label: "IPR" },
  { key: "problem_type_label", label: "Tipo" },
  { key: "impact_label", label: "Impacto" },
  { key: "state", label: "Estado" },
  { key: "detected_at", label: "Detectado" },
];

interface ProblemaDetail extends ProblemaListItem {
  impact_description: string | null;
  proposed_solution: string | null;
  solution_applied: string | null;
  detected_by_name: string | null;
  resolved_by_name: string | null;
  resolved_at: string | null;
  created_at: string;
}

const ESTADO_OPTIONS = [
  { value: "ABIERTO", label: "Abierto" },
  { value: "EN_GESTION", label: "En Gestión" },
  { value: "RESUELTO", label: "Resuelto" },
  { value: "CERRADO_SIN_RESOLVER", label: "Cerrado sin Resolver" },
];

const TIPO_OPTIONS = [
  { value: "TECNICO", label: "Técnico" },
  { value: "FINANCIERO", label: "Financiero" },
  { value: "LEGAL", label: "Legal" },
  { value: "ADMINISTRATIVO", label: "Administrativo" },
  { value: "AMBIENTAL", label: "Ambiental" },
  { value: "SOCIAL", label: "Social" },
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

export default function ProblemasPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<ProblemaListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ProblemaDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const [solutionApplied, setSolutionApplied] = useState("");
  const [closeReason, setCloseReason] = useState("");

  // Cache problem_state category IDs for state transitions
  const [problemStates, setProblemStates] = useState<CategoryRef[]>([]);

  const page = Number(searchParams.get("page") ?? "1");
  const estado = searchParams.get("estado") ?? "";
  const tipo = searchParams.get("tipo") ?? "";
  const search = searchParams.get("search") ?? "";

  const filterValues: Record<string, string> = {
    estado,
    tipo,
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

  const handleSearchChange = (value: string) => {
    router.push(buildUrl({ search: value, page: 1 }));
  };

  const handleClear = () => {
    router.push(pathname);
  };

  const handlePageChange = (newPage: number) => {
    router.push(buildUrl({ page: newPage }));
  };

  useEffect(() => {
    api.get<CategoryRef[]>("/api/catalogs/categories/problem_state").then(setProblemStates).catch(() => {});
  }, []);

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (estado) params.set("state", estado);
    if (tipo) params.set("problem_type", tipo);
    if (search) params.set("search", search);

    api
      .get<PaginatedResponse<ProblemaListItem>>(`/api/problemas?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, estado, tipo, search, refreshKey]);

  const openDetail = (row: unknown) => {
    const problema = row as ProblemaListItem;
    setSelectedId(problema.id);
    setDetail(null);
    setDetailLoading(true);
    setSolutionApplied("");
    setCloseReason("");

    api
      .get<ProblemaDetail>(`/api/problemas/${problema.id}`)
      .then(setDetail)
      .catch(() => setDetail(problema as ProblemaDetail))
      .finally(() => setDetailLoading(false));
  };

  const getStateId = (code: string): string | null => {
    const state = problemStates.find((s) => s.code === code);
    return state?.id ?? null;
  };

  const handleResolve = async () => {
    if (!selectedId) return;
    const stateId = getStateId("RESUELTO");
    if (!stateId) return;

    setActionLoading(true);
    try {
      await api.patch(`/api/problemas/${selectedId}`, {
        state_id: stateId,
        solution_applied: solutionApplied || null,
      });
      setSelectedId(null);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      console.error("Error al resolver:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleClose = async () => {
    if (!selectedId) return;
    const stateId = getStateId("CERRADO_SIN_RESOLVER");
    if (!stateId) return;

    setActionLoading(true);
    try {
      await api.patch(`/api/problemas/${selectedId}`, {
        state_id: stateId,
        solution_applied: closeReason || null,
      });
      setSelectedId(null);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      console.error("Error al cerrar:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleEnGestion = async () => {
    if (!selectedId) return;
    const stateId = getStateId("EN_GESTION");
    if (!stateId) return;

    setActionLoading(true);
    try {
      await api.patch(`/api/problemas/${selectedId}`, {
        state_id: stateId,
      });
      setSelectedId(null);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      console.error("Error al cambiar estado:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const canResolve = detail && ["ABIERTO", "EN_GESTION"].includes(detail.state);
  const canClose = detail && ["ABIERTO", "EN_GESTION"].includes(detail.state);
  const canEnGestion = detail && detail.state === "ABIERTO";

  const columns = [
    {
      key: "days_open",
      label: "Días abierto",
      render: (v: unknown) => (
        <span className="text-xs tabular-nums text-muted-foreground">{String(v ?? 0)}d</span>
      ),
    },
    {
      key: "ipr_codigo_bip",
      label: "BIP",
      render: (v: unknown) => (
        <span className="text-xs font-mono text-muted-foreground">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "description",
      label: "Descripción",
      render: (v: unknown) => (
        <span className="font-medium line-clamp-1 max-w-xs">{String(v ?? "")}</span>
      ),
    },
    {
      key: "problem_type_label",
      label: "Tipo",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "-")}</Badge>
      ),
    },
    {
      key: "impact_label",
      label: "Impacto",
      render: (v: unknown) => {
        const val = String(v ?? "-");
        const colorMap: Record<string, string> = {
          ALTO: "border-red-500 text-red-600",
          MEDIO: "border-orange-500 text-orange-600",
          BAJO: "border-gray-400 text-gray-600",
        };
        return (
          <Badge variant="outline" className={`text-xs ${colorMap[val.toUpperCase()] ?? ""}`}>
            {val}
          </Badge>
        );
      },
    },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Problemas</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Registro de problemas e impedimentos en IPRs
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "problemas")}>
            <Download className="size-4 mr-1" />CSV
          </Button>
          <Button onClick={() => router.push("/problemas/nuevo")} size="sm">
            <Plus className="size-4 mr-1" />
            Nuevo Problema
          </Button>
        </div>
      </div>

      <FilterBar
        filters={[
          { key: "estado", label: "Estado", options: ESTADO_OPTIONS },
          { key: "tipo", label: "Tipo", options: TIPO_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar problema..."
        searchValue={search}
        onSearchChange={handleSearchChange}
      />

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
        title="Detalle de Problema"
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
                <span className="text-xs text-muted-foreground tabular-nums">
                  {detail.days_open}d abierto
                </span>
              </div>
              <p className="font-medium">{detail.description}</p>
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
              <div className="flex gap-2">
                <Badge variant="outline" className="text-xs">
                  {detail.problem_type_label}
                </Badge>
                {detail.impact_label && (
                  <Badge variant="outline" className="text-xs">
                    {detail.impact_label}
                  </Badge>
                )}
              </div>
              {detail.detected_by_name && (
                <p className="text-sm">
                  <span className="text-muted-foreground">Detectado por: </span>
                  {detail.detected_by_name}
                </p>
              )}
              <p className="text-sm">
                <span className="text-muted-foreground">Fecha detección: </span>
                {formatDate(detail.detected_at)}
              </p>
              {detail.impact_description && (
                <div className="pt-1">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Impacto</p>
                  <p className="text-sm">{detail.impact_description}</p>
                </div>
              )}
              {detail.proposed_solution && (
                <div className="pt-1">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Solución propuesta</p>
                  <p className="text-sm">{detail.proposed_solution}</p>
                </div>
              )}
              {detail.solution_applied && (
                <div className="pt-1">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Solución aplicada</p>
                  <p className="text-sm">{detail.solution_applied}</p>
                </div>
              )}
              {detail.resolved_by_name && (
                <p className="text-sm">
                  <span className="text-muted-foreground">Resuelto por: </span>
                  {detail.resolved_by_name}
                  {detail.resolved_at && ` el ${formatDate(detail.resolved_at)}`}
                </p>
              )}
            </div>

            {/* State timeline */}
            <div className="pt-2 border-t">
              <h3 className="text-sm font-semibold mb-2">Historial</h3>
              <div className="space-y-2">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                  <div className="text-xs">
                    <p className="font-medium">Detectado — ABIERTO</p>
                    <p className="text-muted-foreground">
                      {formatDate(detail.detected_at)}
                      {detail.detected_by_name && ` por ${detail.detected_by_name}`}
                    </p>
                  </div>
                </div>
                {detail.state !== "ABIERTO" && (
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                    <div className="text-xs">
                      <p className="font-medium">EN_GESTION</p>
                      <p className="text-muted-foreground">Pasado a gestión</p>
                    </div>
                  </div>
                )}
                {detail.resolved_by_name && (
                  <div className="flex items-start gap-2">
                    <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${detail.state === "RESUELTO" ? "bg-green-500" : "bg-red-500"}`} />
                    <div className="text-xs">
                      <p className="font-medium">{detail.state === "RESUELTO" ? "Resuelto" : "Cerrado sin resolver"}</p>
                      <p className="text-muted-foreground">
                        {detail.resolved_at && formatDate(detail.resolved_at)}
                        {` por ${detail.resolved_by_name}`}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            {(canResolve || canClose || canEnGestion) && (
              <div className="pt-2 border-t space-y-3">
                {canEnGestion && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleEnGestion}
                    disabled={actionLoading}
                  >
                    Pasar a En Gestión
                  </Button>
                )}

                {canResolve && (
                  <div className="space-y-2">
                    <textarea
                      className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      value={solutionApplied}
                      onChange={(e) => setSolutionApplied(e.target.value)}
                      placeholder="Describa la solución aplicada..."
                    />
                    <Button
                      size="sm"
                      className="bg-green-600 hover:bg-green-700"
                      onClick={handleResolve}
                      disabled={actionLoading}
                    >
                      Resolver
                    </Button>
                  </div>
                )}

                {canClose && (
                  <div className="space-y-2 pt-2 border-t">
                    <textarea
                      className="flex min-h-[40px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      value={closeReason}
                      onChange={(e) => setCloseReason(e.target.value)}
                      placeholder="Motivo de cierre..."
                    />
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-red-600 border-red-300 hover:bg-red-50"
                      onClick={handleClose}
                      disabled={actionLoading}
                    >
                      Cerrar sin Resolver
                    </Button>
                  </div>
                )}
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
