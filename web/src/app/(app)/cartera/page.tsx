"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { formatCLP, formatDate } from "@/lib/format";
import { exportCSV } from "@/lib/csv-export";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Download, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import type {
  PaginatedResponse,
  CarteraIPRItem,
  CarteraSummary,
  CuotaVencidaItem,
  HealthSignal,
  CategoryRef,
} from "@/types";

// ---------------------------------------------------------------------------
// Signal colors
// ---------------------------------------------------------------------------
const signalDot: Record<HealthSignal, string> = {
  VERDE: "bg-green-500",
  AMARILLO: "bg-amber-500",
  ROJO: "bg-red-500",
};

// ---------------------------------------------------------------------------
// CSV column defs
// ---------------------------------------------------------------------------
const CSV_COLUMNS = [
  { key: "health_signal", label: "Señal" },
  { key: "codigo_bip", label: "BIP" },
  { key: "name", label: "Nombre" },
  { key: "mechanism", label: "Mecanismo" },
  { key: "mcd_phase", label: "Fase" },
  { key: "physical_progress", label: "Av. Físico %" },
  { key: "financial_progress", label: "Av. Financiero %" },
  { key: "agreement_count", label: "Convenios" },
  { key: "overdue_installments", label: "Cuotas Vencidas" },
  { key: "active_alerts", label: "Alertas" },
  { key: "open_problems", label: "Problemas" },
  { key: "overdue_commitments", label: "Comp. Vencidos" },
];

const CSV_CUOTAS = [
  { key: "ipr_codigo_bip", label: "BIP" },
  { key: "agreement_number", label: "Convenio" },
  { key: "counterpart_name", label: "Contraparte" },
  { key: "installment_number", label: "Cuota N°" },
  { key: "amount", label: "Monto" },
  { key: "due_date", label: "Vencimiento" },
  { key: "days_overdue", label: "Días Atraso" },
];

// ---------------------------------------------------------------------------
// Phase options
// ---------------------------------------------------------------------------
const PHASE_OPTIONS = [
  { value: "F0", label: "F0" },
  { value: "F1", label: "F1" },
  { value: "F2", label: "F2" },
  { value: "F3", label: "F3" },
  { value: "F4", label: "F4" },
  { value: "F5", label: "F5" },
];

const SIGNAL_OPTIONS: { value: HealthSignal; label: string }[] = [
  { value: "ROJO", label: "Rojo" },
  { value: "AMARILLO", label: "Amarillo" },
  { value: "VERDE", label: "Verde" },
];

