"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Download, TrendingUp, TrendingDown, Minus, X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PaginatedResponse, IPRListItem, DGIIndicator } from "@/types";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DOMAINS = [
  { id: "ipr", label: "IPR" },
  { id: "indicadores", label: "Indicadores" },
  { id: "presupuesto", label: "Presupuesto" },
  { id: "convenios", label: "Convenios" },
  { id: "organizaciones", label: "Organizaciones" },
  { id: "personas", label: "Personas" },
  { id: "territorio", label: "Territorio" },
  { id: "eventos", label: "Eventos" },
  { id: "rendiciones", label: "Rendiciones" },
] as const;

type DomainId = (typeof DOMAINS)[number]["id"];

const IPR_TYPE_OPTIONS = [
  { value: "INFRAESTRUCTURA", label: "Infraestructura" },
  { value: "EQUIPAMIENTO", label: "Equipamiento" },
  { value: "TRANSFERENCIA", label: "Transferencia" },
  { value: "PROGRAMA_SOCIAL", label: "Programa Social" },
  { value: "PROGRAMA_8PCT", label: "Programa 8%" },
  { value: "CONSERVACION", label: "Conservación" },
  { value: "ESTUDIO", label: "Estudio" },
];

const IPR_STATUS_OPTIONS = [
  { value: "EN_FORMULACION", label: "En Formulación" },
  { value: "EN_EJECUCION", label: "En Ejecución" },
  { value: "TERMINADO", label: "Terminado" },
  { value: "CERRADO", label: "Cerrado" },
];

const IPR_SECTOR_OPTIONS = [
  { value: "SPORTS", label: "Deportes" },
  { value: "CULTURE", label: "Cultura" },
  { value: "EDUCATION", label: "Educación" },
  { value: "HEALTH", label: "Salud" },
  { value: "INFRASTRUCTURE", label: "Infraestructura" },
];

const ALERT_LEVEL_OPTIONS = [
  { value: "CRITICO", label: "Crítico" },
  { value: "ALTO", label: "Alto" },
  { value: "ATENCION", label: "Atención" },
  { value: "INFO", label: "Info" },
];

const INDICATOR_DIMENSION_OPTIONS = [
  { value: "GESTION", label: "Gestión" },
  { value: "PRESUPUESTO", label: "Presupuesto" },
  { value: "PROCESO", label: "Proceso" },
  { value: "RESULTADO", label: "Resultado" },
  { value: "TD", label: "Transform. Digital" },
];

const INDICATOR_SIGNAL_OPTIONS = [
  { value: "VERDE", label: "Verde" },
  { value: "AMARILLO", label: "Amarillo" },
  { value: "ROJO", label: "Rojo" },
];

const alertLevelColors: Record<string, string> = {
  CRITICO: "bg-red-600 text-white",
  ALTO: "bg-orange-500 text-white",
  ATENCION: "bg-amber-400 text-white",
  INFO: "bg-blue-500 text-white",
};

