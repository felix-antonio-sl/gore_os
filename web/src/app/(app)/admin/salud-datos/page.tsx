"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { PageGuard } from "@/components/page-guard";
import { cn } from "@/lib/utils";
import { Database, Users, FileText, Building2, Handshake } from "lucide-react";
import type { DataQualityMetrics } from "@/types";

interface MetricCardProps {
  label: string;
  value: number;
  total: number;
  pct: number;
}

function MetricCard({ label, value, total, pct }: MetricCardProps) {
  const color =
    pct >= 70 ? "text-green-600" : pct >= 40 ? "text-amber-600" : "text-red-600";
  const bgColor =
    pct >= 70
      ? "bg-green-500"
      : pct >= 40
        ? "bg-amber-500"
        : "bg-red-500";

  return (
    <div className="rounded-lg border bg-card p-3 space-y-2">
      <p className="text-xs text-muted-foreground">{label}</p>
      <div className="flex items-baseline gap-2">
        <span className={cn("text-2xl font-semibold tabular-nums", color)}>
          {pct}%
        </span>
        <span className="text-xs text-muted-foreground tabular-nums">
          {value}/{total}
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all", bgColor)}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  );
}

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  total: number;
  metrics: { label: string; value: number; total: number; pct: number }[];
}

function Section({ title, icon, total, metrics }: SectionProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        {icon}
        <h2 className="text-sm font-semibold">{title}</h2>
        <span className="text-xs text-muted-foreground tabular-nums ml-auto">
          {total.toLocaleString("es-CL")} registros
        </span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {metrics.map((m) => (
          <MetricCard key={m.label} {...m} />
        ))}
      </div>
    </div>
  );
}

export default function SaludDatosPage() {
  const [data, setData] = useState<DataQualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<DataQualityMetrics>("/api/admin/data-quality")
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageGuard allowedRoles={["ADMIN_SISTEMA"]}>
      <div className="p-6 space-y-6">
        <PageHeader
          title="Salud de Datos"
          description="Métricas de completitud por entidad"
          accentColor="violet"
        />

        {loading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-24 rounded-lg bg-muted animate-pulse" />
            ))}
          </div>
        ) : data ? (
          <div className="space-y-8">
            <Section
              title="Personas"
              icon={<Users className="size-4 text-violet-600" />}
              total={data.persons.total}
              metrics={[
                { label: "Con email", value: data.persons.with_email, total: data.persons.total, pct: data.persons.pct_email },
                { label: "Con RUT", value: data.persons.with_rut, total: data.persons.total, pct: data.persons.pct_rut },
                { label: "Con teléfono", value: data.persons.with_phone, total: data.persons.total, pct: data.persons.pct_phone },
              ]}
            />

            <Section
              title="IPRs"
              icon={<Database className="size-4 text-indigo-600" />}
              total={data.iprs.total}
              metrics={[
                { label: "Con ejecutor", value: data.iprs.with_executor, total: data.iprs.total, pct: data.iprs.pct_executor },
                { label: "Con mecanismo", value: data.iprs.with_mechanism, total: data.iprs.total, pct: data.iprs.pct_mechanism },
                { label: "Con naturaleza", value: data.iprs.with_nature, total: data.iprs.total, pct: data.iprs.pct_nature },
                { label: "Con partes", value: data.iprs.with_parties, total: data.iprs.total, pct: data.iprs.pct_parties },
                { label: "Con territorio", value: data.iprs.with_territory, total: data.iprs.total, pct: data.iprs.pct_territory },
              ]}
            />

            <Section
              title="Convenios"
              icon={<Handshake className="size-4 text-emerald-600" />}
              total={data.agreements.total}
              metrics={[
                { label: "Con resultado CGR", value: data.agreements.with_cgr, total: data.agreements.total, pct: data.agreements.pct_cgr },
                { label: "Con IPR vinculado", value: data.agreements.with_ipr, total: data.agreements.total, pct: data.agreements.pct_ipr },
                { label: "Con referente técnico", value: data.agreements.with_referent, total: data.agreements.total, pct: data.agreements.pct_referent },
              ]}
            />

            <Section
              title="Documentos"
              icon={<FileText className="size-4 text-cyan-600" />}
              total={data.documents.total}
              metrics={[
                { label: "Con tipo", value: data.documents.with_type, total: data.documents.total, pct: data.documents.pct_type },
                { label: "Con URL", value: data.documents.with_url, total: data.documents.total, pct: data.documents.pct_url },
              ]}
            />

            <Section
              title="Organizaciones"
              icon={<Building2 className="size-4 text-amber-600" />}
              total={data.organizations.total}
              metrics={[
                { label: "Con tipo", value: data.organizations.with_type, total: data.organizations.total, pct: data.organizations.pct_type },
                { label: "Con organización padre", value: data.organizations.with_parent, total: data.organizations.total, pct: data.organizations.pct_parent },
              ]}
            />
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No se pudieron cargar las métricas.</p>
        )}
      </div>
    </PageGuard>
  );
}
