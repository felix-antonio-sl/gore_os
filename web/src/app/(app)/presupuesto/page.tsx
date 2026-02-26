"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import type { PaginatedResponse, PresupuestoListItem, PresupuestoDetail } from "@/types";

const CSV_COLUMNS = [
  { key: "division_name", label: "División" },
  { key: "name", label: "Programa" },
  { key: "initial_amount", label: "Presupuesto Inicial" },
  { key: "current_amount", label: "Presupuesto Vigente" },
  { key: "committed_amount", label: "Comprometido" },
  { key: "execution_pct", label: "% Ejecución" },
];

const SUBTITLE_OPTIONS = [
  { value: "21", label: "Subtítulo 21 — Personal" },
  { value: "22", label: "Subtítulo 22 — Bienes y Servicios" },
  { value: "24", label: "Subtítulo 24 — Transferencias Corrientes" },
  { value: "29", label: "Subtítulo 29 — Activos No Financieros" },
  { value: "31", label: "Subtítulo 31 — Iniciativas de Inversión" },
  { value: "33", label: "Subtítulo 33 — Transferencias de Capital" },
];

const YEAR_OPTIONS = [
  { value: "2026", label: "2026" },
  { value: "2025", label: "2025" },
  { value: "2024", label: "2024" },
];

function formatCLP(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

function formatDate(dateStr: string): string {
  try {
    return new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

function ExecutionBar({ pct }: { pct: number }) {
  const color = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-amber-500" : "bg-red-500";
  const textColor = pct >= 70 ? "text-green-700" : pct >= 40 ? "text-amber-700" : "text-red-700";
  return (
    <div className="flex items-center gap-2 min-w-[100px]">
      <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <span className={`text-xs font-mono font-medium tabular-nums ${textColor}`}>{pct}%</span>
    </div>
  );
}

export default function PresupuestoPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<PresupuestoListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<PresupuestoDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Edit state
  const [isEditing, setIsEditing] = useState(false);
  const [editInitial, setEditInitial] = useState("");
  const [editCurrent, setEditCurrent] = useState("");
  const [editCommitted, setEditCommitted] = useState("");
  const [editAccrued, setEditAccrued] = useState("");
  const [editPaid, setEditPaid] = useState("");
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);

  const page = Number(searchParams.get("page") ?? "1");
  const fiscal_year = searchParams.get("fiscal_year") ?? "";
  const subtitle = searchParams.get("subtitle") ?? "";
  const search = searchParams.get("search") ?? "";

  const filterValues: Record<string, string> = { fiscal_year, subtitle, search };

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
  const handlePageChange = (newPage: number) => router.push(buildUrl({ page: newPage }));

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (fiscal_year) params.set("fiscal_year", fiscal_year);
    if (subtitle) params.set("subtitle", subtitle);
    if (search) params.set("search", search);

    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsLoading(true);
    api
      .get<PaginatedResponse<PresupuestoListItem>>(`/api/presupuesto?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, fiscal_year, subtitle, search]);

  const openDetail = (row: unknown) => {
    const item = row as PresupuestoListItem;
    setSelectedId(item.id);
    setDetail(null);
    setIsEditing(false);
    setEditError(null);
    setDetailLoading(true);
    api
      .get<PresupuestoDetail>(`/api/presupuesto/${item.id}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false));
  };

  const openEdit = () => {
    if (!detail) return;
    setEditInitial(String(detail.initial_amount ?? ""));
    setEditCurrent(String(detail.current_amount ?? ""));
    setEditCommitted(String(detail.committed_amount ?? ""));
    setEditAccrued(String(detail.accrued_amount ?? ""));
    setEditPaid(String(detail.paid_amount ?? ""));
    setEditError(null);
    setIsEditing(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId) return;
    setEditSubmitting(true);
    setEditError(null);
    try {
      await api.patch(`/api/presupuesto/${selectedId}`, {
        initial_amount: editInitial ? parseFloat(editInitial) : undefined,
        current_amount: editCurrent ? parseFloat(editCurrent) : undefined,
        committed_amount: editCommitted ? parseFloat(editCommitted) : undefined,
        accrued_amount: editAccrued ? parseFloat(editAccrued) : undefined,
        paid_amount: editPaid ? parseFloat(editPaid) : undefined,
      });
      setIsEditing(false);
      // Refresh detail
      setDetailLoading(true);
      api
        .get<PresupuestoDetail>(`/api/presupuesto/${selectedId}`)
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
      key: "code",
      label: "Código",
      render: (v: unknown) => (
        <span className="font-mono text-xs text-muted-foreground">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "name",
      label: "Nombre",
      render: (v: unknown) => (
        <span className="font-medium line-clamp-1 max-w-xs">{String(v ?? "")}</span>
      ),
    },
    { key: "division_name", label: "División" },
    {
      key: "subtitle_label",
      label: "Subtítulo",
      render: (v: unknown) => (
        <span className="text-xs text-muted-foreground">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "initial_amount",
      label: "Monto inicial",
      render: (v: unknown) => (
        <span className="text-xs tabular-nums font-mono">{formatCLP(Number(v))}</span>
      ),
    },
    {
      key: "execution_pct",
      label: "Ejecución",
      render: (v: unknown) => <ExecutionBar pct={Number(v ?? 0)} />,
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Presupuesto</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Programas presupuestarios y ejecución financiera
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "presupuesto")}>
          <Download className="size-4 mr-1" />CSV
        </Button>
      </div>

      <FilterBar
        filters={[
          { key: "fiscal_year", label: "Año", options: YEAR_OPTIONS },
          { key: "subtitle", label: "Subtítulo", options: SUBTITLE_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar por código o nombre..."
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
        title="Detalle Presupuestario"
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
              <p className="font-mono text-xs text-muted-foreground">{detail.code}</p>
              <p className="font-semibold text-base mt-1">{detail.name}</p>
              <p className="text-sm text-muted-foreground mt-0.5">
                Año fiscal: {detail.fiscal_year}
                {detail.division_name && ` · ${detail.division_name}`}
              </p>
            </div>

            {/* Ejecución */}
            <div className="space-y-1">
              <div className="flex justify-between items-center mb-1">
                <p className="text-sm font-medium">Ejecución</p>
                <span className={`text-sm font-bold tabular-nums ${
                  detail.execution_pct >= 70 ? "text-green-700" :
                  detail.execution_pct >= 40 ? "text-amber-700" : "text-red-700"
                }`}>{detail.execution_pct}%</span>
              </div>
              <ExecutionBar pct={detail.execution_pct} />
            </div>

            {/* Montos — vista o edición */}
            {isEditing ? (
              <form onSubmit={handleEditSubmit} className="space-y-3">
                <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">Editar Montos (CLP)</p>
                {[
                  { label: "Monto inicial", value: editInitial, setter: setEditInitial },
                  { label: "Monto vigente", value: editCurrent, setter: setEditCurrent },
                  { label: "Comprometido", value: editCommitted, setter: setEditCommitted },
                  { label: "Devengado", value: editAccrued, setter: setEditAccrued },
                  { label: "Pagado", value: editPaid, setter: setEditPaid },
                ].map(({ label, value, setter }) => (
                  <div key={label} className="flex items-center gap-2">
                    <label className="text-xs text-muted-foreground w-28 shrink-0">{label}</label>
                    <Input
                      type="number"
                      min="0"
                      step="1"
                      value={value}
                      onChange={(e) => setter(e.target.value)}
                      className="h-7 text-xs"
                    />
                  </div>
                ))}
                {editError && <p className="text-xs text-red-600">{editError}</p>}
                <div className="flex gap-2 pt-1">
                  <Button type="submit" size="sm" disabled={editSubmitting}>
                    {editSubmitting ? "Guardando..." : "Guardar"}
                  </Button>
                  <Button type="button" size="sm" variant="outline" onClick={() => setIsEditing(false)}>
                    Cancelar
                  </Button>
                </div>
              </form>
            ) : (
              <>
                {canEdit && (
                  <Button size="sm" variant="outline" onClick={openEdit} className="w-full">
                    Editar Montos
                  </Button>
                )}
                <div className="rounded-lg border divide-y text-sm">
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Monto inicial</span>
                    <span className="font-mono">{formatCLP(detail.initial_amount)}</span>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Monto vigente</span>
                    <span className="font-mono">{formatCLP(detail.current_amount)}</span>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Comprometido</span>
                    <span className="font-mono">{formatCLP(detail.committed_amount)}</span>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Devengado</span>
                    <span className="font-mono">{formatCLP(detail.accrued_amount)}</span>
                  </div>
                  <div className="flex justify-between px-3 py-2 font-medium">
                    <span>Pagado</span>
                    <span className="font-mono">{formatCLP(detail.paid_amount)}</span>
                  </div>
                  {detail.fndr_amount != null && (
                    <div className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">FNDR</span>
                      <span className="font-mono">{formatCLP(detail.fndr_amount)}</span>
                    </div>
                  )}
                </div>
              </>
            )}

            {/* Clasificación */}
            {(detail.subtitle_label || detail.item_label || detail.allocation_label) && (
              <div className="space-y-1 text-sm">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">Clasificación</p>
                {detail.subtitle_label && (
                  <p><span className="text-muted-foreground">Subtítulo: </span>{detail.subtitle_label}</p>
                )}
                {detail.item_label && (
                  <p><span className="text-muted-foreground">Ítem: </span>{detail.item_label}</p>
                )}
                {detail.allocation_label && (
                  <p><span className="text-muted-foreground">Asignación: </span>{detail.allocation_label}</p>
                )}
              </div>
            )}

            {/* Arrastres */}
            {detail.carryovers.length > 0 && (
              <div className="space-y-2">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">Arrastres</p>
                <div className="rounded-lg border divide-y text-sm">
                  {detail.carryovers.map((co) => (
                    <div key={co.id} className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">Año {co.fiscal_year}</span>
                      <span className="font-mono">{formatCLP(co.amount)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* CDPs */}
            {detail.budget_commitments.length > 0 && (
              <div className="space-y-2">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">
                  CDPs ({detail.budget_commitments.length})
                </p>
                <div className="space-y-2">
                  {detail.budget_commitments.map((cdp) => (
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
                        <span className="font-mono text-xs">{formatCLP(cdp.amount)}</span>
                      </div>
                      {cdp.ipr_codigo_bip && (
                        <p className="text-xs text-muted-foreground mt-0.5">IPR: {cdp.ipr_codigo_bip}</p>
                      )}
                    </div>
                  ))}
                </div>
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
