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
import { Download, Plus, ChevronDown } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import { formatCLP, formatDate } from "@/lib/format";
import { PageHeader } from "@/components/page-header";
import { ComboboxAsync, type ComboboxOption } from "@/components/combobox-async";
import { toast } from "sonner";
import type { PaginatedResponse, PresupuestoListItem, PresupuestoDetail } from "@/types";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const CSV_COLUMNS = [
  { key: "division_name", label: "División" },
  { key: "name", label: "Programa" },
  { key: "program_type_label", label: "Tipo Programa" },
  { key: "program_code_label", label: "Programa DIPRES" },
  { key: "item_label", label: "Ítem" },
  { key: "allocation_label", label: "Asignación" },
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

function ExecutionBar({ pct }: { pct: number }) {
  const color = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-amber-500" : "bg-red-500";
  const textColor = pct >= 70 ? "text-green-700" : pct >= 40 ? "text-amber-700" : "text-red-700";
  return (
    <div className="flex items-center gap-2 min-w-[100px]">
      <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className={`text-xs font-mono font-medium tabular-nums cursor-help ${textColor}`}>{pct}%</span>
        </TooltipTrigger>
        <TooltipContent>Ejecución = Comprometido / Vigente × 100</TooltipContent>
      </Tooltip>
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
  const [editSubtitle, setEditSubtitle] = useState("");
  const [editItem, setEditItem] = useState("");
  const [editAllocation, setEditAllocation] = useState("");

  // Catalog options for classifier selects
  const [subtitleOptions, setSubtitleOptions] = useState<{id: string; label: string}[]>([]);
  const [itemOptions, setItemOptions] = useState<{id: string; label: string}[]>([]);
  const [allocationOptions, setAllocationOptions] = useState<{id: string; label: string}[]>([]);

  // CDP creation state
  const [showCdpForm, setShowCdpForm] = useState(false);
  const [cdpAmount, setCdpAmount] = useState("");
  const [cdpIprId, setCdpIprId] = useState("");
  const [cdpSubmitting, setCdpSubmitting] = useState(false);

  // Division filter options
  const [divisionOptions, setDivisionOptions] = useState<{ value: string; label: string }[]>([]);
  const [programCodeOptions, setProgramCodeOptions] = useState<{ value: string; label: string }[]>([]);

  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);

  const page = Number(searchParams.get("page") ?? "1");
  const fiscal_year = searchParams.get("fiscal_year") ?? "";
  const subtitle = searchParams.get("subtitle") ?? "";
  const division_id = searchParams.get("division_id") ?? "";
  const program_code = searchParams.get("program_code") ?? "";
  const search = searchParams.get("search") ?? "";

  const filterValues: Record<string, string> = { fiscal_year, subtitle, division_id, program_code, search };

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
    api.get<{ id: string; name: string }[]>("/api/catalogs/divisions").then((divs) => {
      setDivisionOptions(divs.map((d) => ({ value: d.id, label: d.name })));
    }).catch(() => {});
    api.get<{ id: string; code: string; label: string }[]>("/api/admin/budget-program-codes").then((codes) => {
      setProgramCodeOptions(codes.map((c) => ({ value: c.code, label: `${c.code} — ${c.label}` })));
    }).catch(() => {});
    api.get<{ id: string; code: string; label: string }[]>("/api/catalogs/categories/budget_subtitle").then(setSubtitleOptions).catch(() => {});
    api.get<{ id: string; code: string; label: string }[]>("/api/catalogs/categories/budget_item").then(setItemOptions).catch(() => {});
    api.get<{ id: string; code: string; label: string }[]>("/api/catalogs/categories/budget_allocation").then(setAllocationOptions).catch(() => {});
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (fiscal_year) params.set("fiscal_year", fiscal_year);
    if (subtitle) params.set("subtitle", subtitle);
    if (division_id) params.set("division_id", division_id);
    if (program_code) params.set("program_code", program_code);
    if (search) params.set("search", search);

    setIsLoading(true);
    api
      .get<PaginatedResponse<PresupuestoListItem>>(`/api/presupuesto?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, fiscal_year, subtitle, division_id, program_code, search]);

  const searchIprs = async (query: string): Promise<ComboboxOption[]> => {
    const results = await api.get<{ id: string; codigo_bip: string; name: string }[]>(
      `/api/catalogs/iprs?search=${encodeURIComponent(query)}`
    );
    return results.map((r) => ({ value: r.id, label: `${r.codigo_bip} — ${r.name}` }));
  };

  const refreshDetail = () => {
    if (!selectedId) return;
    setDetailLoading(true);
    api
      .get<PresupuestoDetail>(`/api/presupuesto/${selectedId}`)
      .then(setDetail)
      .catch(() => {})
      .finally(() => setDetailLoading(false));
  };

  const handleCdpSubmit = async () => {
    if (!selectedId || !cdpAmount) return;
    setCdpSubmitting(true);
    try {
      await api.post(`/api/presupuesto/${selectedId}/cdps`, {
        amount: parseInt(cdpAmount),
        ipr_id: cdpIprId || undefined,
      });
      toast.success("CDP creado exitosamente");
      setCdpAmount("");
      setCdpIprId("");
      setShowCdpForm(false);
      refreshDetail();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear CDP");
    } finally {
      setCdpSubmitting(false);
    }
  };

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
    setEditSubtitle(detail.subtitle_id ?? "");
    setEditItem(detail.item_id ?? "");
    setEditAllocation(detail.allocation_id ?? "");
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
        subtitle_id: editSubtitle || undefined,
        item_id: editItem || undefined,
        allocation_id: editAllocation || undefined,
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
      key: "program_code_label",
      label: "Programa",
      render: (v: unknown) => (
        <span className="text-xs text-muted-foreground">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "item_label",
      label: "Ítem",
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
    <TooltipProvider>
    <div className="p-6 space-y-4">
      <PageHeader
        title="Presupuesto"
        description="Programas presupuestarios y ejecución financiera"
        actions={
          <>
            {canEdit && (
              <Button size="sm" onClick={() => router.push("/presupuesto/nuevo")}>
                <Plus className="size-4 mr-1" />Nuevo Programa
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "presupuesto")}>
              <Download className="size-4 mr-1" />CSV
            </Button>
          </>
        }
      />

      <FilterBar
        filters={[
          { key: "fiscal_year", label: "Año", options: YEAR_OPTIONS },
          { key: "subtitle", label: "Subtítulo", options: SUBTITLE_OPTIONS },
          { key: "division_id", label: "División", options: divisionOptions },
          { key: "program_code", label: "Programa", options: programCodeOptions },
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
                <div className="border-t pt-2 mt-2 space-y-2">
                  <p className="text-xs font-medium text-muted-foreground">Clasificador</p>
                  {subtitleOptions.length > 0 && (
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-muted-foreground w-28 shrink-0">Subtítulo</label>
                      <Select value={editSubtitle} onValueChange={setEditSubtitle}>
                        <SelectTrigger className="h-8 text-xs flex-1">
                          <SelectValue placeholder="Sin cambio" />
                        </SelectTrigger>
                        <SelectContent>
                          {subtitleOptions.map((o) => (
                            <SelectItem key={o.id} value={o.id}>{o.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                  {itemOptions.length > 0 && (
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-muted-foreground w-28 shrink-0">Ítem</label>
                      <Select value={editItem} onValueChange={setEditItem}>
                        <SelectTrigger className="h-8 text-xs flex-1">
                          <SelectValue placeholder="Sin cambio" />
                        </SelectTrigger>
                        <SelectContent>
                          {itemOptions.map((o) => (
                            <SelectItem key={o.id} value={o.id}>{o.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                  {allocationOptions.length > 0 && (
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-muted-foreground w-28 shrink-0">Asignación</label>
                      <Select value={editAllocation} onValueChange={setEditAllocation}>
                        <SelectTrigger className="h-8 text-xs flex-1">
                          <SelectValue placeholder="Sin cambio" />
                        </SelectTrigger>
                        <SelectContent>
                          {allocationOptions.map((o) => (
                            <SelectItem key={o.id} value={o.id}>{o.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>
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
            {(detail.subtitle_label || detail.program_code_label || detail.item_label || detail.allocation_label) && (
              <div className="space-y-1 text-sm">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">Clasificación</p>
                {detail.subtitle_label && (
                  <p><span className="text-muted-foreground">Subtítulo: </span>{detail.subtitle_label}</p>
                )}
                {detail.program_code_label && (
                  <p><span className="text-muted-foreground">Programa: </span>{detail.program_code_label}</p>
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
            <div className="space-y-2">
              <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">
                CDPs ({detail.budget_commitments.length})
              </p>
              {detail.budget_commitments.length > 0 && (
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
                        <p className="text-xs text-muted-foreground mt-0.5">
                          IPR:{" "}
                          {cdp.ipr_id ? (
                            <button
                              type="button"
                              className="font-mono text-blue-600 hover:underline cursor-pointer"
                              onClick={() => { setSelectedId(null); router.push(`/ipr/${cdp.ipr_id}`); }}
                            >
                              {cdp.ipr_codigo_bip}
                            </button>
                          ) : (
                            <span className="font-mono">{cdp.ipr_codigo_bip}</span>
                          )}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* CDP creation form */}
              {canEdit && (
                <div>
                  <button
                    type="button"
                    onClick={() => setShowCdpForm(!showCdpForm)}
                    className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
                  >
                    <ChevronDown className={`size-3 transition-transform ${showCdpForm ? "rotate-180" : ""}`} />
                    Nuevo CDP
                  </button>
                  {showCdpForm && (
                    <div className="mt-2 space-y-2 rounded-md border p-3">
                      <div className="space-y-1">
                        <label className="text-xs text-muted-foreground">Monto (CLP) *</label>
                        <Input
                          type="number"
                          min="1"
                          step="1"
                          value={cdpAmount}
                          onChange={(e) => setCdpAmount(e.target.value)}
                          className="h-7 text-xs"
                          placeholder="Monto del CDP"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs text-muted-foreground">IPR Asociada (opcional)</label>
                        <ComboboxAsync
                          value={cdpIprId}
                          onChange={setCdpIprId}
                          searchFn={searchIprs}
                          placeholder="Buscar IPR..."
                        />
                      </div>
                      <div className="flex gap-2 pt-1">
                        <Button
                          size="sm"
                          className="h-7 text-xs"
                          disabled={!cdpAmount || cdpSubmitting}
                          onClick={handleCdpSubmit}
                        >
                          {cdpSubmitting ? "Creando..." : "Crear CDP"}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-7 text-xs"
                          onClick={() => { setShowCdpForm(false); setCdpAmount(""); setCdpIprId(""); }}
                        >
                          Cancelar
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">No se pudo cargar el detalle.</p>
        )}
      </DrawerPanel>
    </div>
    </TooltipProvider>
  );
}
