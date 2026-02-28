"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/lib/auth";
import { Download, Plus } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import { formatDate, formatCLP } from "@/lib/format";
import type {
  PaginatedResponse,
  ActoListItem,
  ActoDetail,
  ActoTransition,
} from "@/types";

const CSV_COLUMNS = [
  { key: "act_number", label: "N° Acto" },
  { key: "act_type_label", label: "Tipo" },
  { key: "subject", label: "Materia" },
  { key: "state_label", label: "Estado" },
  { key: "issuer_name", label: "Emisor" },
  { key: "issued_at", label: "Fecha" },
  { key: "resolution_type_label", label: "Tipo Resolución" },
];

const STATE_OPTIONS = [
  { value: "BORRADOR", label: "Borrador" },
  { value: "EN_REVISION", label: "En Revisión" },
  { value: "VISADO", label: "Visado" },
  { value: "FIRMADO", label: "Firmado" },
  { value: "TRAMITADO", label: "Tramitado" },
  { value: "TOMADO_RAZON", label: "Toma de Razón" },
  { value: "RECHAZADO_CGR", label: "Rechazado CGR" },
  { value: "ANULADO", label: "Anulado" },
];

const TYPE_OPTIONS = [
  { value: "RESOLUCION", label: "Resolución" },
  { value: "DECRETO", label: "Decreto" },
  { value: "OFICIO", label: "Oficio" },
  { value: "CERTIFICADO", label: "Certificado" },
  { value: "INFORME", label: "Informe" },
];

const STATE_STEP_ORDER = [
  "BORRADOR",
  "EN_REVISION",
  "VISADO",
  "FIRMADO",
  "TRAMITADO",
  "TOMADO_RAZON",
];

const STATE_STEP_COLORS: Record<string, string> = {
  BORRADOR: "bg-gray-300",
  EN_REVISION: "bg-amber-400",
  VISADO: "bg-blue-400",
  FIRMADO: "bg-green-500",
  TRAMITADO: "bg-green-600",
  TOMADO_RAZON: "bg-emerald-700",
  RECHAZADO_CGR: "bg-red-500",
  ANULADO: "bg-gray-500",
};

function StateStepper({ currentState }: { currentState: string }) {
  const isTerminalBad = currentState === "RECHAZADO_CGR" || currentState === "ANULADO";
  const stepIndex = STATE_STEP_ORDER.indexOf(currentState);

  return (
    <div className="flex items-center gap-1">
      {STATE_STEP_ORDER.map((step, i) => {
        const isActive = step === currentState;
        const isPast = stepIndex >= 0 && i < stepIndex;
        let color = "bg-muted";
        if (isActive) color = STATE_STEP_COLORS[step] ?? "bg-gray-400";
        else if (isPast) color = "bg-green-200";

        return (
          <div key={step} className="flex items-center gap-1">
            <div
              className={`h-2 w-8 rounded-full ${color}`}
              title={STATE_OPTIONS.find((s) => s.value === step)?.label ?? step}
            />
          </div>
        );
      })}
      {isTerminalBad && (
        <div
          className={`h-2 w-8 rounded-full ${STATE_STEP_COLORS[currentState]}`}
          title={STATE_OPTIONS.find((s) => s.value === currentState)?.label ?? currentState}
        />
      )}
    </div>
  );
}

