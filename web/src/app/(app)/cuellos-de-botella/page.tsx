"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { RefreshCw, Search } from "lucide-react";
import { formatDate } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { DGI_ROLES } from "@/types";
import type { PaginatedResponse, BottleneckFinding, BottleneckInvestigation } from "@/types";

const FINDING_TYPE_COLORS: Record<string, string> = {
  ACUMULACION: "bg-purple-50 text-purple-700 border-purple-200",
  CICLO_TIEMPO: "bg-blue-50 text-blue-700 border-blue-200",
  PRESUPUESTO: "bg-amber-50 text-amber-700 border-amber-200",
};

const FINDING_TYPE_LABELS: Record<string, string> = {
  ACUMULACION: "Acumulación",
  CICLO_TIEMPO: "Ciclo Tiempo",
  PRESUPUESTO: "Presupuesto",
};

const SEVERITY_COLORS: Record<string, string> = {
  ALTO: "bg-red-50 text-red-700 border-red-200",
  MEDIO: "bg-amber-50 text-amber-700 border-amber-200",
};

const STATUS_COLORS: Record<string, string> = {
  DETECTADO: "bg-slate-50 text-slate-700 border-slate-200",
  VERIFICADO: "bg-blue-50 text-blue-700 border-blue-200",
  ANALIZADO: "bg-cyan-50 text-cyan-700 border-cyan-200",
  PROPUESTO: "bg-amber-50 text-amber-700 border-amber-200",
  IMPLEMENTADO: "bg-green-50 text-green-700 border-green-200",
  CERRADO: "bg-gray-50 text-gray-500 border-gray-200",
};

