"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { TimelineHistory } from "@/components/timeline-history";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";
import { AlertTriangle, Clock, Download, Plus } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import { cn } from "@/lib/utils";
import { formatCLP, formatDate } from "@/lib/format";
import { DeadlineCell } from "@/components/deadline-cell";
import { PageHeader } from "@/components/page-header";
import type { PaginatedResponse, ConvenioListItem, ConvenioDetail, ConvenioResumen, CategoryRef, InstallmentItem, RenditionSummaryItem } from "@/types";

const CSV_COLUMNS = [
  { key: "agreement_number", label: "Número" },
  { key: "agreement_type_label", label: "Tipo" },
  { key: "state", label: "Estado" },
  { key: "receiver_name", label: "Contraparte" },
  { key: "total_amount", label: "Monto" },
  { key: "valid_to", label: "Vigencia Hasta" },
];

const STATE_OPTIONS = [
  { value: "VIGENTE", label: "Vigente" },
  { value: "EN_MODIFICACION", label: "En Modificación" },
  { value: "FIRMADO_CONTRAPARTE", label: "Firmado Contraparte" },
  { value: "FIRMADO_GORE", label: "Firmado GORE" },
  { value: "EN_REVISION_JURIDICA", label: "En Revisión Jurídica" },
  { value: "EN_REVISION_FINANCIERA", label: "En Revisión Financiera" },
  { value: "VISADO_INTERNO", label: "Visado Interno" },
  { value: "EN_NEGOCIACION", label: "En Negociación" },
  { value: "TDR_PENDIENTE", label: "TdR Pendiente" },
  { value: "BORRADOR", label: "Borrador" },
  { value: "VENCIDO", label: "Vencido" },
  { value: "TERMINADO", label: "Terminado" },
  { value: "RESCILIADO", label: "Resciliado" },
];

const TYPE_OPTIONS = [
  { value: "MANDATO", label: "Mandato" },
  { value: "TRANSFERENCIA", label: "Transferencia" },
  { value: "COLABORACION", label: "Colaboración" },
  { value: "PROGRAMACION", label: "Programación" },
  { value: "MARCO", label: "Marco" },
  { value: "EJECUCION", label: "Ejecución Directa" },
];

const PAYMENT_STATUS_COLORS: Record<string, string> = {
  PAGADO: "text-green-700 bg-green-50 border-green-200",
  EN_PROCESO: "text-blue-700 bg-blue-50 border-blue-200",
  PENDIENTE: "text-amber-700 bg-amber-50 border-amber-200",
  DIFERIDO: "text-orange-700 bg-orange-50 border-orange-200",
  RECHAZADO: "text-red-700 bg-red-50 border-red-200",
};

const RENDITION_STATE_COLORS: Record<string, string> = {
  INGRESADA: "text-blue-700 bg-blue-50 border-blue-200",
  EN_REVISION_RTF: "text-purple-700 bg-purple-50 border-purple-200",
  VISADA_RTF: "text-indigo-700 bg-indigo-50 border-indigo-200",
  EN_REVISION_UCR: "text-cyan-700 bg-cyan-50 border-cyan-200",
  OBSERVADA: "text-amber-700 bg-amber-50 border-amber-200",
  APROBADA: "text-green-700 bg-green-50 border-green-200",
  RECHAZADA: "text-red-700 bg-red-50 border-red-200",
  EN_CORRECCION: "text-orange-700 bg-orange-50 border-orange-200",
};