export default function ActosPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<ActoListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ActoDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Edit state
  const [isEditing, setIsEditing] = useState(false);
  const [editStateId, setEditStateId] = useState("");
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [validTransitions, setValidTransitions] = useState<ActoTransition[]>([]);

  const canEdit =
    user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);
  const canCreate = canEdit;

  const page = Number(searchParams.get("page") ?? "1");
  const state = searchParams.get("state") ?? "";
  const act_type = searchParams.get("act_type") ?? "";

  const filterValues: Record<string, string> = { state, act_type };

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) params.delete(k);
        else params.set(k, String(v));
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  const handleFilterChange = (key: string, value: string) => {
    router.push(buildUrl({ [key]: value, page: 1 }));
  };

  const handleClear = () => router.push(pathname);
  const handlePageChange = (newPage: number) =>
    router.push(buildUrl({ page: newPage }));

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (state) params.set("state", state);
    if (act_type) params.set("act_type", act_type);

    setIsLoading(true);
    api
      .get<PaginatedResponse<ActoListItem>>(
        `/api/actos?${params.toString()}`
      )
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, state, act_type]);

  const openDetail = (row: unknown) => {
    const item = row as ActoListItem;
    setSelectedId(item.id);
    setDetail(null);
    setIsEditing(false);
    setEditError(null);
    setDetailLoading(true);
    api
      .get<ActoDetail>(`/api/actos/${item.id}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false));
  };

  const openEdit = () => {
    if (!detail || !selectedId) return;
    setEditStateId("");
    setEditError(null);
    setValidTransitions([]);
    setIsEditing(true);
    api
      .get<ActoTransition[]>(`/api/actos/${selectedId}/transiciones`)
      .then(setValidTransitions)
      .catch(() => setValidTransitions([]));
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId) return;
    setEditSubmitting(true);
    setEditError(null);
    const body: Record<string, unknown> = {};
    if (editStateId) body.state_id = editStateId;
    try {
      await api.patch(`/api/actos/${selectedId}`, body);
      setIsEditing(false);
      setDetailLoading(true);
      api
        .get<ActoDetail>(`/api/actos/${selectedId}`)
        .then(setDetail)
        .catch(() => {})
        .finally(() => setDetailLoading(false));
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEditSubmitting(false);
    }
  };

  const columns = [
    {
      key: "act_number",
      label: "N° Acto",
      render: (v: unknown) => (
        <span className="font-mono text-xs">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "act_type_label",
      label: "Tipo",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">
          {String(v ?? "-")}
        </Badge>
      ),
    },
    {
      key: "subject",
      label: "Materia",
      render: (v: unknown) => (
        <span className="text-sm line-clamp-1 max-w-[260px]">
          {String(v ?? "-")}
        </span>
      ),
    },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
    {
      key: "issuer_name",
      label: "Emisor",
      render: (v: unknown) => (
        <span className="text-xs line-clamp-1 max-w-[140px]">
          {String(v ?? "-")}
        </span>
      ),
    },
    {
      key: "issued_at",
      label: "Fecha",
      render: (v: unknown) => (
        <span className="text-xs">{formatDate(String(v))}</span>
      ),
    },
    {
      key: "requires_cgr",
      label: "CGR",
      render: (v: unknown) =>
        v ? (
          <Badge variant="outline" className="text-xs text-blue-600 border-blue-300">
            CGR
          </Badge>
        ) : null,
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Actos Administrativos</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Resoluciones, decretos, oficios y otros actos institucionales
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              exportCSV(CSV_COLUMNS, data?.items ?? [], "actos")
            }
          >
            <Download className="size-4 mr-1" />
            CSV
          </Button>
          {canCreate && (
            <Button size="sm" onClick={() => router.push("/actos/nuevo")}>
              <Plus className="size-4 mr-1" />
              Nuevo Acto
            </Button>
          )}
        </div>
      </div>

      <FilterBar
        filters={[
          { key: "state", label: "Estado", options: STATE_OPTIONS },
          { key: "act_type", label: "Tipo", options: TYPE_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar por número o materia..."
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
        title="Detalle de Acto Administrativo"
      >
        {detailLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-8 rounded bg-muted animate-pulse" />
            ))}
          </div>
        ) : detail ? (
          <div className="space-y-5">
            {/* Header */}
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-mono text-xs text-muted-foreground">
                  {detail.act_number}
                </span>
                <Badge variant="outline" className="text-xs">
                  {detail.act_type_label}
                </Badge>
                <StatusBadge status={detail.state} size="sm" />
              </div>
              <p className="text-sm mt-2">{detail.subject}</p>
            </div>

            {/* State stepper */}
            <div>
              <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide mb-2">
                Progreso
              </p>
              <StateStepper currentState={detail.state} />
            </div>

            {/* Edit button + form */}
            {canEdit && !isEditing && (
              <Button
                size="sm"
                variant="outline"
                onClick={openEdit}
                className="w-full"
              >
                Cambiar Estado
              </Button>
            )}
            {isEditing && (
              <form onSubmit={handleEditSubmit} className="space-y-3">
                <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">
                  Transición de Estado
                </p>
                <div className="space-y-1">
                  <label className="text-xs text-muted-foreground">
                    Nuevo estado
                  </label>
                  {validTransitions.length > 0 ? (
                    <Select value={editStateId} onValueChange={setEditStateId}>
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue placeholder="Seleccione nuevo estado" />
                      </SelectTrigger>
                      <SelectContent>
                        {validTransitions.map((t) => (
                          <SelectItem
                            key={t.id}
                            value={t.id}
                            className="text-xs"
                          >
                            {t.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <p className="text-xs text-muted-foreground italic py-1">
                      (Estado terminal — sin transiciones disponibles)
                    </p>
                  )}
                </div>
                {editError && (
                  <p className="text-xs text-red-600">{editError}</p>
                )}
                <div className="flex gap-2 pt-1">
                  <Button type="submit" size="sm" disabled={editSubmitting || !editStateId}>
                    {editSubmitting ? "Guardando..." : "Confirmar"}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => setIsEditing(false)}
                  >
                    Cancelar
                  </Button>
                </div>
              </form>
            )}

            {/* Details */}
            <div className="rounded-lg border divide-y text-sm">
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Emisor</span>
                <span>{detail.issuer_name ?? "-"}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Firmante</span>
                <span>{detail.signer_name ?? "-"}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Fecha emisión</span>
                <span>{formatDate(detail.issued_at)}</span>
              </div>
              {detail.effective_from && (
                <div className="flex justify-between px-3 py-2">
                  <span className="text-muted-foreground">Vigente desde</span>
                  <span>{formatDate(detail.effective_from)}</span>
                </div>
              )}
              {detail.effective_to && (
                <div className="flex justify-between px-3 py-2">
                  <span className="text-muted-foreground">Vigente hasta</span>
                  <span>{formatDate(detail.effective_to)}</span>
                </div>
              )}
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Creado</span>
                <span>{formatDate(detail.created_at)}</span>
              </div>
            </div>

            {/* Resolution section */}
            {detail.resolution_type && (
              <div className="space-y-2">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">
                  Resolución
                </p>
                <div className="rounded-lg border divide-y text-sm">
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Tipo</span>
                    <span>{detail.resolution_type_label}</span>
                  </div>
                  {detail.resolution_subtype_label && (
                    <div className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">Subtipo</span>
                      <span>{detail.resolution_subtype_label}</span>
                    </div>
                  )}
                  {detail.ipr_codigo_bip && (
                    <div className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">IPR</span>
                      <button
                        type="button"
                        className="font-mono text-xs text-blue-600 hover:underline cursor-pointer"
                        onClick={() => {
                          setSelectedId(null);
                          router.push(`/ipr/${detail.ipr_id}`);
                        }}
                      >
                        {detail.ipr_codigo_bip}
                      </button>
                    </div>
                  )}
                  {detail.agreement_number && (
                    <div className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">Convenio</span>
                      <span className="font-mono text-xs">
                        {detail.agreement_number}
                      </span>
                    </div>
                  )}
                  {detail.budget_amount !== null && detail.budget_amount !== undefined && (
                    <div className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">Monto</span>
                      <span className="font-mono">
                        {formatCLP(detail.budget_amount)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* CGR section */}
            {detail.requires_cgr && (
              <div className="space-y-2">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">
                  Contraloría (CGR)
                </p>
                <div className="rounded-lg border divide-y text-sm">
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Requiere CGR</span>
                    <Badge
                      variant="outline"
                      className="text-xs text-blue-600 border-blue-300"
                    >
                      Sí
                    </Badge>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Enviado</span>
                    <span>{formatDate(detail.cgr_submitted_at)}</span>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Resuelto</span>
                    <span>{formatDate(detail.cgr_resolved_at)}</span>
                  </div>
                  {detail.cgr_outcome_label && (
                    <div className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">Resultado</span>
                      <Badge variant="outline">{detail.cgr_outcome_label}</Badge>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">
            No se pudo cargar el detalle.
          </p>
        )}
      </DrawerPanel>
    </div>
  );
}
