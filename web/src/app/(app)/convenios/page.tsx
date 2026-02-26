"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
import { StatusBadge } from "@/components/status-badge";
import { TemporalIndicator } from "@/components/temporal-indicator";
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
import { useAuth } from "@/lib/auth";
import type { PaginatedResponse, ConvenioListItem, ConvenioDetail } from "@/types";

const STATE_OPTIONS = [
  { value: "VIGENTE", label: "Vigente" },
  { value: "EN_MODIFICACION", label: "En Modificación" },
  { value: "FIRMADO_CONTRAPARTE", label: "Firmado Contraparte" },
  { value: "FIRMADO_GORE", label: "Firmado GORE" },
  { value: "EN_REVISION_JURIDICA", label: "En Revisión Jurídica" },
  { value: "EN_NEGOCIACION", label: "En Negociación" },
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

function formatCLP(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    return new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

const CGR_OPTIONS = [
  { value: "TOMADO_RAZON", label: "Toma razón" },
  { value: "REPRESENTADO", label: "Representado" },
  { value: "EXENTO", label: "Exento" },
  { value: "ENVIADO", label: "Enviado" },
  { value: "PENDIENTE", label: "Pendiente" },
  { value: "NO_APLICA", label: "No aplica" },
  { value: "EN_REVISION", label: "En revisión" },
];

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
  const [editState, setEditState] = useState("");
  const [editTotalAmount, setEditTotalAmount] = useState("");
  const [editValidTo, setEditValidTo] = useState("");
  const [editCgrOutcome, setEditCgrOutcome] = useState("");
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);

  const page = Number(searchParams.get("page") ?? "1");
  const state = searchParams.get("state") ?? "";
  const agreement_type = searchParams.get("agreement_type") ?? "";

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

    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsLoading(true);
    api
      .get<PaginatedResponse<ConvenioListItem>>(`/api/convenios?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, state, agreement_type]);

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
    if (!detail) return;
    setEditState(detail.state ?? "");
    setEditTotalAmount(String(detail.total_amount ?? ""));
    setEditValidTo(detail.valid_to ? detail.valid_to.slice(0, 10) : "");
    setEditCgrOutcome("");
    setEditError(null);
    setIsEditing(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId) return;
    setEditSubmitting(true);
    setEditError(null);
    const body: Record<string, unknown> = {};
    if (editState) body.state = editState;
    if (editTotalAmount) body.total_amount = parseFloat(editTotalAmount);
    if (editValidTo) body.valid_to = editValidTo;
    if (editCgrOutcome) body.cgr_outcome = editCgrOutcome;
    try {
      await api.patch(`/api/convenios/${selectedId}`, body);
      setIsEditing(false);
      setDetailLoading(true);
      api
        .get<ConvenioDetail>(`/api/convenios/${selectedId}`)
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
        return <span className="text-xs text-muted-foreground">{formatDate(r.valid_to)}</span>;
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
      <div>
        <h1 className="text-2xl font-bold">Convenios</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Gestión de convenios y cuotas de pago
        </p>
      </div>

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
                    <Select value={editState} onValueChange={setEditState}>
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue placeholder="Seleccione estado" />
                      </SelectTrigger>
                      <SelectContent>
                        {STATE_OPTIONS.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value} className="text-xs">
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
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
                        {CGR_OPTIONS.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value} className="text-xs">
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
                  <span className="font-mono text-xs">{detail.ipr_codigo_bip}</span>
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
              <div className="flex justify-between px-3 py-2">
                <span className="text-muted-foreground">Vigencia hasta</span>
                <span className={detail.days_to_expiry !== null && detail.days_to_expiry < 30 ? "text-red-600 font-medium" : ""}>
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
            {detail.installments.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="font-medium text-xs uppercase text-muted-foreground tracking-wide">
                    Cuotas ({detail.paid_installments}/{detail.installment_count} pagadas)
                  </p>
                </div>
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