// ---------------------------------------------------------------------------
// Progress bar inline component
// ---------------------------------------------------------------------------
function ProgressBar({ value }: { value: number | null }) {
  if (value === null || value === undefined) return <span className="text-xs text-muted-foreground">-</span>;
  const pct = Math.min(Math.max(value, 0), 100);
  return (
    <div className="flex items-center gap-1.5">
      <div className="h-2 w-16 rounded-full bg-gray-200 overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all",
            pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-amber-500" : "bg-red-500"
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs tabular-nums font-mono">{pct.toFixed(0)}%</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Signal dot with tooltip
// ---------------------------------------------------------------------------
function SignalDot({ signal, reasons }: { signal: HealthSignal; reasons: string[] }) {
  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className={cn("inline-block h-3 w-3 rounded-full shrink-0", signalDot[signal])} />
        </TooltipTrigger>
        {reasons.length > 0 && (
          <TooltipContent side="right" className="max-w-xs">
            <ul className="text-xs space-y-0.5">
              {reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </TooltipContent>
        )}
      </Tooltip>
    </TooltipProvider>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------
export default function CarteraPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Filters from URL
  const initialSignal = searchParams.get("health_signal") as HealthSignal | null;

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [divisionId, setDivisionId] = useState<string>("");
  const [mechanism, setMechanism] = useState<string>("");
  const [phase, setPhase] = useState<string>("");
  const [signal, setSignal] = useState<string>(initialSignal || "");

  const [data, setData] = useState<PaginatedResponse<CarteraIPRItem> | null>(null);
  const [summary, setSummary] = useState<CarteraSummary | null>(null);
  const [cuotas, setCuotas] = useState<PaginatedResponse<CuotaVencidaItem> | null>(null);
  const [cuotasPage, setCuotasPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [loadingCuotas, setLoadingCuotas] = useState(false);
  const [divisions, setDivisions] = useState<CategoryRef[]>([]);
  const [mechanisms, setMechanisms] = useState<CategoryRef[]>([]);
  const [tab, setTab] = useState("cartera");

  // Load catalog data
  useEffect(() => {
    api.get<CategoryRef[]>("/api/catalogs/divisions").then(setDivisions).catch(() => {});
    api.get<CategoryRef[]>("/api/catalogs/categories/mechanism").then(setMechanisms).catch(() => {});
  }, []);

  // Fetch cartera + summary
  const fetchCartera = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), page_size: "20" });
      if (search) params.set("search", search);
      if (divisionId) params.set("division_id", divisionId);
      if (mechanism) params.set("mechanism", mechanism);
      if (phase) params.set("mcd_phase", phase);
      if (signal) params.set("health_signal", signal);

      const summaryParams = new URLSearchParams();
      if (search) summaryParams.set("search", search);
      if (divisionId) summaryParams.set("division_id", divisionId);
      if (mechanism) summaryParams.set("mechanism", mechanism);
      if (phase) summaryParams.set("mcd_phase", phase);

      const [carteraRes, summaryRes] = await Promise.all([
        api.get<PaginatedResponse<CarteraIPRItem>>(`/api/dgi/cartera?${params}`),
        api.get<CarteraSummary>(`/api/dgi/cartera/resumen?${summaryParams}`),
      ]);
      setData(carteraRes);
      setSummary(summaryRes);
    } catch {
      // error handled by ApiClient
    } finally {
      setLoading(false);
    }
  }, [page, search, divisionId, mechanism, phase, signal]);

  useEffect(() => { fetchCartera(); }, [fetchCartera]);

  // Fetch cuotas when tab changes
  const fetchCuotas = useCallback(async () => {
    setLoadingCuotas(true);
    try {
      const params = new URLSearchParams({ page: String(cuotasPage), page_size: "20" });
      if (divisionId) params.set("division_id", divisionId);
      const res = await api.get<PaginatedResponse<CuotaVencidaItem>>(`/api/dgi/cartera/cuotas-vencidas?${params}`);
      setCuotas(res);
    } catch {
      // handled
    } finally {
      setLoadingCuotas(false);
    }
  }, [cuotasPage, divisionId]);

  useEffect(() => {
    if (tab === "cuotas") fetchCuotas();
  }, [tab, fetchCuotas]);

  // Reset page on filter change
  useEffect(() => { setPage(1); }, [search, divisionId, mechanism, phase, signal]);

  // Debounce search
  const [searchInput, setSearchInput] = useState("");
  useEffect(() => {
    const t = setTimeout(() => setSearch(searchInput), 300);
    return () => clearTimeout(t);
  }, [searchInput]);

  // DataTable columns for cartera
  const columns = [
    {
      key: "health_signal",
      label: "",
      render: (_: unknown, row: unknown) => {
        const r = row as CarteraIPRItem;
        return <SignalDot signal={r.health_signal} reasons={r.health_reasons} />;
      },
    },
    {
      key: "codigo_bip",
      label: "BIP",
      render: (v: unknown) => (
        <span className="font-mono text-xs">{String(v)}</span>
      ),
    },
    {
      key: "name",
      label: "Nombre",
      render: (v: unknown) => (
        <span className="text-sm max-w-[200px] truncate block">{String(v)}</span>
      ),
    },
    {
      key: "mechanism",
      label: "Mecanismo",
      render: (v: unknown) => v ? <Badge variant="outline" className="text-[10px]">{String(v)}</Badge> : <span className="text-muted-foreground">-</span>,
    },
    {
      key: "mcd_phase",
      label: "Fase",
      render: (v: unknown) => v ? <Badge className="bg-blue-100 text-blue-700 border-blue-300 text-[10px]">{String(v)}</Badge> : "-",
    },
    {
      key: "physical_progress",
      label: "Av. Físico",
      className: "hidden md:table-cell",
      render: (v: unknown) => <ProgressBar value={v as number | null} />,
    },
    {
      key: "financial_progress",
      label: "Av. Financiero",
      className: "hidden md:table-cell",
      render: (v: unknown) => <ProgressBar value={v as number | null} />,
    },
    {
      key: "agreement_count",
      label: "Convenios",
      render: (_: unknown, row: unknown) => {
        const r = row as CarteraIPRItem;
        if (r.agreement_count === 0) return <span className="text-muted-foreground">0</span>;
        return (
          <span className="text-xs">
            {r.agreement_count} <span className="text-muted-foreground">({r.agreement_latest_state || "-"})</span>
          </span>
        );
      },
    },
    {
      key: "overdue_installments",
      label: "Cuotas V.",
      render: (v: unknown) => {
        const n = v as number;
        return n > 0
          ? <span className="text-xs font-semibold text-red-600">{n}</span>
          : <span className="text-muted-foreground">0</span>;
      },
    },
    {
      key: "active_alerts",
      label: "Alertas",
      render: (_: unknown, row: unknown) => {
        const r = row as CarteraIPRItem;
        if (r.active_alerts === 0) return <span className="text-muted-foreground">0</span>;
        return (
          <span className="text-xs">
            {r.active_alerts}
            {r.critical_alerts > 0 && (
              <span className="text-red-600 ml-0.5">({r.critical_alerts}!)</span>
            )}
          </span>
        );
      },
    },
  ];

  // DataTable columns for cuotas vencidas
  const cuotasColumns = [
    {
      key: "ipr_codigo_bip",
      label: "BIP",
      render: (v: unknown) => (
        <span className="font-mono text-xs">{v ? String(v) : "-"}</span>
      ),
    },
    { key: "agreement_number", label: "Convenio" },
    { key: "counterpart_name", label: "Contraparte" },
    { key: "installment_number", label: "Cuota N°" },
    {
      key: "amount",
      label: "Monto",
      render: (v: unknown) => <span className="font-mono text-xs">{formatCLP(v as number)}</span>,
    },
    {
      key: "due_date",
      label: "Vencimiento",
      render: (v: unknown) => formatDate(v as string),
    },
    {
      key: "days_overdue",
      label: "Días Atraso",
      render: (v: unknown) => {
        const n = v as number;
        return (
          <Badge variant="outline" className={cn("text-xs", n > 30 ? "border-red-400 text-red-600" : "border-amber-400 text-amber-600")}>
            {n}d
          </Badge>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Control de Cartera IPR"
        description="Vista unificada del portafolio de inversiones"
        actions={
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              exportCSV(
                tab === "cuotas" ? CSV_CUOTAS : CSV_COLUMNS,
                tab === "cuotas" ? (cuotas?.items ?? []) : (data?.items ?? []),
                tab === "cuotas" ? "cuotas-vencidas" : "cartera-ipr"
              )
            }
          >
            <Download className="size-4 mr-1" />CSV
          </Button>
        }
      />

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* Signal cards */}
          <Card
            className={cn("cursor-pointer transition-all hover:shadow-md", signal === "VERDE" && "ring-2 ring-green-500")}
            onClick={() => { setSignal(signal === "VERDE" ? "" : "VERDE"); setTab("cartera"); }}
          >
            <CardContent className="px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="inline-block h-3 w-3 rounded-full bg-green-500" />
                <span className="text-xs text-muted-foreground">Verde</span>
              </div>
              <p className="text-2xl font-bold mt-1">{summary.verde}</p>
            </CardContent>
          </Card>
          <Card
            className={cn("cursor-pointer transition-all hover:shadow-md", signal === "AMARILLO" && "ring-2 ring-amber-500")}
            onClick={() => { setSignal(signal === "AMARILLO" ? "" : "AMARILLO"); setTab("cartera"); }}
          >
            <CardContent className="px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="inline-block h-3 w-3 rounded-full bg-amber-500" />
                <span className="text-xs text-muted-foreground">Amarillo</span>
              </div>
              <p className="text-2xl font-bold mt-1">{summary.amarillo}</p>
            </CardContent>
          </Card>
          <Card
            className={cn("cursor-pointer transition-all hover:shadow-md", signal === "ROJO" && "ring-2 ring-red-500")}
            onClick={() => { setSignal(signal === "ROJO" ? "" : "ROJO"); setTab("cartera"); }}
          >
            <CardContent className="px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="inline-block h-3 w-3 rounded-full bg-red-500" />
                <span className="text-xs text-muted-foreground">Rojo</span>
              </div>
              <p className="text-2xl font-bold mt-1">{summary.rojo}</p>
            </CardContent>
          </Card>

          {/* Metric cards */}
          <Card>
            <CardContent className="px-4 py-3">
              <div className="flex items-center gap-1.5">
                <AlertTriangle className="size-3.5 text-amber-600" />
                <span className="text-xs text-muted-foreground">Cuotas Vencidas</span>
              </div>
              <p className="text-2xl font-bold mt-1">{summary.overdue_installments_total}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="px-4 py-3">
              <span className="text-xs text-muted-foreground">Pendientes CGR</span>
              <p className="text-2xl font-bold mt-1">{summary.pending_cgr_total}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="px-4 py-3">
              <span className="text-xs text-muted-foreground">Monto Total</span>
              <p className="text-lg font-bold font-mono mt-1">{formatCLP(summary.monto_total)}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="cartera">Cartera IPR</TabsTrigger>
          <TabsTrigger value="cuotas">Cuotas Vencidas</TabsTrigger>
        </TabsList>

        {/* Tab: Cartera IPR */}
        <TabsContent value="cartera" className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            <Input
              placeholder="Buscar BIP o nombre..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-56"
            />
            <Select value={divisionId} onValueChange={(v) => setDivisionId(v === "ALL" ? "" : v)}>
              <SelectTrigger className="w-44">
                <SelectValue placeholder="División" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todas</SelectItem>
                {divisions.map((d) => (
                  <SelectItem key={d.id} value={d.id}>{d.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={mechanism} onValueChange={(v) => setMechanism(v === "ALL" ? "" : v)}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Mecanismo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                {mechanisms.map((m) => (
                  <SelectItem key={m.id} value={m.code}>{m.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={phase} onValueChange={(v) => setPhase(v === "ALL" ? "" : v)}>
              <SelectTrigger className="w-28">
                <SelectValue placeholder="Fase" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todas</SelectItem>
                {PHASE_OPTIONS.map((p) => (
                  <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={signal} onValueChange={(v) => setSignal(v === "ALL" ? "" : v)}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Señal" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todas</SelectItem>
                {SIGNAL_OPTIONS.map((s) => (
                  <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="overflow-x-auto">
            <DataTable
              columns={columns}
              data={data?.items ?? []}
              page={data?.page ?? 1}
              totalPages={data?.total_pages ?? 1}
              total={data?.total ?? 0}
              onPageChange={setPage}
              onRowClick={(row) => router.push(`/ipr/${(row as CarteraIPRItem).id}`)}
              isLoading={loading}
            />
          </div>
        </TabsContent>

        {/* Tab: Cuotas Vencidas */}
        <TabsContent value="cuotas" className="space-y-4">
          <DataTable
            columns={cuotasColumns}
            data={cuotas?.items ?? []}
            page={cuotas?.page ?? 1}
            totalPages={cuotas?.total_pages ?? 1}
            total={cuotas?.total ?? 0}
            onPageChange={setCuotasPage}
            onRowClick={(row) => {
              const r = row as CuotaVencidaItem;
              if (r.ipr_id) router.push(`/ipr/${r.ipr_id}`);
            }}
            isLoading={loadingCuotas}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
