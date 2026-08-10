"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { StatusBadge } from "@/components/status-badge";
import { EmptyState } from "@/components/empty-state";
import { Clickable } from "@/components/clickable";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Download, AlertTriangle, RotateCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { exportCSV } from "@/lib/csv-export";
import { formatCurrency } from "@/lib/format";
import { PageHeader } from "@/components/page-header";
import { MechanismBadge, PhaseBadge } from "./components/ipr-badges";
import type { PaginatedResponse, IPRListItem } from "@/types";
import { SECTOR_OPTIONS } from "./components/ipr-constants";

const CSV_COLUMNS = [
  { key: "codigo_bip", label: "Código BIP" },
  { key: "name", label: "Nombre" },
  { key: "ipr_type", label: "Tipo" },
  { key: "status", label: "Estado" },
  { key: "investment_sector", label: "Sector" },
  { key: "executor_name", label: "Ejecutor" },
];

const IPR_TYPE_OPTIONS = [
  { value: "INFRAESTRUCTURA", label: "Infraestructura" },
  { value: "EQUIPAMIENTO", label: "Equipamiento" },
  { value: "TRANSFERENCIA", label: "Transferencia" },
  { value: "PROGRAMA_SOCIAL", label: "Programa Social" },
  { value: "PROGRAMA_8PCT", label: "Programa 8%" },
  { value: "CONSERVACION", label: "Conservación" },
  { value: "ESTUDIO", label: "Estudio" },
];

const STATUS_OPTIONS = [
  // F0
  { value: "INGRESADO", label: "F0 · Ingresado" },
  // F1
  { value: "EN_REVISION", label: "F1 · En Revisión" },
  { value: "PRE_ADMISIBLE", label: "F1 · Pre-Admisible" },
  { value: "ADMISIBLE", label: "F1 · Admisible" },
  { value: "INADMISIBLE", label: "F1 · Inadmisible" },
  // F2
  { value: "EN_EVALUACION", label: "F2 · En Evaluación" },
  { value: "RS", label: "F2 · RS" },
  { value: "FI", label: "F2 · FI" },
  { value: "FC", label: "F2 · FC" },
  { value: "OT", label: "F2 · OT" },
  { value: "AD", label: "F2 · AD" },
  { value: "RF", label: "F2 · RF" },
  { value: "ITF", label: "F2 · ITF" },
  { value: "AT", label: "F2 · AT" },
  // F3
  { value: "CDP_EMITIDO", label: "F3 · CDP Emitido" },
  // F4
  { value: "EN_FORMALIZACION", label: "F4 · En Formalización" },
  { value: "FORMALIZADO", label: "F4 · Formalizado" },
  { value: "EN_LICITACION", label: "F4 · En Licitación" },
  { value: "ADJUDICADO", label: "F4 · Adjudicado" },
  { value: "CONTRATO_FIRMADO", label: "F4 · Contrato Firmado" },
  { value: "EN_EJECUCION", label: "F4 · En Ejecución" },
  { value: "EN_OBRA", label: "F4 · En Obra" },
  { value: "RECEPCION_PROVISORIA", label: "F4 · Recepción Provisoria" },
  { value: "RECEPCION_DEFINITIVA", label: "F4 · Recepción Definitiva" },
  { value: "SUSPENDIDO", label: "F4 · Suspendido" },
  // F5
  { value: "EN_RENDICION", label: "F5 · En Rendición" },
  { value: "RENDICION_APROBADA", label: "F5 · Rendición Aprobada" },
  { value: "EN_CIERRE_ADMINISTRATIVO", label: "F5 · En Cierre Administrativo" },
  { value: "CERRADO", label: "F5 · Cerrado" },
  // Terminales
  { value: "ANULADO", label: "Anulado" },
  { value: "TERMINADO_ANTICIPADAMENTE", label: "Terminado Anticipadamente" },
];

const ALERT_LEVEL_OPTIONS = [
  { value: "CRITICO", label: "Crítico" },
  { value: "ALTO", label: "Alto" },
  { value: "ATENCION", label: "Atención" },
  { value: "INFO", label: "Info" },
];

const MECHANISM_OPTIONS = [
  { value: "SNI", label: "SNI General" },
  { value: "C33", label: "Circular 33" },
  { value: "FRIL", label: "FRIL" },
  { value: "GLOSA06", label: "Glosa 06" },
  { value: "TRANSFER", label: "Transferencias" },
  { value: "SUBV8", label: "Subvención 8%" },
  { value: "FRPD", label: "FRPD Royalty" },
];