export default function ConveniosPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<ConvenioListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ConvenioDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Edit state
  const [isEditing, setIsEditing] = useState(false);
  const [editStateId, setEditStateId] = useState("");
  const [editTotalAmount, setEditTotalAmount] = useState("");
  const [editValidTo, setEditValidTo] = useState("");
  const [editCgrOutcome, setEditCgrOutcome] = useState("");
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [validTransitions, setValidTransitions] = useState<{ id: string; code: string; label: string }[]>([]);
  const [cgrOptions, setCgrOptions] = useState<CategoryRef[]>([]);

  // Cuota state
  const [showCuotaForm, setShowCuotaForm] = useState(false);
  const [cuotaAmount, setCuotaAmount] = useState("");
  const [cuotaDueDate, setCuotaDueDate] = useState("");
  const [cuotaSubmitting, setCuotaSubmitting] = useState(false);
  const [cuotaError, setCuotaError] = useState<string | null>(null);
  const [paymentStatuses, setPaymentStatuses] = useState<CategoryRef[]>([]);

  // Bulk cuota state
  const [showBulkForm, setShowBulkForm] = useState(false);
  const [bulkTotalAmount, setBulkTotalAmount] = useState("");
  const [bulkNumInstallments, setBulkNumInstallments] = useState("6");
  const [bulkStartDate, setBulkStartDate] = useState("");
  const [bulkFrequency, setBulkFrequency] = useState("1");
  const [bulkSubmitting, setBulkSubmitting] = useState(false);

  // Payment registration state
  const [payingCuotaId, setPayingCuotaId] = useState<string | null>(null);
  const [payAmount, setPayAmount] = useState("");
  const [payRef, setPayRef] = useState("");
  const [paySubmitting, setPaySubmitting] = useState(false);
  const [confirmPayOpen, setConfirmPayOpen] = useState(false);

  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "ANALISTA", "ASESOR_JURIDICO"].includes(user.role_code);

  // Role awareness
  const role = user?.role_code;
  const isJuridico = role === "ASESOR_JURIDICO";
  const didAutoScope = useRef(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [expiringItems, setExpiringItems] = useState<ConvenioListItem[]>([]);
  const [resumen, setResumen] = useState<ConvenioResumen | null>(null);

  const page = Number(searchParams.get("page") ?? "1");
  const state = searchParams.get("state") ?? "";
  const agreement_type = searchParams.get("agreement_type") ?? "";
  const dateFrom = searchParams.get("date_from") ?? "";
  const dateTo = searchParams.get("date_to") ?? "";

  const filterValues: Record<string, string> = { state, agreement_type };

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
    if (state) params.set("state", state);
    if (agreement_type) params.set("agreement_type", agreement_type);
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);

    setIsLoading(true);
    api
      .get<PaginatedResponse<ConvenioListItem>>(`/api/convenios?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, state, agreement_type, dateFrom, dateTo, refreshKey]);

  // Auto-scope: ASESOR_JURIDICO gets EN_REVISION_JURIDICA pre-selected
  useEffect(() => {
    if (didAutoScope.current) return;
    if (isJuridico && !searchParams.has("state")) {
      didAutoScope.current = true;
      const params = new URLSearchParams(searchParams.toString());
      params.set("state", "EN_REVISION_JURIDICA");
      router.replace(`${pathname}?${params.toString()}`);
    }
  }, [isJuridico, searchParams, pathname, router]);

  // Fetch expiring convenios + resumen
  useEffect(() => {
    api
      .get<PaginatedResponse<ConvenioListItem>>("/api/convenios?state=VIGENTE&page_size=50")
      .then((r) =>
        setExpiringItems(
          r.items
            .filter((i) => i.days_to_expiry !== null && i.days_to_expiry >= 0 && i.days_to_expiry <= 90)
            .sort((a, b) => (a.days_to_expiry ?? 999) - (b.days_to_expiry ?? 999))
        )
      )
      .catch(() => setExpiringItems([]));
    api
      .get<ConvenioResumen>("/api/convenios/resumen")
      .then(setResumen)
      .catch(() => setResumen(null));
  }, [refreshKey]);

  const openDetail = (row: unknown) => {
    const item = row as ConvenioListItem;
    setSelectedId(item.id);
    setDetail(null);
    setIsEditing(false);
    setEditError(null);
    setDetailLoading(true);
    api
      .get<ConvenioDetail>(`/api/convenios/${item.id}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false));
  };

  const openEdit = () => {
    if (!detail || !selectedId) return;
    setEditStateId("");
    setEditTotalAmount(String(detail.total_amount ?? ""));
    setEditValidTo(detail.valid_to ? detail.valid_to.slice(0, 10) : "");
    setEditCgrOutcome("");
    setEditError(null);
    setValidTransitions([]);
    setIsEditing(true);
    api
      .get<{ id: string; code: string; label: string }[]>(`/api/convenios/${selectedId}/transiciones`)
      .then(setValidTransitions)
      .catch(() => setValidTransitions([]));
    api
      .get<CategoryRef[]>("/api/catalogs/categories/cgr_outcome")
      .then(setCgrOptions)
      .catch(() => setCgrOptions([]));
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId) return;
    setEditSubmitting(true);
    setEditError(null);
    const body: Record<string, unknown> = {};
    if (editStateId) body.state_id = editStateId;
    if (editTotalAmount) body.total_amount = parseFloat(editTotalAmount);
    if (editValidTo) body.valid_to = editValidTo;
    if (editCgrOutcome) body.cgr_outcome_id = editCgrOutcome;
    try {
      await api.patch(`/api/convenios/${selectedId}`, body);
      setIsEditing(false);
      setDetailLoading(true);
      api
        .get<ConvenioDetail>(`/api/convenios/${selectedId}`)
        .then(setDetail)
        .catch(() => {})
        .finally(() => setDetailLoading(false));
      setRefreshKey((k) => k + 1);
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEditSubmitting(false);
    }
  };

  const refreshDetail = () => {
    if (!selectedId) return;
    setDetailLoading(true);
    api
      .get<ConvenioDetail>(`/api/convenios/${selectedId}`)
      .then(setDetail)
      .catch(() => {})
      .finally(() => setDetailLoading(false));
  };

  const openCuotaForm = () => {
    setCuotaAmount("");
    setCuotaDueDate("");
    setCuotaError(null);
    setShowCuotaForm(true);
    if (paymentStatuses.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/payment_status").then(setPaymentStatuses).catch(() => {});
    }
  };

  const handleCuotaSubmit = async () => {
    if (!selectedId || !cuotaAmount || !cuotaDueDate) return;
    const pendienteStatus = paymentStatuses.find((s) => s.code === "PENDIENTE");
    if (!pendienteStatus) { setCuotaError("Estado PENDIENTE no encontrado"); return; }
    const nextNumber = (detail?.installments.length ?? 0) + 1;
    setCuotaSubmitting(true);
    setCuotaError(null);
    try {
      await api.post(`/api/convenios/${selectedId}/cuotas`, {
        installment_number: nextNumber,
        amount: parseFloat(cuotaAmount),
        due_date: cuotaDueDate,
        payment_status_id: pendienteStatus.id,
      });
      setShowCuotaForm(false);
      refreshDetail();
    } catch (err) {
      setCuotaError(err instanceof Error ? err.message : "Error al crear cuota");
    } finally {
      setCuotaSubmitting(false);
    }
  };

  const handleBulkSubmit = async () => {
    if (!selectedId || !bulkTotalAmount || !bulkNumInstallments || !bulkStartDate) return;
    setBulkSubmitting(true);
    try {
      await api.post(`/api/convenios/${selectedId}/cuotas/bulk`, {
        total_amount: parseInt(bulkTotalAmount),
        num_installments: parseInt(bulkNumInstallments),
        start_date: bulkStartDate,
        frequency_months: parseInt(bulkFrequency),
      });
      toast.success(`${bulkNumInstallments} cuotas generadas exitosamente`);
      setShowBulkForm(false);
      setBulkTotalAmount("");
      setBulkNumInstallments("6");
      setBulkStartDate("");
      setBulkFrequency("1");
      refreshDetail();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al generar cuotas");
    } finally {
      setBulkSubmitting(false);
    }
  };

  const bulkAmountPer = bulkTotalAmount && bulkNumInstallments
    ? Math.floor(parseInt(bulkTotalAmount) / parseInt(bulkNumInstallments))
    : 0;

  const openPayForm = (inst: InstallmentItem) => {
    setPayingCuotaId(inst.id);
    setPayAmount(String(inst.amount));
    setPayRef("");
    if (paymentStatuses.length === 0) {
      api.get<CategoryRef[]>("/api/catalogs/categories/payment_status").then(setPaymentStatuses).catch(() => {});
    }
  };

  const handlePaySubmit = async () => {
    if (!selectedId || !payingCuotaId) return;
    const pagadoStatus = paymentStatuses.find((s) => s.code === "PAGADO");
    if (!pagadoStatus) return;
    setPaySubmitting(true);
    setConfirmPayOpen(false);
    try {
      await api.patch(`/api/convenios/${selectedId}/cuotas/${payingCuotaId}`, {
        payment_status_id: pagadoStatus.id,
        paid_at: new Date().toISOString(),
        paid_amount: payAmount ? parseFloat(payAmount) : null,
        payment_reference: payRef || null,
      });
      setPayingCuotaId(null);
      refreshDetail();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al registrar pago");
    } finally {
      setPaySubmitting(false);
    }
  };

  const columns = [
    {
      key: "agreement_number",
      label: "N° Convenio",
      render: (v: unknown) => (
        <span className="font-mono text-xs">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "agreement_type_label",
      label: "Tipo",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "-")}</Badge>
      ),
    },
    {
      key: "ipr_codigo_bip",
      label: "BIP",
      render: (v: unknown) => (
        <span className="font-mono text-xs text-muted-foreground">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "receiver_name",
      label: "Receptor",
      render: (v: unknown) => (
        <span className="text-sm line-clamp-1 max-w-[160px]">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "total_amount",
      label: "Monto",
      render: (v: unknown) => (
        <span className="text-xs font-mono tabular-nums">{formatCLP(Number(v))}</span>
      ),
    },
    {
      key: "days_to_expiry",
      label: "Vencimiento",
      render: (_: unknown, row: unknown) => {
        const r = row as ConvenioListItem;
        if (r.state === "VENCIDO")
          return <StatusBadge status="VENCIDO" size="sm" />;
        if (r.days_to_expiry !== null)
          return <TemporalIndicator daysRemaining={r.days_to_expiry} state={r.state} />;
        return <DeadlineCell date={r.valid_to ?? null} />;
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
      <PageHeader
        title="Convenios"
        description={
          isJuridico
            ? "Revisión jurídica de convenios"
            : "Gestión de convenios y cuotas de pago"
        }
        accentColor="emerald"
        actions={
          <>
            <Button variant="outline" size="sm" onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "convenios")}>
              <Download className="size-4 mr-1" />CSV
            </Button>
            {canEdit && (
              <Button size="sm" onClick={() => router.push("/convenios/nuevo")}>
                <Plus className="size-4 mr-1" />
                Nuevo Convenio
              </Button>
            )}
          </>
        }
      />

      {/* KPI Strip */}
      {resumen && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-lg border bg-card p-3">
            <p className="text-xs text-muted-foreground">Total convenios</p>
            <p className="text-2xl font-semibold tabular-nums">{resumen.total}</p>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <p className="text-xs text-muted-foreground">Vencen en 30 días</p>
            <p className={cn("text-2xl font-semibold tabular-nums", resumen.expiring_30d > 0 ? "text-red-600" : "")}>
              {resumen.expiring_30d}
            </p>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <p className="text-xs text-muted-foreground">Sin IPR vinculado</p>
            <p className={cn("text-2xl font-semibold tabular-nums", resumen.without_ipr > 0 ? "text-amber-600" : "")}>
              {resumen.without_ipr}
            </p>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <p className="text-xs text-muted-foreground">Monto total</p>
            <p className="text-lg font-semibold tabular-nums font-mono">{formatCLP(resumen.total_amount)}</p>
          </div>
        </div>
      )}

      {/* Próximos a vencer */}
      {expiringItems.length > 0 && (
        <div className="rounded-lg border bg-card overflow-hidden border-l-4 border-l-amber-400">
          <div className="px-4 py-3 bg-amber-50/50 dark:bg-amber-950/20 flex items-center gap-2">
            <Clock className="size-4 text-amber-600" />
            <h3 className="text-sm font-semibold">Próximos a vencer</h3>
            <span className="text-xs text-muted-foreground tabular-nums ml-auto">
              {expiringItems.length}
            </span>
          </div>
          <div className="divide-y">
            {expiringItems.slice(0, 5).map((item) => (
              <div
                key={item.id}
                onClick={() => openDetail(item)}
                className={cn(
                  "flex items-center gap-3 px-4 py-2.5 cursor-pointer hover:bg-muted/50 transition-colors",
                  item.days_to_expiry !== null && item.days_to_expiry < 30
                    ? "bg-red-50/30 dark:bg-red-950/10"
                    : ""
                )}
              >
                <span className="font-mono text-xs text-muted-foreground shrink-0 w-28">
                  {item.agreement_number ?? "-"}
                </span>
                <span className="flex-1 text-sm truncate">{item.receiver_name ?? "-"}</span>
                <span className="text-xs font-mono tabular-nums text-muted-foreground shrink-0">
                  {formatCLP(item.total_amount)}
                </span>
                <span
                  className={cn(
                    "text-xs tabular-nums font-medium shrink-0 w-10 text-right",
                    item.days_to_expiry !== null && item.days_to_expiry < 30
                      ? "text-red-600"
                      : item.days_to_expiry !== null && item.days_to_expiry < 60
                        ? "text-amber-600"
                        : "text-muted-foreground"
                  )}
                >
                  {item.days_to_expiry}d
                </span>
              </div>
            ))}
            {expiringItems.length > 5 && (
              <p className="px-4 py-2 text-xs text-muted-foreground text-center">
                +{expiringItems.length - 5} más
              </p>
            )}
          </div>
        </div>
      )}

      <FilterBar
        filters={[
          { key: "state", label: "Estado", options: STATE_OPTIONS },
          { key: "agreement_type", label: "Tipo", options: TYPE_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar por número o BIP..."
      />

      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground whitespace-nowrap">Vigencia hasta:</span>
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
        title="Detalle de Convenio"
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
                <span className="font-mono text-xs text-muted-foreground">{detail.agreement_number ?? "Sin número"}</span>
                <Badge variant="outline" className="text-xs">{detail.agreement_type_label}</Badge>
                <StatusBadge status={detail.state} size="sm" />
              </div>
              {/* Financial chain strip */}
              {(detail.pending_renditions != null && detail.pending_renditions > 0) && (
                <div className="mt-2 flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs">
                  <AlertTriangle className="size-3.5 text-amber-600 shrink-0" />
                  <span className="text-amber-800">
                    {detail.pending_renditions} rendición{detail.pending_renditions > 1 ? "es" : ""} pendiente{detail.pending_renditions > 1 ? "s" : ""}
                    {detail.blocked_renditions != null && detail.blocked_renditions > 0 && (
                      <> · <span className="font-medium">{detail.blocked_renditions} bloqueante{detail.blocked_renditions > 1 ? "s" : ""} (Art. 18)</span></>
                    )}
                  </span>
                  <button
                    onClick={() => {
                      setSelectedId(null);
                      router.push(`/datos?dominio=rendiciones`);
                    }}
                    className="ml-auto text-amber-700 underline hover:text-amber-900"
                  >
                    Ver
                  </button>
                </div>
              )}
              {canEdit && !isEditing && (
                <Button size="sm" variant="outline" onClick={openEdit} className="mt-2 w-full">
                  Editar
                </Button>
              )}
              {isEditing && (
                <form onSubmit={handleEditSubmit} className="mt-3 space-y-3">
                  <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">Editar Convenio</p>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground">Estado</label>
                    {validTransitions.length > 0 ? (
                      <Select value={editStateId} onValueChange={setEditStateId}>
                        <SelectTrigger className="h-8 text-xs">
                          <SelectValue placeholder="Seleccione nuevo estado" />
                        </SelectTrigger>
                        <SelectContent>
                          {validTransitions.map((t) => (
                            <SelectItem key={t.id} value={t.id} className="text-xs">
                              {t.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      <p className="text-xs text-muted-foreground italic py-1">(Estado final — sin transiciones disponibles)</p>
                    )}
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground">Monto total (CLP)</label>
                    <Input
                      type="number"
                      min="0"
                      value={editTotalAmount}
                      onChange={(e) => setEditTotalAmount(e.target.value)}
                      className="h-8 text-xs"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground">Vigencia hasta</label>
                    <Input
                      type="date"
                      value={editValidTo}
                      onChange={(e) => setEditValidTo(e.target.value)}
                      className="h-8 text-xs"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground">Resultado CGR</label>
                    <Select value={editCgrOutcome} onValueChange={setEditCgrOutcome}>
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue placeholder="Sin cambio" />
                      </SelectTrigger>
                      <SelectContent>
                        {cgrOptions.map((opt) => (
                          <SelectItem key={opt.id} value={opt.id} className="text-xs">
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
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
              )}
              {detail.ipr_name && (
                <p className="text-sm mt-2">
                  <span className="text-muted-foreground">IPR: </span>
                  {detail.ipr_id ? (
                    <button
                      type="button"
                      className="font-mono text-xs text-blue-600 hover:underline cursor-pointer"
                      onClick={() => { setSelectedId(null); router.push(`/ipr/${detail.ipr_id}`); }}
                    >
                      {detail.ipr_codigo_bip}
                    </button>
                  ) : (
                    <span className="font-mono text-xs">{detail.ipr_codigo_bip}</span>
                  )}
                  {` — ${detail.ipr_name}`}
                </p>
              )}
            </div>

            {/* Partes */}
            <div className="space-y-1 text-sm">
              <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">Partes</p>
              <p><span className="text-muted-foreground">Otorgante: </span>{detail.giver_name ?? "-"}</p>
              <p><span className="text-muted-foreground">Receptor: </span>{detail.receiver_name ?? "-"}</p>
              {detail.technical_referent_name && (
                <p><span className="text-muted-foreground">Referente técnico: </span>{detail.technical_referent_name}</p>
              )}
            </div>

            {/* Montos y fechas */}
            <div className="rounded-lg border divide-y text-sm">
              <div className="flex justify-between px-3 py-2 font-medium">
                <span>Monto total</span>
                <span className="font-mono">{formatCLP(detail.total_amount)}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Firmado</span>
                <span>{formatDate(detail.signed_at)}</span>
              </div>
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Vigencia desde</span>
                <span>{formatDate(detail.valid_from)}</span>
              </div>
              {detail.days_to_expiry !== null && detail.days_to_expiry >= 0 && detail.days_to_expiry < 90 && (
                <div className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-xs border mx-3 mb-1 ${
                  detail.days_to_expiry < 30 ? "bg-red-50 border-red-200 text-red-800" :
                  detail.days_to_expiry < 60 ? "bg-amber-50 border-amber-200 text-amber-800" :
                  "bg-yellow-50 border-yellow-200 text-yellow-800"
                }`}>
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                  Vigencia vence en {detail.days_to_expiry} dia{detail.days_to_expiry !== 1 ? "s" : ""}
                </div>
              )}
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Vigencia hasta</span>
                <span className={
                  detail.days_to_expiry !== null && detail.days_to_expiry >= 0 && detail.days_to_expiry < 30 ? "text-red-600 font-medium" :
                  detail.days_to_expiry !== null && detail.days_to_expiry >= 0 && detail.days_to_expiry < 60 ? "text-amber-600 font-medium" :
                  detail.days_to_expiry !== null && detail.days_to_expiry >= 0 && detail.days_to_expiry < 90 ? "text-yellow-700" : ""
                }>
                  {formatDate(detail.valid_to)}
                  {detail.days_to_expiry !== null && detail.days_to_expiry >= 0 && (
                    <span className="text-xs text-muted-foreground ml-1">({detail.days_to_expiry}d)</span>
                  )}
                </span>
              </div>
            </div>

            {/* CGR */}
            {detail.cgr_outcome_label && (
              <div className="text-sm">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide mb-1">Resultado CGR</p>
                <Badge variant="outline">{detail.cgr_outcome_label}</Badge>
              </div>
            )}

            {/* Cuotas */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">
                  Cuotas ({detail.paid_installments}/{detail.installment_count} pagadas)
                </p>
                {canEdit && !showCuotaForm && !showBulkForm && (
                  <div className="flex gap-1">
                    <Button size="sm" variant="outline" className="h-6 text-xs" onClick={openCuotaForm}>
                      <Plus className="size-3 mr-1" />Cuota
                    </Button>
                    <Button size="sm" variant="outline" className="h-6 text-xs" onClick={() => setShowBulkForm(true)}>
                      Generar
                    </Button>
                  </div>
                )}
              </div>

              {/* Bulk cuota form */}
              {showBulkForm && (
                <div className="rounded-md border p-3 space-y-2 bg-muted/30">
                  <p className="text-xs font-medium">Generar Cuotas Masivamente</p>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <label className="text-[10px] text-muted-foreground">Monto total (CLP)</label>
                      <Input type="number" min="1" value={bulkTotalAmount} onChange={(e) => setBulkTotalAmount(e.target.value)} className="h-7 text-xs" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] text-muted-foreground">Cantidad cuotas</label>
                      <Input type="number" min="1" max="60" value={bulkNumInstallments} onChange={(e) => setBulkNumInstallments(e.target.value)} className="h-7 text-xs" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] text-muted-foreground">Fecha inicio</label>
                      <Input type="date" value={bulkStartDate} onChange={(e) => setBulkStartDate(e.target.value)} className="h-7 text-xs" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] text-muted-foreground">Frecuencia</label>
                      <Select value={bulkFrequency} onValueChange={setBulkFrequency}>
                        <SelectTrigger className="h-7 text-xs">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">Mensual</SelectItem>
                          <SelectItem value="3">Trimestral</SelectItem>
                          <SelectItem value="6">Semestral</SelectItem>
                          <SelectItem value="12">Anual</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  {bulkAmountPer > 0 && (
                    <p className="text-[10px] text-muted-foreground">
                      {bulkNumInstallments} cuotas de {formatCLP(bulkAmountPer)} CLP
                    </p>
                  )}
                  <div className="flex gap-1">
                    <Button size="sm" className="h-6 text-xs" onClick={handleBulkSubmit} disabled={bulkSubmitting || !bulkTotalAmount || !bulkNumInstallments || !bulkStartDate}>
                      {bulkSubmitting ? "Generando..." : "Generar"}
                    </Button>
                    <Button size="sm" variant="ghost" className="h-6 text-xs" onClick={() => setShowBulkForm(false)}>Cancelar</Button>
                  </div>
                </div>
              )}

              {/* Add cuota form */}
              {showCuotaForm && (
                <div className="rounded-md border p-3 space-y-2 bg-muted/30">
                  <p className="text-xs font-medium">Nueva cuota #{(detail.installments.length) + 1}</p>
                  <div className="grid grid-cols-2 gap-2">
                    <Input type="number" min="0" placeholder="Monto (CLP)" value={cuotaAmount} onChange={(e) => setCuotaAmount(e.target.value)} className="h-7 text-xs" />
                    <Input type="date" value={cuotaDueDate} onChange={(e) => setCuotaDueDate(e.target.value)} className="h-7 text-xs" />
                  </div>
                  {cuotaError && <p className="text-xs text-red-600">{cuotaError}</p>}
                  <div className="flex gap-1">
                    <Button size="sm" className="h-6 text-xs" onClick={handleCuotaSubmit} disabled={cuotaSubmitting || !cuotaAmount || !cuotaDueDate}>
                      {cuotaSubmitting ? "..." : "Crear"}
                    </Button>
                    <Button size="sm" variant="ghost" className="h-6 text-xs" onClick={() => setShowCuotaForm(false)}>Cancelar</Button>
                  </div>
                </div>
              )}

              {detail.installments.length > 0 && (
                <div className="space-y-2">
                  {detail.installments.map((inst) => (
                    <div key={inst.id} className="rounded-md border px-3 py-2 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-xs">Cuota {inst.installment_number}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded border font-medium ${PAYMENT_STATUS_COLORS[inst.payment_status] ?? ""}`}>
                          {inst.payment_status_label}
                        </span>
                      </div>
                      <div className="flex justify-between mt-1 text-xs text-muted-foreground">
                        <span>Vence: {formatDate(inst.due_date)}</span>
                        <span className="font-mono">{formatCLP(inst.amount)}</span>
                      </div>
                      {inst.paid_at && (
                        <p className="text-xs text-green-600 mt-0.5">
                          Pagado: {formatDate(inst.paid_at)} — {formatCLP(inst.paid_amount)}
                        </p>
                      )}
                      {inst.payment_reference && (
                        <p className="text-xs text-muted-foreground mt-0.5">Ref: {inst.payment_reference}</p>
                      )}
                      {/* Pay button */}
                      {canEdit && inst.payment_status !== "PAGADO" && payingCuotaId !== inst.id && (
                        <Button size="sm" variant="outline" className="h-8 text-xs mt-1" onClick={() => openPayForm(inst)}>
                          Registrar Pago
                        </Button>
                      )}
                      {/* Pay form inline */}
                      {payingCuotaId === inst.id && (
                        <div className="mt-2 space-y-1.5 p-2 rounded bg-muted/30">
                          <div className="grid grid-cols-2 gap-1.5">
                            <Input type="number" min="0" placeholder="Monto pagado" value={payAmount} onChange={(e) => setPayAmount(e.target.value)} className="h-6 text-xs" />
                            <Input placeholder="Referencia" value={payRef} onChange={(e) => setPayRef(e.target.value)} className="h-6 text-xs" />
                          </div>
                          <div className="flex gap-1">
                            <Button size="sm" className="h-5 text-[10px]" onClick={() => setConfirmPayOpen(true)} disabled={paySubmitting}>
                              {paySubmitting ? "..." : "Confirmar"}
                            </Button>
                            <Button size="sm" variant="ghost" className="h-5 text-[10px]" onClick={() => setPayingCuotaId(null)}>Cancelar</Button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Cadena Financiera: cuotas ↔ rendiciones */}
            {detail.renditions && detail.renditions.length > 0 && (
              <div className="space-y-2">
                <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">
                  Cadena Financiera
                </p>
                <div className="rounded-lg border overflow-hidden">
                  <div className="grid grid-cols-[1fr_auto_auto] gap-2 px-3 py-1.5 bg-muted/40 text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                    <span>Rendición</span>
                    <span>Monto</span>
                    <span>Estado</span>
                  </div>
                  <div className="divide-y">
                    {detail.renditions.map((rend) => (
                      <div key={rend.id} className="grid grid-cols-[1fr_auto_auto] gap-2 px-3 py-2 items-center">
                        <div>
                          <span className="font-mono text-xs text-muted-foreground">{rend.short_id}…</span>
                          <span className="text-[10px] text-muted-foreground ml-2">{formatDate(rend.created_at)}</span>
                        </div>
                        <span className="text-xs font-mono tabular-nums">{rend.amount ? formatCLP(rend.amount) : "—"}</span>
                        <span className={cn(
                          "text-[10px] px-1.5 py-0.5 rounded border font-medium whitespace-nowrap",
                          RENDITION_STATE_COLORS[rend.state] ?? "text-gray-700 bg-gray-50 border-gray-200"
                        )}>
                          {rend.state_label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                {/* Summary line */}
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{detail.renditions.length} rendición{detail.renditions.length > 1 ? "es" : ""}</span>
                  <span>·</span>
                  <span className="text-green-600">
                    {detail.renditions.filter((r) => r.state === "APROBADA").length} aprobada{detail.renditions.filter((r) => r.state === "APROBADA").length !== 1 ? "s" : ""}
                  </span>
                  {detail.renditions.some((r) => r.state === "OBSERVADA") && (
                    <>
                      <span>·</span>
                      <span className="text-amber-600">
                        {detail.renditions.filter((r) => r.state === "OBSERVADA").length} observada{detail.renditions.filter((r) => r.state === "OBSERVADA").length !== 1 ? "s" : ""}
                      </span>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Historial de estados */}
            {detail.history && detail.history.length > 0 && (
              <div className="pt-2 border-t">
                <h3 className="text-sm font-semibold mb-3">Historial de Estados</h3>
                <TimelineHistory entries={detail.history} />
              </div>
            )}
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">No se pudo cargar el detalle.</p>
        )}
      </DrawerPanel>

      {/* Confirmación de pago */}
      <Dialog open={confirmPayOpen} onOpenChange={setConfirmPayOpen}>
        <DialogContent className="sm:max-w-[380px]">
          <DialogHeader>
            <DialogTitle>Confirmar Pago</DialogTitle>
            <DialogDescription>
              Registrar pago de {payAmount ? formatCLP(parseFloat(payAmount)) : "—"}{payRef ? ` (Ref: ${payRef})` : ""}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmPayOpen(false)}>Cancelar</Button>
            <Button onClick={handlePaySubmit} disabled={paySubmitting}>
              {paySubmitting ? "Registrando..." : "Confirmar Pago"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
