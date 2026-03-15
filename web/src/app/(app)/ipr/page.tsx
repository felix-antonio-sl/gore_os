"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { exportCSV } from "@/lib/csv-export";
import { formatCurrency } from "@/lib/format";
import { PageHeader } from "@/components/page-header";
import type { PaginatedResponse, IPRListItem } from "@/types";

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

const SECTOR_OPTIONS = [
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

const alertLevelColors: Record<string, string> = {
  CRITICO: "bg-red-600 text-white",
  ALTO: "bg-orange-500 text-white",
  ATENCION: "bg-amber-400 text-white",
  INFO: "bg-blue-500 text-white",
};

const mechanismColors: Record<string, string> = {
  SNI: "bg-indigo-100 text-indigo-800 border-indigo-200",
  C33: "bg-violet-100 text-violet-800 border-violet-200",
  FRIL: "bg-emerald-100 text-emerald-800 border-emerald-200",
  GLOSA06: "bg-sky-100 text-sky-800 border-sky-200",
  TRANSFER: "bg-amber-100 text-amber-800 border-amber-200",
  SUBV8: "bg-rose-100 text-rose-800 border-rose-200",
  FRPD: "bg-teal-100 text-teal-800 border-teal-200",
};

const mcdPhaseColors: Record<string, string> = {
  F0: "bg-slate-100 text-slate-700 border-slate-200",
  F1: "bg-blue-100 text-blue-700 border-blue-200",
  F2: "bg-cyan-100 text-cyan-700 border-cyan-200",
  F3: "bg-purple-100 text-purple-700 border-purple-200",
  F4: "bg-green-100 text-green-700 border-green-200",
  F5: "bg-gray-100 text-gray-700 border-gray-200",
};

export default function IprPage() {
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
      if (active) setIsLoading(true);
    });

    api
      .get<PaginatedResponse<IPRListItem>>(`/api/ipr?${params.toString()}`)
      .then((response) => {
        if (active) setData(response);
      })
      .catch(() => {
        if (active) setData(null);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [page, tipo, estado, sector, alertLevel, mechanism, mcdPhase, division, search]);

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
      render: (value: unknown) => (
        <Badge variant="outline" className="text-xs">
          {String(value ?? "-")}
        </Badge>
      ),
    },
    {
      key: "mechanism",
      label: "Mecanismo",
      render: (value: unknown) => {
        const v = String(value ?? "");
        if (!v) return <span className="text-muted-foreground text-xs">—</span>;
        return (
          <Badge variant="outline" className={cn("text-xs", mechanismColors[v])}>
            {v}
          </Badge>
        );
      },
    },
    {
      key: "mcd_phase",
      label: "Fase MCD",
      render: (value: unknown) => {
        const v = String(value ?? "");
        if (!v) return <span className="text-muted-foreground text-xs">—</span>;
        return (
          <Badge variant="outline" className={cn("text-xs", mcdPhaseColors[v])}>
            {v}
          </Badge>
        );
      },
    },
    {
      key: "status",
      label: "Estado",
      render: (value: unknown) => <StatusBadge status={String(value ?? "")} size="sm" />,
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
      />
    </div>
  );
}
