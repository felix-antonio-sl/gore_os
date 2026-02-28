"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  FileText,
  Eye,
  Download,
  Edit2,
  CheckCircle2,
  Clock,
  AlertCircle,
  Save,
  X,
  Plus,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";
import type { DGIReport } from "@/types";

// ---------------------------------------------------------------------------
// Local types for report content
// ---------------------------------------------------------------------------
interface ReportContentSection {
  section_id: string;
  title: string;
  content: string;
  auto_populated: boolean;
  last_edited_at: string | null;
}

interface ReportContent {
  id: string;
  title: string;
  report_type: string;
  status: string;
  period_start: string | null;
  period_end: string | null;
  sections: ReportContentSection[];
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

type ReportType = "ALL" | "FLASH" | "SEMANAL" | "MENSUAL" | "TEMATICO";

const REPORT_TYPE_TABS: { id: ReportType; label: string }[] = [
  { id: "ALL", label: "Todos" },
  { id: "FLASH", label: "Flash" },
  { id: "SEMANAL", label: "Semanal" },
  { id: "MENSUAL", label: "Mensual" },
  { id: "TEMATICO", label: "Temático" },
];

// Color maps
const reportTypeBadgeColors: Record<string, string> = {
  FLASH: "bg-red-100 text-red-700 border-red-200",
  SEMANAL: "bg-blue-100 text-blue-700 border-blue-200",
  MENSUAL: "bg-green-100 text-green-700 border-green-200",
  TEMATICO: "bg-purple-100 text-purple-700 border-purple-200",
};

const reportTypeLabels: Record<string, string> = {
  FLASH: "Flash",
  SEMANAL: "Semanal",
  MENSUAL: "Mensual",
  TEMATICO: "Temático",
};

const reportStatusColors: Record<string, string> = {
  BORRADOR: "bg-gray-100 text-gray-600 border-gray-200",
  EN_REVISION: "bg-amber-100 text-amber-700 border-amber-200",
  APROBADO: "bg-green-100 text-green-700 border-green-200",
  ENVIADO: "bg-blue-100 text-blue-700 border-blue-200",
};

const reportStatusLabels: Record<string, string> = {
  BORRADOR: "Borrador",
  EN_REVISION: "En Revisión",
  APROBADO: "Aprobado",
  ENVIADO: "Enviado",
};

// ---------------------------------------------------------------------------
// Mock draft report (in-progress informe)
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function ReportTypeBadge({ type }: { type: string }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "text-[10px] px-1.5 py-0 font-semibold whitespace-nowrap",
        reportTypeBadgeColors[type] ?? "bg-gray-100 text-gray-600 border-gray-200"
      )}
    >
      {reportTypeLabels[type] ?? type}
    </Badge>
  );
}

function ReportStatusBadge({ status }: { status: string }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "text-[10px] px-1.5 py-0 whitespace-nowrap",
        reportStatusColors[status] ?? "bg-gray-100 text-gray-600"
      )}
    >
      {reportStatusLabels[status] ?? status}
    </Badge>
  );
}

// ---------------------------------------------------------------------------
// In-progress draft card — data-driven
// ---------------------------------------------------------------------------

