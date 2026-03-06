"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { ArrowLeft, Edit2, CheckCircle, Send, RotateCcw, ShieldCheck } from "lucide-react";
import { formatDate } from "@/lib/format";

interface ReportSection {
  section_id: string;
  title: string;
  content: string;
  auto_populated: boolean;
  last_edited_at: string | null;
}

interface ReportContent {
  id: string;
  code: string | null;
  title: string;
  report_type: string;
  status: string;
  period_start: string | null;
  period_end: string | null;
  recipient: string | null;
  generated_by_name: string | null;
  created_at: string;
  sections: ReportSection[];
}

const STATUS_LABELS: Record<string, string> = {
  BORRADOR: "Borrador",
  EN_REVISION: "En Revisión",
  APROBADO: "Aprobado",
  ENVIADO: "Enviado",
};

const TYPE_LABELS: Record<string, string> = {
  FLASH: "Flash",
  SEMANAL: "Semanal",
  MENSUAL: "Mensual",
  TEMATICO: "Temático",
};

export default function InformeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const { user } = useAuth();
  const [report, setReport] = useState<ReportContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);

  const changeStatus = async (newStatus: string) => {
    setStatusLoading(true);
    try {
      await api.post(`/api/dgi/reports/${id}/status`, { status: newStatus });
      // Reload content
      const updated = await api.get<ReportContent>(`/api/dgi/reports/${id}/content`);
      setReport(updated);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al cambiar estado");
    } finally {
      setStatusLoading(false);
    }
  };

  useEffect(() => {
    api
      .get<ReportContent>(`/api/dgi/reports/${id}/content`)
      .then(setReport)
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-48 rounded bg-muted animate-pulse" />
        <div className="h-32 rounded-xl bg-muted animate-pulse" />
        <div className="h-48 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="p-6">
        <Button variant="ghost" size="sm" className="mb-4" onClick={() => router.push("/informes")}>
          <ArrowLeft className="size-4 mr-1" /> Volver
        </Button>
        <p className="text-destructive text-sm">{error ?? "Informe no encontrado."}</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-5 max-w-4xl">
      <Button variant="ghost" size="sm" onClick={() => router.push("/informes")}>
        <ArrowLeft className="size-4 mr-1" /> Volver a Informes
      </Button>

      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="outline">{TYPE_LABELS[report.report_type] ?? report.report_type}</Badge>
          <Badge variant={report.status === "ENVIADO" ? "default" : "secondary"}>
            {STATUS_LABELS[report.status] ?? report.status}
          </Badge>
          {report.code && <span className="text-xs font-mono text-muted-foreground">{report.code}</span>}
        </div>
        <h1 className="text-2xl font-bold">{report.title}</h1>
      </div>

      {/* Workflow actions */}
      {user && (
        <div className="flex gap-2 flex-wrap">
          {report.status === "BORRADOR" && (
            <Button size="sm" onClick={() => changeStatus("EN_REVISION")} disabled={statusLoading}>
              <Send className="size-4 mr-1" />Enviar a Revisión
            </Button>
          )}
          {report.status === "EN_REVISION" && user.role_code === "JEFE_DGI" && (
            <>
              <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => changeStatus("ENVIADO")} disabled={statusLoading}>
                <ShieldCheck className="size-4 mr-1" />Aprobar y Enviar
              </Button>
              <Button size="sm" variant="outline" onClick={() => changeStatus("BORRADOR")} disabled={statusLoading}>
                <RotateCcw className="size-4 mr-1" />Devolver a Borrador
              </Button>
            </>
          )}
        </div>
      )}

      {/* Metadata */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-lg border bg-muted/20">
        <div>
          <p className="text-xs text-muted-foreground">Período</p>
          <p className="text-sm font-medium">
            {formatDate(report.period_start)}
            {report.period_end && ` — ${formatDate(report.period_end)}`}
          </p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Destinatario</p>
          <p className="text-sm font-medium">{report.recipient ?? "-"}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Generado por</p>
          <p className="text-sm font-medium">{report.generated_by_name ?? "-"}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Creado</p>
          <p className="text-sm font-medium">{formatDate(report.created_at)}</p>
        </div>
      </div>

      <Separator />

      {/* Sections */}
      <div className="space-y-4">
        {report.sections.map((section) => (
          <Card key={section.section_id}>
            <CardHeader className="py-3 px-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-semibold">{section.title}</CardTitle>
                <div className="flex items-center gap-2">
                  {section.auto_populated ? (
                    <Badge variant="secondary" className="text-[10px] gap-1">
                      <CheckCircle className="size-2.5" /> Auto-poblado
                    </Badge>
                  ) : (
                    <Badge variant="default" className="text-[10px] gap-1 bg-blue-600">
                      <Edit2 className="size-2.5" /> Editado
                    </Badge>
                  )}
                  {section.last_edited_at && (
                    <span className="text-[10px] text-muted-foreground">
                      {formatDate(section.last_edited_at)}
                    </span>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="px-4 pb-4">
              <pre className="text-sm whitespace-pre-wrap leading-relaxed font-sans">
                {section.content || <span className="text-muted-foreground italic">Sin contenido</span>}
              </pre>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