export default function CuellosDeBotellaPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const canCreate = user && DGI_ROLES.includes(user.role_code);

  const [findings, setFindings] = useState<BottleneckFinding[]>([]);
  const [scanLoading, setScanLoading] = useState(true);
  const [investigations, setInvestigations] = useState<PaginatedResponse<BottleneckInvestigation> | null>(null);
  const [tableLoading, setTableLoading] = useState(true);
  const [tableError, setTableError] = useState<string | null>(null);
  const [creatingIndex, setCreatingIndex] = useState<number | null>(null);

  const page = Number(searchParams.get("page") ?? "1");

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

  const handlePageChange = (newPage: number) => router.push(buildUrl({ page: newPage }));

  const fetchScan = () => {
    setScanLoading(true);
    api
      .get<BottleneckFinding[]>("/api/dgi/data/bottlenecks/scan")
      .then(setFindings)
      .catch(() => {
        setFindings([]);
        toast.error("Error al ejecutar escaneo");
      })
      .finally(() => setScanLoading(false));
  };

  const fetchInvestigations = () => {
    setTableLoading(true);
    setTableError(null);
    api
      .get<PaginatedResponse<BottleneckInvestigation>>(
        `/api/dgi/data/bottlenecks?page=${page}&page_size=20`
      )
      .then((res) => {
        setInvestigations(res);
        setTableError(null);
      })
      .catch((err: Error) => {
        setInvestigations(null);
        setTableError(err.message || "No se pudieron cargar las investigaciones.");
      })
      .finally(() => setTableLoading(false));
  };

  useEffect(() => {
    fetchScan();
  }, []);

  useEffect(() => {
    fetchInvestigations();
  }, [page]);

  const handleCreateInvestigation = async (finding: BottleneckFinding, index: number) => {
    setCreatingIndex(index);
    try {
      const result = await api.post<{ id: string }>("/api/dgi/data/bottlenecks", {
        detection_type: finding.finding_type,
        division_id: finding.division_id,
        problem: finding.description,
        detection_value: finding.detection_value,
        detection_threshold: finding.detection_threshold,
      });
      router.push(`/cuellos-de-botella/${result.id}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear investigación");
      setCreatingIndex(null);
    }
  };

  const columns = [
    {
      key: "code",
      label: "Código",
      render: (v: unknown) => (
        <span className="font-mono text-xs">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "division_name",
      label: "División",
      render: (v: unknown) => (
        <span className="text-sm">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "detection_type",
      label: "Tipo",
      render: (v: unknown) => {
        const code = String(v ?? "");
        return (
          <Badge variant="outline" className={`text-xs ${FINDING_TYPE_COLORS[code] ?? ""}`}>
            {FINDING_TYPE_LABELS[code] ?? code}
          </Badge>
        );
      },
    },
    {
      key: "status",
      label: "Estado",
      render: (v: unknown) => {
        const code = String(v ?? "");
        return (
          <Badge variant="outline" className={`text-xs ${STATUS_COLORS[code] ?? ""}`}>
            {code}
          </Badge>
        );
      },
    },
    {
      key: "detected_at",
      label: "Detectado",
      render: (v: unknown) => (
        <span className="text-xs">{formatDate(v as string)}</span>
      ),
    },
    {
      key: "created_by_name",
      label: "Creado por",
      render: (v: unknown) => (
        <span className="text-sm">{String(v ?? "-")}</span>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Cuellos de Botella"
        description="Detección y resolución de cuellos de botella institucionales"
        accentColor="cyan"
        actions={
          <Button variant="outline" size="sm" onClick={fetchScan} disabled={scanLoading}>
            <RefreshCw className={`size-4 mr-1 ${scanLoading ? "animate-spin" : ""}`} />
            Escanear
          </Button>
        }
      />

      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Detección Automática</h2>

        {scanLoading ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-40 rounded-xl bg-muted animate-pulse" />
            ))}
          </div>
        ) : findings.length === 0 ? (
          <div className="rounded-xl border bg-card p-8">
            <EmptyState
              icon={<Search className="size-10 text-muted-foreground/50" />}
              title="Sin hallazgos activos"
              description="El escaneo no detectó cuellos de botella en este momento. Vuelve a escanear para revisar el estado más reciente."
              action={
                <Button variant="outline" size="sm" onClick={fetchScan} disabled={scanLoading}>
                  <RefreshCw className={`size-4 mr-1 ${scanLoading ? "animate-spin" : ""}`} />
                  Escanear de nuevo
                </Button>
              }
              compact
            />
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {findings.map((finding, idx) => (
              <div key={idx} className="rounded-xl border bg-card p-4 space-y-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className={`text-xs ${FINDING_TYPE_COLORS[finding.finding_type] ?? ""}`}>
                    {FINDING_TYPE_LABELS[finding.finding_type] ?? finding.finding_type}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${SEVERITY_COLORS[finding.severity] ?? ""}`}>
                    {finding.severity}
                  </Badge>
                </div>
                {finding.division_name && (
                  <p className="text-xs text-muted-foreground">{finding.division_name}</p>
                )}
                <p className="text-sm">{finding.description}</p>
                <div className="flex items-baseline gap-2 text-sm">
                  <span className="font-mono font-bold tabular-nums">
                    {finding.detection_value.toLocaleString("es-CL")}
                  </span>
                  <span className="text-muted-foreground">/</span>
                  <span className="font-mono text-muted-foreground tabular-nums">
                    {finding.detection_threshold.toLocaleString("es-CL")}
                  </span>
                  <span className="text-xs text-muted-foreground">umbral</span>
                </div>
                {canCreate && (
                  <Button
                    size="sm"
                    className="w-full"
                    disabled={creatingIndex === idx}
                    onClick={() => handleCreateInvestigation(finding, idx)}
                  >
                    {creatingIndex === idx ? "Creando..." : "Abrir Investigación"}
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Investigaciones</h2>
        <DataTable
          columns={columns}
          data={investigations?.items ?? []}
          page={page}
          totalPages={investigations?.total_pages ?? 1}
          total={investigations?.total ?? 0}
          onPageChange={handlePageChange}
          onRowClick={(row) => {
            const item = row as BottleneckInvestigation;
            router.push(`/cuellos-de-botella/${item.id}`);
          }}
          isLoading={tableLoading}
          error={tableError}
          onRetry={fetchInvestigations}
          emptyTitle="Sin investigaciones"
          emptyDescription="Cuando abras una investigación desde un hallazgo, aparecerá aquí."
        />
      </div>
    </div>
  );
}