function DraftReportCardLive({ report }: { report: DGIReport }) {
  const [content, setContent] = useState<ReportContent | null>(null);
  const [contentLoading, setContentLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setContentLoading(true);
    api
      .get<ReportContent>(`/api/dgi/reports/${report.id}/content`)
      .then(setContent)
      .catch(() => setContent(null))
      .finally(() => setContentLoading(false));
  }, [report.id]);

  const startEdit = (section: ReportContentSection) => {
    setEditingId(section.section_id);
    setEditText(section.content);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditText("");
  };

  const saveEdit = async (sectionId: string) => {
    setSaving(true);
    try {
      await api.patch(`/api/dgi/reports/${report.id}`, {
        section_id: sectionId,
        content: editText,
      });
      // Refresh content
      const updated = await api.get<ReportContent>(`/api/dgi/reports/${report.id}/content`);
      setContent(updated);
      setEditingId(null);
    } catch {
      // keep editing open on error
    } finally {
      setSaving(false);
    }
  };

  const handleExport = () => {
    window.open(`/api/dgi/reports/${report.id}/export`, "_blank");
  };

  return (
    <Card className="border-blue-200 bg-blue-50/30">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <ReportTypeBadge type={report.report_type} />
              <ReportStatusBadge status={report.status} />
            </div>
            <CardTitle className="text-base leading-tight">{report.title}</CardTitle>
            {(report.period_start || report.period_end) && (
              <p className="text-xs text-muted-foreground">
                Período: {formatDate(report.period_start)} → {formatDate(report.period_end)}
              </p>
            )}
          </div>
          <div className="flex gap-2 shrink-0">
            <Button
              size="sm"
              variant="outline"
              className="h-8 text-xs gap-1.5"
              onClick={handleExport}
            >
              <Download className="size-3.5" />
              Exportar JSON
            </Button>
          </div>
        </div>
      </CardHeader>
      <Separator />
      <CardContent className="pt-3 pb-4">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Secciones del informe
        </p>
        {contentLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-10 rounded bg-muted animate-pulse" />
            ))}
          </div>
        ) : content ? (
          <div className="space-y-1.5">
            {content.sections.map((section) => (
              <div key={section.section_id} className="rounded-md border bg-background">
                {editingId === section.section_id ? (
                  <div className="p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{section.title}</span>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-6"
                          onClick={cancelEdit}
                          disabled={saving}
                        >
                          <X className="size-3.5" />
                        </Button>
                        <Button
                          size="icon"
                          className="size-6"
                          onClick={() => saveEdit(section.section_id)}
                          disabled={saving}
                        >
                          <Save className="size-3.5" />
                        </Button>
                      </div>
                    </div>
                    <textarea
                      className="w-full text-xs font-mono rounded border bg-muted/30 p-2 resize-y min-h-[120px] focus:outline-none focus:ring-1 focus:ring-ring"
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                    />
                  </div>
                ) : (
                  <div className="flex items-start justify-between px-3 py-2 gap-2">
                    <div className="flex items-start gap-2.5 min-w-0">
                      {section.auto_populated ? (
                        <CheckCircle2 className="size-4 text-green-600 shrink-0 mt-0.5" />
                      ) : (
                        <Edit2 className="size-4 text-blue-500 shrink-0 mt-0.5" />
                      )}
                      <div className="min-w-0">
                        <p className="text-sm">{section.title}</p>
                        <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                          {section.content.split("\n")[0]}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-[10px] px-1.5 py-0",
                          section.auto_populated
                            ? "bg-green-50 text-green-700 border-green-200"
                            : "bg-blue-50 text-blue-700 border-blue-200"
                        )}
                      >
                        {section.auto_populated ? "Auto-poblado" : "Editado"}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-6 text-muted-foreground hover:text-foreground"
                        onClick={() => startEdit(section)}
                      >
                        <Edit2 className="size-3.5" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No se pudo cargar el contenido del informe.</p>
        )}
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Create report button (when no draft exists)
// ---------------------------------------------------------------------------

function CreateReportButton({ onCreated }: { onCreated: () => void }) {
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    setLoading(true);
    try {
      const today = new Date();
      const weekNum = Math.ceil((today.getDate() - today.getDay() + 1) / 7);
      const monday = new Date(today);
      monday.setDate(today.getDate() - today.getDay() + 1);
      const friday = new Date(monday);
      friday.setDate(monday.getDate() + 4);

      await api.post("/api/dgi/reports", {
        title: `Informe Semanal S${String(weekNum).padStart(2, "0")} ${today.getFullYear()}`,
        report_type: "SEMANAL",
        period_start: monday.toISOString().split("T")[0],
        period_end: friday.toISOString().split("T")[0],
      });
      onCreated();
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-3 rounded-lg border border-dashed border-blue-300 bg-blue-50/20 px-4 py-3">
      <FileText className="size-5 text-blue-400 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">Sin informe en curso esta semana</p>
        <p className="text-xs text-muted-foreground">Crea el informe semanal para comenzar a completar las secciones.</p>
      </div>
      <Button size="sm" className="shrink-0 gap-1.5" onClick={handleCreate} disabled={loading}>
        <Plus className="size-3.5" />
        Crear Informe
      </Button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Report detail view (clicked row)
// ---------------------------------------------------------------------------

function ReportDetailView({
  report,
  onClose,
}: {
  report: DGIReport;
  onClose: () => void;
}) {
  const router = useRouter();
  return (
    <div className="fixed inset-0 bg-black/20 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg shadow-2xl">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <ReportTypeBadge type={report.report_type} />
                <ReportStatusBadge status={report.status} />
              </div>
              <CardTitle className="text-base leading-tight">{report.title}</CardTitle>
              {report.code && (
                <p className="text-[11px] font-mono text-muted-foreground">{report.code}</p>
              )}
            </div>
            <Button variant="ghost" size="icon" className="size-8 shrink-0" onClick={onClose}>
              ×
            </Button>
          </div>
        </CardHeader>
        <Separator />
        <CardContent className="py-4 space-y-3 text-sm">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-muted-foreground">Período inicio</p>
              <p className="text-sm mt-0.5">{formatDate(report.period_start)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Período fin</p>
              <p className="text-sm mt-0.5">{formatDate(report.period_end)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Destinatario</p>
              <p className="text-sm mt-0.5">{report.recipient ?? "-"}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Generado por</p>
              <p className="text-sm mt-0.5">{report.generated_by_name ?? "-"}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Enviado</p>
              <p className="text-sm mt-0.5">{formatDate(report.sent_at)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Creado</p>
              <p className="text-sm mt-0.5">{formatDate(report.created_at)}</p>
            </div>
          </div>
        </CardContent>
        <Separator />
        <div className="px-6 py-3 flex justify-end gap-2">
          <Button variant="outline" size="sm" onClick={onClose}>
            Cerrar
          </Button>
          <Button
            size="sm"
            onClick={() => {
              onClose();
              router.push(`/informes/${report.id}`);
            }}
          >
            <Eye className="size-4 mr-1.5" />
            Ver informe
          </Button>
        </div>
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function InformesPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const typeParam = (searchParams.get("tipo") as ReportType) ?? "ALL";
  const activeType: ReportType =
    REPORT_TYPE_TABS.find((t) => t.id === typeParam)?.id ?? "ALL";

  const page = Number(searchParams.get("page") ?? "1");

  const [reports, setReports] = useState<DGIReport[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState<DGIReport | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

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

  const handleTypeChange = (type: ReportType) => {
    router.push(buildUrl({ tipo: type === "ALL" ? "" : type, page: 1 }));
  };

  const handlePageChange = (newPage: number) => {
    router.push(buildUrl({ page: newPage }));
  };

  // Fetch reports
  useEffect(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (activeType !== "ALL") params.set("report_type", activeType);

    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsLoading(true);
    api
      .get<DGIReport[]>(`/api/dgi/reports?${params.toString()}`)
      .then(setReports)
      .catch(() => setReports(null))
      .finally(() => setIsLoading(false));
  }, [activeType, page, refreshKey]);

  // Detect draft report
  const draftReport = reports?.find((r) => r.status === "BORRADOR") ?? null;

  // Table columns
  const columns = [
    {
      key: "report_type",
      label: "Tipo",
      render: (value: unknown) => <ReportTypeBadge type={String(value ?? "")} />,
    },
    {
      key: "title",
      label: "Título",
      render: (value: unknown) => (
        <span className="text-xs font-medium">{String(value ?? "-")}</span>
      ),
    },
    {
      key: "period_start",
      label: "Período",
      render: (value: unknown) => (
        <span className="text-xs text-muted-foreground">{formatDate(String(value ?? ""))}</span>
      ),
    },
    {
      key: "recipient",
      label: "Destinatario",
      render: (value: unknown) => (
        <span className="text-xs text-muted-foreground">{String(value ?? "-")}</span>
      ),
    },
    {
      key: "status",
      label: "Estado",
      render: (value: unknown) => <ReportStatusBadge status={String(value ?? "")} />,
    },
    {
      key: "id",
      label: "Acciones",
      render: (_: unknown, row: unknown) => {
        const r = row as DGIReport;
        return (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs px-2 gap-1"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedReport(r);
            }}
          >
            <Eye className="size-3.5" />
            Ver
          </Button>
        );
      },
    },
  ];

  // Stats summary (computed from data)
  const totalReports = reports?.length ?? 0;
  const enviados = reports?.filter((r) => r.status === "ENVIADO").length ?? 0;
  const enRevision = reports?.filter((r) => r.status === "EN_REVISION").length ?? 0;
  const borradores = reports?.filter((r) => r.status === "BORRADOR").length ?? 0;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-5 py-3 border-b shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold leading-tight">Informes DGI</h1>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Generación y seguimiento de informes institucionales
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="size-4 text-green-600" />
              <span>
                <span className="font-semibold text-foreground">{enviados}</span> enviados
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <AlertCircle className="size-4 text-amber-500" />
              <span>
                <span className="font-semibold text-foreground">{enRevision}</span> en revisión
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock className="size-4 text-gray-400" />
              <span>
                <span className="font-semibold text-foreground">{borradores}</span> borradores
              </span>
            </div>
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="px-5 py-4 space-y-6 max-w-5xl">
          {/* Draft in-progress section */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold">Informe en curso</h2>
              <Badge variant="outline" className="text-[10px] px-1.5 py-0 bg-blue-50 text-blue-600 border-blue-200">
                Semana actual
              </Badge>
            </div>
            {draftReport ? (
              <DraftReportCardLive report={draftReport} />
            ) : (
              <CreateReportButton onCreated={() => setRefreshKey((k) => k + 1)} />
            )}
          </section>

          <Separator />

          {/* Historical reports section */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold">Historial de informes</h2>
              <span className="text-xs text-muted-foreground">
                {totalReports} {totalReports === 1 ? "informe" : "informes"} en total
              </span>
            </div>

            {/* Type filter tabs */}
            <div className="flex items-center gap-1 mb-4 flex-wrap">
              {REPORT_TYPE_TABS.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => handleTypeChange(tab.id)}
                  className={cn(
                    "px-3 py-1.5 rounded-md text-xs font-medium transition-colors border",
                    activeType === tab.id
                      ? "bg-foreground text-background border-foreground"
                      : "bg-background text-muted-foreground border-border hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  {tab.label}
                  {tab.id === "FLASH" && (
                    <span className="ml-1 text-red-500">●</span>
                  )}
                  {tab.id === "SEMANAL" && (
                    <span className="ml-1 text-blue-500">●</span>
                  )}
                  {tab.id === "MENSUAL" && (
                    <span className="ml-1 text-green-500">●</span>
                  )}
                  {tab.id === "TEMATICO" && (
                    <span className="ml-1 text-purple-500">●</span>
                  )}
                </button>
              ))}
            </div>

            <DataTable
              columns={columns}
              data={reports ?? []}
              page={page}
              totalPages={1}
              total={totalReports}
              onPageChange={handlePageChange}
              onRowClick={(row) => setSelectedReport(row as DGIReport)}
              isLoading={isLoading}
            />
          </section>

          {/* Empty state when no data at all */}
          {!isLoading && reports?.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground gap-2">
              <FileText className="size-10 opacity-30" />
              <p className="text-sm">No hay informes para el filtro seleccionado</p>
              <p className="text-xs">
                {activeType !== "ALL" ? (
                  <>
                    No se encontraron informes de tipo{" "}
                    <span className="font-medium">{reportTypeLabels[activeType] ?? activeType}</span>
                  </>
                ) : (
                  "El historial de informes aparecerá aquí"
                )}
              </p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Report detail modal */}
      {selectedReport && (
        <ReportDetailView
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />
      )}
    </div>
  );
}