const signalColors: Record<string, string> = {
  VERDE: "bg-green-600",
  AMARILLO: "bg-amber-400",
  ROJO: "bg-red-600",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatCurrency(value: number | null): string {
  if (value === null) return "-";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "-";
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

function TrendIcon({ trend }: { trend: "up" | "down" | "flat" | null }) {
  if (trend === "up") return <TrendingUp className="size-3 text-green-600 inline-block" />;
  if (trend === "down") return <TrendingDown className="size-3 text-red-600 inline-block" />;
  return <Minus className="size-3 text-muted-foreground inline-block" />;
}

function SignalDot({ signal }: { signal: "VERDE" | "AMARILLO" | "ROJO" | null }) {
  if (!signal) return <span className="inline-block size-2.5 rounded-full bg-gray-300" />;
  return (
    <span
      className={cn("inline-block size-2.5 rounded-full", signalColors[signal] ?? "bg-gray-300")}
      title={signal}
    />
  );
}

// ---------------------------------------------------------------------------
// Detail Panel: IPR
// ---------------------------------------------------------------------------

function IPRDetailPanel({ ipr, onClose }: { ipr: IPRListItem; onClose: () => void }) {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">{ipr.codigo_bip}</p>
          <h3 className="text-sm font-semibold leading-tight line-clamp-2">{ipr.name}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Tipo" value={ipr.ipr_type ?? "-"} />
          <Separator />
          <DetailRow
            label="Estado"
            value={<StatusBadge status={ipr.status ?? ""} size="sm" />}
          />
          <Separator />
          <DetailRow label="Sector" value={ipr.investment_sector ?? "-"} />
          <Separator />
          <DetailRow label="Fuente" value={ipr.funding_source ?? "-"} />
          <Separator />
          <DetailRow label="Ejecutor" value={ipr.executor_name ?? "-"} />
          <Separator />
          <DetailRow
            label="Presupuesto"
            value={
              <span className="font-mono tabular-nums text-xs">
                {formatCurrency(ipr.total_budget)}
              </span>
            }
          />
          <Separator />
          <DetailRow
            label="Alerta"
            value={
              ipr.alert_level ? (
                <Badge
                  className={cn(
                    "text-[10px] px-1.5 py-0",
                    alertLevelColors[ipr.alert_level] ?? "bg-gray-300"
                  )}
                >
                  {ipr.alert_level}
                </Badge>
              ) : (
                "-"
              )
            }
          />
          <Separator />
          <DetailRow
            label="Problemas"
            value={
              ipr.has_open_problems ? (
                <Badge variant="destructive" className="text-[10px] px-1.5 py-0">
                  Con problemas
                </Badge>
              ) : (
                <span className="text-muted-foreground text-xs">Sin problemas</span>
              )
            }
          />
        </div>
      </ScrollArea>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Detail Panel: Indicator
// ---------------------------------------------------------------------------

function IndicatorDetailPanel({
  indicator,
  onClose,
}: {
  indicator: DGIIndicator;
  onClose: () => void;
}) {
  const pct =
    indicator.current_value !== null && indicator.target_value && indicator.target_value > 0
      ? Math.min(100, Math.round((indicator.current_value / indicator.target_value) * 100))
      : null;

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground">{indicator.code}</p>
          <h3 className="text-sm font-semibold leading-tight">{indicator.name}</h3>
        </div>
        <Button variant="ghost" size="icon" className="size-7 shrink-0" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-4 py-3 space-y-3 text-sm">
          <DetailRow label="Dimensión" value={indicator.dimension} />
          <Separator />
          <DetailRow label="Unidad" value={indicator.unit} />
          <Separator />
          <DetailRow
            label="Valor actual"
            value={
              <span className="font-mono tabular-nums font-semibold text-base">
                {indicator.current_value !== null ? indicator.current_value : "-"}{" "}
                <span className="text-xs font-normal text-muted-foreground">{indicator.unit}</span>
              </span>
            }
          />
          <Separator />
          <DetailRow
            label="Meta"
            value={
              <span className="font-mono tabular-nums">
                {indicator.target_value !== null ? indicator.target_value : "-"}{" "}
                <span className="text-xs text-muted-foreground">{indicator.unit}</span>
              </span>
            }
          />
          {pct !== null && (
            <>
              <Separator />
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Avance</span>
                  <span className="font-mono">{pct}%</span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all",
                      pct >= 90
                        ? "bg-green-600"
                        : pct >= 60
                        ? "bg-amber-400"
                        : "bg-red-500"
                    )}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            </>
          )}
          <Separator />
          <DetailRow
            label="Señal"
            value={
              <div className="flex items-center gap-1.5">
                <SignalDot signal={indicator.signal} />
                <span>{indicator.signal ?? "-"}</span>
              </div>
            }
          />
          <Separator />
          <DetailRow
            label="Tendencia"
            value={
              <div className="flex items-center gap-1">
                <TrendIcon trend={indicator.trend} />
                <span className="text-xs capitalize">{indicator.trend ?? "-"}</span>
              </div>
            }
          />
          <Separator />
          <DetailRow
            label="Actualizado"
            value={formatDate(indicator.last_updated_at)}
          />
          {indicator.description && (
            <>
              <Separator />
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground font-medium">Descripción</p>
                <p className="text-xs leading-relaxed text-foreground/80">
                  {indicator.description}
                </p>
              </div>
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Shared helper component
// ---------------------------------------------------------------------------

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-start justify-between gap-2">
      <span className="text-xs text-muted-foreground shrink-0 w-24">{label}</span>
      <div className="text-xs text-right">{value}</div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Coming soon placeholder
// ---------------------------------------------------------------------------

function ComingSoon({ domain }: { domain: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-muted-foreground gap-2">
      <div className="size-12 rounded-full bg-muted flex items-center justify-center">
        <span className="text-2xl">📂</span>
      </div>
      <p className="text-sm font-medium">
        {domain} — Próximamente
      </p>
      <p className="text-xs max-w-xs text-center">
        Este explorador de datos está en construcción. Estará disponible en la próxima iteración.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function DatosPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Domain selection
  const domainParam = (searchParams.get("dominio") as DomainId) ?? "ipr";
  const activeDomain: DomainId = DOMAINS.find((d) => d.id === domainParam)?.id ?? "ipr";

  // Pagination + filters
  const page = Number(searchParams.get("page") ?? "1");
  const tipo = searchParams.get("tipo") ?? "";
  const estado = searchParams.get("estado") ?? "";
  const sector = searchParams.get("sector") ?? "";
  const alertLevel = searchParams.get("alert_level") ?? "";
  const search = searchParams.get("search") ?? "";
  const dimension = searchParams.get("dimension") ?? "";
  const signal = searchParams.get("signal") ?? "";

  // Data state
  const [iprData, setIprData] = useState<PaginatedResponse<IPRListItem> | null>(null);
  const [indicatorData, setIndicatorData] = useState<DGIIndicator[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Selection state
  const [selectedIPR, setSelectedIPR] = useState<IPRListItem | null>(null);
  const [selectedIndicator, setSelectedIndicator] = useState<DGIIndicator | null>(null);

  // URL helpers
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

  const handleDomainChange = (domain: DomainId) => {
    setSelectedIPR(null);
    setSelectedIndicator(null);
    router.push(`${pathname}?dominio=${domain}`);
  };

  const handleFilterChange = (key: string, value: string) => {
    router.push(buildUrl({ [key]: value, page: 1 }));
  };

  const handleSearchChange = (value: string) => {
    router.push(buildUrl({ search: value, page: 1 }));
  };

  const handleClear = () => {
    router.push(`${pathname}?dominio=${activeDomain}`);
  };

  const handlePageChange = (newPage: number) => {
    router.push(buildUrl({ page: newPage }));
  };

  // Fetch IPR data
  useEffect(() => {
    if (activeDomain !== "ipr") return;
    setIsLoading(true);
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "25");
    if (tipo) params.set("ipr_type", tipo);
    if (estado) params.set("status", estado);
    if (sector) params.set("sector", sector);
    if (alertLevel) params.set("alert_level", alertLevel);
    if (search) params.set("search", search);

    api
      .get<PaginatedResponse<IPRListItem>>(`/api/ipr?${params.toString()}`)
      .then(setIprData)
      .catch(() => setIprData(null))
      .finally(() => setIsLoading(false));
  }, [activeDomain, page, tipo, estado, sector, alertLevel, search]);

  // Fetch indicator data
  useEffect(() => {
    if (activeDomain !== "indicadores") return;
    setIsLoading(true);
    const params = new URLSearchParams();
    if (dimension) params.set("dimension", dimension);
    if (signal) params.set("signal", signal);
    if (search) params.set("search", search);

    api
      .get<DGIIndicator[]>(`/api/dgi/data/indicators?${params.toString()}`)
      .then(setIndicatorData)
      .catch(() => setIndicatorData(null))
      .finally(() => setIsLoading(false));
  }, [activeDomain, dimension, signal, search]);

  // Show toast for export (placeholder)
  const handleExport = () => {
    alert("Exportar CSV — Próximamente disponible");
  };

  // IPR columns
  const iprColumns = [
    {
      key: "alert_level",
      label: "",
      render: (value: unknown) => {
        const v = String(value ?? "");
        if (!v || v === "null") return <span className="inline-block size-2 rounded-full bg-transparent" />;
        return (
          <span
            className={cn("inline-block rounded-full size-2.5", alertLevelColors[v] ?? "bg-gray-300")}
            title={v}
          />
        );
      },
    },
    {
      key: "codigo_bip",
      label: "BIP",
      render: (value: unknown) => (
        <span className="text-[11px] font-mono text-muted-foreground">{String(value ?? "-")}</span>
      ),
    },
    {
      key: "name",
      label: "Nombre",
      render: (value: unknown) => (
        <span className="text-xs font-medium leading-snug line-clamp-2">{String(value ?? "")}</span>
      ),
    },
    {
      key: "ipr_type",
      label: "Tipo",
      render: (value: unknown) => (
        <Badge variant="outline" className="text-[10px] px-1.5 py-0 whitespace-nowrap">
          {String(value ?? "-")}
        </Badge>
      ),
    },
    {
      key: "status",
      label: "Estado",
      render: (value: unknown) => <StatusBadge status={String(value ?? "")} size="sm" />,
    },
    {
      key: "total_budget",
      label: "Presup.",
      render: (value: unknown) => (
        <span className="text-[11px] text-right tabular-nums font-mono">
          {formatCurrency(value as number | null)}
        </span>
      ),
    },
  ];

  // Indicator columns
  const indicatorColumns = [
    {
      key: "code",
      label: "Código",
      render: (value: unknown) => (
        <span className="text-[11px] font-mono text-muted-foreground">{String(value ?? "-")}</span>
      ),
    },
    {
      key: "name",
      label: "Nombre",
      render: (value: unknown) => (
        <span className="text-xs font-medium leading-snug">{String(value ?? "")}</span>
      ),
    },
    {
      key: "dimension",
      label: "Dimensión",
      render: (value: unknown) => (
        <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
          {String(value ?? "-")}
        </Badge>
      ),
    },
    {
      key: "current_value",
      label: "Valor",
      render: (value: unknown, row: unknown) => {
        const ind = row as DGIIndicator;
        return (
          <span className="text-xs font-mono tabular-nums">
            {value !== null ? String(value) : "-"}
            {ind.unit ? <span className="text-muted-foreground ml-0.5">{ind.unit}</span> : null}
          </span>
        );
      },
    },
    {
      key: "target_value",
      label: "Meta",
      render: (value: unknown, row: unknown) => {
        const ind = row as DGIIndicator;
        return (
          <span className="text-xs font-mono tabular-nums text-muted-foreground">
            {value !== null ? String(value) : "-"}
            {ind.unit ? <span className="ml-0.5">{ind.unit}</span> : null}
          </span>
        );
      },
    },
    {
      key: "signal",
      label: "Señal",
      render: (value: unknown, row: unknown) => {
        const ind = row as DGIIndicator;
        return (
          <div className="flex items-center gap-1.5">
            <SignalDot signal={ind.signal} />
            <TrendIcon trend={ind.trend} />
          </div>
        );
      },
    },
  ];

  // Indicator table data (pagination simulated client-side)
  const PAGE_SIZE = 25;
  const indicatorItems = indicatorData ?? [];
  const filteredIndicators = indicatorItems.filter((ind) => {
    if (dimension && ind.dimension !== dimension) return false;
    if (signal && ind.signal !== signal) return false;
    if (search) {
      const q = search.toLowerCase();
      return ind.name.toLowerCase().includes(q) || ind.code.toLowerCase().includes(q);
    }
    return true;
  });
  const indTotal = filteredIndicators.length;
  const indTotalPages = Math.max(1, Math.ceil(indTotal / PAGE_SIZE));
  const indPage = Math.min(page, indTotalPages);
  const indSlice = filteredIndicators.slice((indPage - 1) * PAGE_SIZE, indPage * PAGE_SIZE);

  const hasDetailPanel = selectedIPR !== null || selectedIndicator !== null;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-5 py-3 border-b flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-lg font-bold leading-tight">Explorador de Datos</h1>
          <p className="text-[11px] text-muted-foreground mt-0.5">
            Acceso analítico a los dominios de datos de GORE Ñuble
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="h-8 text-xs gap-1.5"
          onClick={handleExport}
        >
          <Download className="size-3.5" />
          Exportar CSV
        </Button>
      </div>

      {/* Body: 3-panel layout */}
      <div
        className={cn(
          "flex-1 overflow-hidden grid",
          hasDetailPanel
            ? "grid-cols-[200px_1fr_340px]"
            : "grid-cols-[200px_1fr]"
        )}
      >
        {/* Left: Domain sidebar */}
        <aside className="border-r bg-muted/20 overflow-y-auto">
          <div className="py-2">
            <p className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Dominios
            </p>
            {DOMAINS.map((domain) => (
              <button
                key={domain.id}
                onClick={() => handleDomainChange(domain.id)}
                className={cn(
                  "w-full text-left px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
                  activeDomain === domain.id
                    ? "bg-accent text-accent-foreground font-medium"
                    : "text-muted-foreground"
                )}
              >
                {domain.label}
                {domain.id !== "ipr" && domain.id !== "indicadores" && (
                  <span className="ml-1.5 text-[9px] text-muted-foreground/60 uppercase tracking-wide">
                    soon
                  </span>
                )}
              </button>
            ))}
          </div>
        </aside>

        {/* Center: Data table */}
        <div className="overflow-auto flex flex-col">
          {activeDomain === "ipr" && (
            <div className="flex flex-col h-full">
              <div className="px-4 pt-3 pb-2 border-b shrink-0">
                <FilterBar
                  filters={[
                    { key: "tipo", label: "Tipo", options: IPR_TYPE_OPTIONS },
                    { key: "estado", label: "Estado", options: IPR_STATUS_OPTIONS },
                    { key: "sector", label: "Sector", options: IPR_SECTOR_OPTIONS },
                    { key: "alert_level", label: "Alerta", options: ALERT_LEVEL_OPTIONS },
                  ]}
                  values={{ tipo, estado, sector, alert_level: alertLevel }}
                  onChange={handleFilterChange}
                  onClear={handleClear}
                  searchPlaceholder="Buscar por nombre o BIP..."
                  searchValue={search}
                  onSearchChange={handleSearchChange}
                />
              </div>
              <div className="px-4 py-3 flex-1 overflow-auto">
                <DataTable
                  columns={iprColumns}
                  data={iprData?.items ?? []}
                  page={page}
                  totalPages={iprData?.total_pages ?? 1}
                  total={iprData?.total ?? 0}
                  onPageChange={handlePageChange}
                  onRowClick={(row) => {
                    setSelectedIPR(row as IPRListItem);
                    setSelectedIndicator(null);
                  }}
                  isLoading={isLoading}
                />
              </div>
            </div>
          )}

          {activeDomain === "indicadores" && (
            <div className="flex flex-col h-full">
              <div className="px-4 pt-3 pb-2 border-b shrink-0">
                <FilterBar
                  filters={[
                    { key: "dimension", label: "Dimensión", options: INDICATOR_DIMENSION_OPTIONS },
                    { key: "signal", label: "Señal", options: INDICATOR_SIGNAL_OPTIONS },
                  ]}
                  values={{ dimension, signal }}
                  onChange={handleFilterChange}
                  onClear={handleClear}
                  searchPlaceholder="Buscar indicador..."
                  searchValue={search}
                  onSearchChange={handleSearchChange}
                />
              </div>
              <div className="px-4 py-3 flex-1 overflow-auto">
                <DataTable
                  columns={indicatorColumns}
                  data={indSlice}
                  page={indPage}
                  totalPages={indTotalPages}
                  total={indTotal}
                  onPageChange={handlePageChange}
                  onRowClick={(row) => {
                    setSelectedIndicator(row as DGIIndicator);
                    setSelectedIPR(null);
                  }}
                  isLoading={isLoading}
                />
              </div>
            </div>
          )}

          {activeDomain !== "ipr" && activeDomain !== "indicadores" && (
            <div className="flex-1 flex items-center justify-center">
              <ComingSoon
                domain={DOMAINS.find((d) => d.id === activeDomain)?.label ?? activeDomain}
              />
            </div>
          )}
        </div>

        {/* Right: Detail panel */}
        {hasDetailPanel && (
          <div className="border-l bg-background overflow-hidden flex flex-col">
            {selectedIPR && (
              <IPRDetailPanel
                ipr={selectedIPR}
                onClose={() => setSelectedIPR(null)}
              />
            )}
            {selectedIndicator && (
              <IndicatorDetailPanel
                indicator={selectedIndicator}
                onClose={() => setSelectedIndicator(null)}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
