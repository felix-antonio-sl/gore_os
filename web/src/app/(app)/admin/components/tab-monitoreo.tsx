"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Database, Users, FileText, Building2, Handshake, ChevronDown, ChevronRight } from "lucide-react";
import type { DataQualityMetrics } from "@/types";

// ---------------------------------------------------------------------------
// SLA Types
// ---------------------------------------------------------------------------

interface SlaItem {
  name: string;
  sla_days: number | null;
  active: number | null;
  breached: number;
  compliance_pct: number;
  signal: "VERDE" | "AMARILLO" | "ROJO";
}

interface SlaDashboard {
  total_monitored: number;
  total_green: number;
  total_red: number;
  slas: SlaItem[];
}

const SIGNAL_DOT: Record<string, string> = {
  VERDE: "bg-green-500",
  AMARILLO: "bg-amber-500",
  ROJO: "bg-red-500",
};

// ---------------------------------------------------------------------------
// Data Quality Helpers
// ---------------------------------------------------------------------------

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

function DataSection({ title, icon, total, metrics }: SectionProps) {
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

// ---------------------------------------------------------------------------
// Collapsible Section
// ---------------------------------------------------------------------------

function MonitorSection({
  title,
  defaultOpen = false,
  children,
}: {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-lg border">
      <button
        type="button"
        className="flex items-center justify-between w-full px-4 py-3 text-left hover:bg-muted/30 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <h3 className="text-sm font-semibold">{title}</h3>
        {open ? <ChevronDown className="size-4 text-muted-foreground" /> : <ChevronRight className="size-4 text-muted-foreground" />}
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export function TabMonitoreo() {
  return (
    <div className="space-y-4">
      <MonitorSection title="Monitoreo SLA" defaultOpen={true}>
        <SlasSection />
      </MonitorSection>

      <MonitorSection title="Salud de Datos">
        <SaludDatosSection />
      </MonitorSection>
    </div>
  );
}

// ---------------------------------------------------------------------------
// SLAs Section
// ---------------------------------------------------------------------------

function SlasSection() {
  const [data, setData] = useState<SlaDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<SlaDashboard>("/api/admin/slas/dashboard")
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data) {
    return <p className="text-sm text-muted-foreground">No se pudieron cargar los SLAs.</p>;
  }

  return (
    <>
      {/* Summary strip */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="rounded-lg border bg-card p-3">
          <p className="text-xs text-muted-foreground">SLAs monitoreados</p>
          <p className="text-2xl font-semibold tabular-nums">{data.total_monitored}</p>
        </div>
        <div className="rounded-lg border bg-card p-3">
          <p className="text-xs text-muted-foreground">En cumplimiento</p>
          <p className="text-2xl font-semibold tabular-nums text-green-600">{data.total_green}</p>
        </div>
        <div className="rounded-lg border bg-card p-3">
          <p className="text-xs text-muted-foreground">En incumplimiento</p>
          <p className={cn("text-2xl font-semibold tabular-nums", data.total_red > 0 ? "text-red-600" : "")}>
            {data.total_red}
          </p>
        </div>
      </div>

      {/* SLA table */}
      <div className="rounded-lg border overflow-hidden">
        <div className="grid grid-cols-[1fr_80px_80px_80px_100px_60px] gap-2 px-4 py-2 bg-muted/40 text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
          <span>SLA</span>
          <span className="text-right">Plazo</span>
          <span className="text-right">Activos</span>
          <span className="text-right">Vencidos</span>
          <span className="text-right">Cumplimiento</span>
          <span className="text-center">Estado</span>
        </div>
        <div className="divide-y">
          {data.slas.map((sla, i) => (
            <div
              key={i}
              className="grid grid-cols-[1fr_80px_80px_80px_100px_60px] gap-2 px-4 py-3 items-center"
            >
              <span className="text-sm font-medium">{sla.name}</span>
              <span className="text-xs text-muted-foreground text-right tabular-nums">
                {sla.sla_days ? `${sla.sla_days}d` : "\u2014"}
              </span>
              <span className="text-xs text-right tabular-nums">
                {sla.active !== null ? sla.active : "\u2014"}
              </span>
              <span className={cn(
                "text-xs text-right tabular-nums font-medium",
                sla.breached > 0 ? "text-red-600" : ""
              )}>
                {sla.breached}
              </span>
              <div className="flex items-center justify-end gap-1.5">
                <div className="h-1.5 w-16 rounded-full bg-muted overflow-hidden">
                  <div
                    className={cn(
                      "h-full rounded-full",
                      sla.signal === "VERDE" ? "bg-green-500" :
                      sla.signal === "AMARILLO" ? "bg-amber-500" : "bg-red-500"
                    )}
                    style={{ width: `${Math.min(sla.compliance_pct, 100)}%` }}
                  />
                </div>
                <span className="text-[10px] tabular-nums w-8 text-right">
                  {sla.compliance_pct}%
                </span>
              </div>
              <div className="flex justify-center">
                <div className={cn("size-2.5 rounded-full", SIGNAL_DOT[sla.signal])} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

// ---------------------------------------------------------------------------
// Salud Datos Section
// ---------------------------------------------------------------------------

function SaludDatosSection() {
  const [data, setData] = useState<DataQualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<DataQualityMetrics>("/api/admin/data-quality")
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-24 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data) {
    return <p className="text-sm text-muted-foreground">No se pudieron cargar las metricas.</p>;
  }

  return (
    <div className="space-y-8">
      <DataSection
        title="Personas"
        icon={<Users className="size-4 text-violet-600" />}
        total={data.persons.total}
        metrics={[
          { label: "Con email", value: data.persons.with_email, total: data.persons.total, pct: data.persons.pct_email },
          { label: "Con RUT", value: data.persons.with_rut, total: data.persons.total, pct: data.persons.pct_rut },
          { label: "Con telefono", value: data.persons.with_phone, total: data.persons.total, pct: data.persons.pct_phone },
        ]}
      />

      <DataSection
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

      <DataSection
        title="Convenios"
        icon={<Handshake className="size-4 text-emerald-600" />}
        total={data.agreements.total}
        metrics={[
          { label: "Con resultado CGR", value: data.agreements.with_cgr, total: data.agreements.total, pct: data.agreements.pct_cgr },
          { label: "Con IPR vinculado", value: data.agreements.with_ipr, total: data.agreements.total, pct: data.agreements.pct_ipr },
          { label: "Con referente tecnico", value: data.agreements.with_referent, total: data.agreements.total, pct: data.agreements.pct_referent },
        ]}
      />

      <DataSection
        title="Documentos"
        icon={<FileText className="size-4 text-cyan-600" />}
        total={data.documents.total}
        metrics={[
          { label: "Con tipo", value: data.documents.with_type, total: data.documents.total, pct: data.documents.pct_type },
          { label: "Con URL", value: data.documents.with_url, total: data.documents.total, pct: data.documents.pct_url },
        ]}
      />

      <DataSection
        title="Organizaciones"
        icon={<Building2 className="size-4 text-amber-600" />}
        total={data.organizations.total}
        metrics={[
          { label: "Con tipo", value: data.organizations.with_type, total: data.organizations.total, pct: data.organizations.pct_type },
          { label: "Con organizacion padre", value: data.organizations.with_parent, total: data.organizations.total, pct: data.organizations.pct_parent },
        ]}
      />
    </div>
  );
}