const MCD_PHASE_OPTIONS = [
  { value: "F0", label: "F0 Formulación" },
  { value: "F1", label: "F1 Admisibilidad" },
  { value: "F2", label: "F2 Evaluación" },
  { value: "F3", label: "F3 Priorización" },
  { value: "F4", label: "F4 Ejecución" },
  { value: "F5", label: "F5 Cierre" },
];

// === Lookup maps: code → label (derived from filter options) ===
const iprTypeLabel: Record<string, string> = Object.fromEntries(IPR_TYPE_OPTIONS.map(o => [o.value, o.label]));
const mechanismLabel: Record<string, string> = Object.fromEntries(MECHANISM_OPTIONS.map(o => [o.value, o.label]));
const phaseLabel: Record<string, string> = Object.fromEntries(MCD_PHASE_OPTIONS.map(o => [o.value, o.label]));

const alertLevelColors: Record<string, string> = {
  CRITICO: "bg-red-600 text-white",
  ALTO: "bg-orange-500 text-white",
  ATENCION: "bg-amber-400 text-white",
  INFO: "bg-blue-500 text-white",
};

export default function IprPage() {
  const [referenceTime] = useState(Date.now);
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const canCreate = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"].includes(user.role_code);

  // Role awareness
  const role = user?.role_code;
  const isJefe = role && ["JEFE_DIVISION", "JEFE_DEPARTAMENTO"].includes(role);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const didAutoScope = useRef(false);

  const [data, setData] = useState<PaginatedResponse<IPRListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [divisionOptions, setDivisionOptions] = useState<{value: string; label: string}[]>([]);

  const page = Number(searchParams.get("page") ?? "1");
  const tipo = searchParams.get("tipo") ?? "";
  const estado = searchParams.get("estado") ?? "";
  const sector = searchParams.get("sector") ?? "";
  const alertLevel = searchParams.get("alert_level") ?? "";
  const mechanism = searchParams.get("mechanism") ?? "";
  const mcdPhase = searchParams.get("mcd_phase") ?? "";
  const division = searchParams.get("division") ?? "";
  const search = searchParams.get("search") ?? "";

  const filterValues: Record<string, string> = {
    tipo,
    estado,
    sector,
    alert_level: alertLevel,
    mechanism,
    mcd_phase: mcdPhase,
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

  const handleSearchChange = (value: string) => {
    router.push(buildUrl({ search: value, page: 1 }));
  };

  const handleClear = () => {
    router.push(pathname);
  };

  const hasActiveFilters =
    !!(tipo || estado || sector || alertLevel || mechanism || mcdPhase || division || search);

  const handleRetry = () => setReloadKey((k) => k + 1);

  const handlePageChange = (newPage: number) => {
    router.push(buildUrl({ page: newPage }));
  };

  useEffect(() => {
    api
      .get<{id: string; code: string; name: string}[]>("/api/catalogs/divisions")
      .then((items) => {
        setDivisionOptions(items.map((d) => ({ value: d.id, label: d.name })));
      })
      .catch(() => {});
  }, []);

  // Auto-scope: JEFE gets division pre-selected
  useEffect(() => {
    if (didAutoScope.current) return;
    if (isJefe && !searchParams.has("division") && user?.division_id) {
      didAutoScope.current = true;
      const params = new URLSearchParams(searchParams.toString());
      params.set("division", user.division_id);
      router.replace(`${pathname}?${params.toString()}`);
    }
  }, [isJefe, user?.division_id, searchParams, pathname, router]);

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (tipo) params.set("ipr_type", tipo);
    if (estado) params.set("status", estado);
    if (sector) params.set("sector", sector);
    if (alertLevel) params.set("alert_level", alertLevel);
    if (mechanism) params.set("mechanism", mechanism);
    if (mcdPhase) params.set("mcd_phase", mcdPhase);
    if (division) params.set("sponsor_division_id", division);
    if (search) params.set("search", search);

    queueMicrotask(() => {
      if (active) {
        setIsLoading(true);
        setLoadError(null);
      }
    });

    api
      .get<PaginatedResponse<IPRListItem>>(`/api/ipr?${params.toString()}`)
      .then((response) => {
        if (active) setData(response);
      })
      .catch((err) => {
        if (active) {
          setData(null);
          setLoadError(err instanceof Error ? err.message : "No se pudieron cargar las IPR.");
        }
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [page, tipo, estado, sector, alertLevel, mechanism, mcdPhase, division, search, reloadKey]);

  const columns = [
    {
      key: "alert_level",
      label: "Alerta",
      render: (value: unknown) => {
        const v = String(value ?? "");
        if (!v) return null;
        return (
          <span
            className={`inline-block rounded-full size-3 ${alertLevelColors[v] ?? "bg-gray-300"}`}
            title={v}
          />
        );
      },
    },
    {
      key: "codigo_bip",
      label: "BIP",
      render: (value: unknown) => (
        <span className="text-xs font-mono">{String(value ?? "-")}</span>
      ),
    },
    {
      key: "name",
      label: "Nombre",
      render: (value: unknown) => (
        <span className="font-medium">{String(value ?? "")}</span>
      ),
    },
    {
      key: "ipr_type",
      label: "Tipo",
      render: (value: unknown) => {
        const v = String(value ?? "");
        return (
          <Badge variant="outline" className="text-xs">
            {iprTypeLabel[v] ?? (v || "-")}
          </Badge>
        );
      },
    },
    {
      key: "mechanism",
      label: "Mecanismo",
      render: (value: unknown) => {
        const v = String(value ?? "");
        if (!v) return <span className="text-muted-foreground text-xs">—</span>;
        return <MechanismBadge code={v} label={mechanismLabel[v] ?? v} />;
      },
    },
    {
      key: "mcd_phase",
      label: "Fase",
      render: (value: unknown) => {
        const v = String(value ?? "");
        if (!v) return <span className="text-muted-foreground text-xs">—</span>;
        return <PhaseBadge code={v} label={phaseLabel[v] ?? v} />;
      },
    },
    {
      key: "status",
      label: "Estado",
      render: (value: unknown) => <StatusBadge status={String(value ?? "")} size="sm" />,
    },
    {
      key: "actor_role",
      label: "Actor",
      render: (value: unknown, row: unknown) => {
        const role = String(value ?? "");
        if (!role) return <span className="text-muted-foreground text-xs">—</span>;
        const action = (row as Record<string, unknown>).actor_action as string | null;
        return (
          <div className="text-xs leading-tight" title={action ?? undefined}>
            <span>{role}</span>
            {action && (
              <span className="block text-[10px] text-muted-foreground truncate max-w-[120px]">{action}</span>
            )}
          </div>
        );
      },
    },
    {
      key: "phase_entered_at",
      label: "Días",
      render: (value: unknown) => {
        if (!value) return <span className="text-muted-foreground text-xs">—</span>;
        const entered = new Date(String(value));
        const days = Math.floor((Date.now() - entered.getTime()) / 86400000);
        const color = days > 90 ? "text-red-600" : days > 30 ? "text-amber-600" : "text-green-600";
        return (
          <span className={cn("text-xs tabular-nums font-medium", color)} title={`En fase desde ${entered.toLocaleDateString("es-CL")}`}>
            {days}d
          </span>
        );
      },
    },
    {
      key: "total_budget",
      label: "$",
      render: (value: unknown) => (
        <span className="text-xs text-right tabular-nums">
          {formatCurrency(value as number | null)}
        </span>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="IPR"
        description={
          isJefe
            ? "IPRs de tu división"
            : role === "ANALISTA"
              ? "IPRs en formulación"
              : "Intervenciones Públicas Regionales"
        }
        accentColor="indigo"
        actions={
          <>
            <Button variant="outline" size="sm" onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "ipr")}>
              <Download className="size-4 mr-1" />CSV
            </Button>
            {canCreate && (
              <Button onClick={() => router.push("/ipr/nuevo")} size="sm">
                <Plus className="size-4 mr-1" />
                Nueva IPR
              </Button>
            )}
          </>
        }
      />

      {/* Context strip */}
      {data && !isLoading && (
        <div className="flex items-center gap-2 text-sm">
          <span className="tabular-nums font-medium">{data.total}</span>
          <span className="text-muted-foreground">
            {isJefe ? "IPRs en tu división" : "IPRs en portafolio"}
          </span>
        </div>
      )}

      <FilterBar
        filters={[
          { key: "tipo", label: "Tipo", options: IPR_TYPE_OPTIONS },
          { key: "estado", label: "Estado", options: STATUS_OPTIONS },
          { key: "mcd_phase", label: "Fase", options: MCD_PHASE_OPTIONS },
          { key: "division", label: "División", options: divisionOptions },
          ...(showAdvanced || !!(sector || mechanism || alertLevel)
            ? [
                { key: "sector", label: "Sector", options: SECTOR_OPTIONS },
                { key: "mechanism", label: "Mecanismo", options: MECHANISM_OPTIONS },
                { key: "alert_level", label: "Alerta", options: ALERT_LEVEL_OPTIONS },
              ]
            : []),
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar por nombre o BIP..."
        searchValue={search}
        onSearchChange={handleSearchChange}
      />
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-xs text-muted-foreground hover:text-foreground transition-colors -mt-2"
      >
        {showAdvanced || !!(sector || mechanism || alertLevel)
          ? "Menos filtros"
          : "Más filtros"}
      </button>

      {/* Desktop: tabla densa */}
      <div className="hidden md:block">
        <DataTable
          columns={columns}
          data={data?.items ?? []}
          page={page}
          totalPages={data?.total_pages ?? 1}
          total={data?.total ?? 0}
          onPageChange={handlePageChange}
          onRowClick={(row) => {
            const ipr = row as IPRListItem;
            router.push(`/ipr/${ipr.id}`);
          }}
          isLoading={isLoading}
          error={loadError}
          onRetry={handleRetry}
          hasActiveFilters={hasActiveFilters}
          onClearFilters={handleClear}
        />
      </div>

      {/* Móvil: tarjetas apiladas */}
      <div className="md:hidden">
        {isLoading ? (
          <div className="space-y-3" aria-busy="true">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-28 rounded-xl bg-muted animate-pulse" />
            ))}
          </div>
        ) : loadError ? (
          <EmptyState
            icon={<AlertTriangle className="size-10 stroke-1 text-amber-500" />}
            title="No se pudieron cargar los datos"
            description={loadError}
            action={
              <Button variant="outline" size="sm" onClick={handleRetry}>
                <RotateCw className="size-4 mr-1.5" />
                Reintentar
              </Button>
            }
          />
        ) : (data?.items.length ?? 0) === 0 ? (
          hasActiveFilters ? (
            <EmptyState
              title="Sin coincidencias"
              description="Ninguna IPR coincide con los filtros aplicados."
              action={
                <Button variant="outline" size="sm" onClick={handleClear}>
                  Limpiar filtros
                </Button>
              }
            />
          ) : (
            <EmptyState title="Aún no hay IPR" description="Cuando se creen, aparecerán aquí." />
          )
        ) : (
          <div className="space-y-3">
            {(data?.items ?? []).map((ipr) => {
              const phaseDays = ipr.phase_entered_at
                ? Math.floor((referenceTime - new Date(ipr.phase_entered_at).getTime()) / 86400000)
                : null;
              const daysColor =
                phaseDays == null
                  ? ""
                  : phaseDays > 90
                    ? "text-red-600"
                    : phaseDays > 30
                      ? "text-amber-600"
                      : "text-green-600";
              return (
                <Clickable
                  key={ipr.id}
                  onClick={() => router.push(`/ipr/${ipr.id}`)}
                  ariaLabel={`Abrir IPR ${ipr.codigo_bip ?? ipr.name}`}
                  className="block rounded-xl border bg-card p-4 hover:border-primary/40 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-[11px] font-mono text-muted-foreground">
                        {ipr.codigo_bip ?? "—"}
                      </p>
                      <p className="font-medium text-sm leading-tight">{ipr.name}</p>
                    </div>
                    {ipr.alert_level && (
                      <span
                        className={`mt-1 inline-block shrink-0 rounded-full size-3 ${alertLevelColors[ipr.alert_level] ?? "bg-gray-300"}`}
                        title={ipr.alert_level}
                      />
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 mt-2">
                    {ipr.ipr_type && (
                      <Badge variant="outline" className="text-[10px]">
                        {iprTypeLabel[ipr.ipr_type] ?? ipr.ipr_type}
                      </Badge>
                    )}
                    {ipr.mechanism && (
                      <MechanismBadge
                        code={ipr.mechanism}
                        label={mechanismLabel[ipr.mechanism] ?? ipr.mechanism}
                        size="sm"
                      />
                    )}
                    {ipr.mcd_phase && (
                      <PhaseBadge
                        code={ipr.mcd_phase}
                        label={phaseLabel[ipr.mcd_phase] ?? ipr.mcd_phase}
                        size="sm"
                      />
                    )}
                  </div>

                  <div className="flex items-center justify-between gap-2 mt-2">
                    {ipr.status && <StatusBadge status={ipr.status} size="sm" />}
                    <div className="flex items-center gap-3 text-[11px] tabular-nums">
                      {phaseDays != null && (
                        <span className={cn("font-medium", daysColor)}>{phaseDays}d</span>
                      )}
                      <span className="text-muted-foreground">
                        {formatCurrency(ipr.total_budget)}
                      </span>
                    </div>
                  </div>
                </Clickable>
              );
            })}

            {/* Paginación móvil */}
            {(data?.total_pages ?? 1) > 1 && (
              <div className="flex items-center justify-between px-1 pt-1 text-sm text-muted-foreground">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => handlePageChange(page - 1)}
                  aria-label="Página anterior"
                >
                  &lt;
                </Button>
                <span>
                  Página {page} de {Math.max(data?.total_pages ?? 1, 1)}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= (data?.total_pages ?? 1)}
                  onClick={() => handlePageChange(page + 1)}
                  aria-label="Página siguiente"
                >
                  &gt;
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
