"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTabParam } from "@/hooks/use-tab-param";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/status-badge";
import { ArrowLeft } from "lucide-react";
import { WRITE_OPERATIONAL_ROLES } from "@/types";
import { MechanismBadge, PhaseBadge } from "../components/ipr-badges";
import type { IprDetail } from "../components/ipr-constants";
import { TabAntecedentes } from "../components/tab-antecedentes";
import { TabCompromisos } from "../components/tab-compromisos";
import { TabProblemas } from "../components/tab-problemas";
import { TabAlertas } from "../components/tab-alertas";
import { TabConvenios } from "../components/tab-convenios";
import { TabRendiciones } from "../components/tab-rendiciones";

const TABS = [
  ["resumen", "Expediente"], ["antecedentes", "Antecedentes"],
  ["compromisos", "Compromisos"], ["problemas", "Problemas"],
  ["alertas", "Alertas"], ["convenios", "Convenios"], ["rendiciones", "Rendiciones"],
] as const;

function IprDetailPageInner({ id }: { id: string }) {
  const { user } = useAuth();
  const [requestedTab, setActiveTab] = useTabParam("tab", "resumen");
  const [ipr, setIpr] = useState<IprDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const activeTab = TABS.some(([key]) => key === requestedTab) ? requestedTab : "antecedentes";
  const showingSummary = activeTab === "resumen";
  const role = user?.role_code;
  const canCreateCompromiso = !!role && ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD", "ANALISTA"].includes(role);
  const canWrite = !!role && WRITE_OPERATIONAL_ROLES.includes(role);

  useEffect(() => {
    let active = true;
    api.get<IprDetail>(`/api/ipr/${id}`)
      .then((data) => { if (active) { setIpr(data); setError(null); } })
      .catch((err) => { if (active) setError(err instanceof Error ? err.message : "No se pudo consultar el expediente."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [id, showingSummary]);

  return (
    <div className="p-4 md:p-6 space-y-5 max-w-7xl mx-auto">
      <Button variant="ghost" size="sm" asChild>
        <Link href="/dashboard"><ArrowLeft className="size-4 mr-2" />Volver a la bandeja</Link>
      </Button>
      {loading ? <div className="h-40 rounded-lg bg-muted animate-pulse" aria-busy="true" /> : error ? (
        <p role="alert" className="text-sm text-destructive">{error}</p>
      ) : ipr ? (
        <>
          <header className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-sm text-muted-foreground">{ipr.codigo_bip}</span>
              <StatusBadge status={ipr.status ?? ""} size="sm" />
              <MechanismBadge code={ipr.mechanism} size="sm" />
              <PhaseBadge code={ipr.mcd_phase} label={ipr.mcd_phase_label} size="sm" />
            </div>
            <h1 className="text-xl md:text-2xl font-semibold tracking-tight break-words">{ipr.name}</h1>
            <p className="text-sm text-muted-foreground">Consulta del expediente y trabajo relacionado.</p>
          </header>
          <nav aria-label="Secciones del expediente" className="flex flex-wrap gap-1 border-b pb-3">
            {TABS.map(([key, label]) => (
              <Button key={key} variant={activeTab === key ? "secondary" : "ghost"} size="sm"
                aria-current={activeTab === key ? "page" : undefined} onClick={() => setActiveTab(key)}>{label}</Button>
            ))}
          </nav>
          {activeTab === "resumen" && (
            <section className="rounded-xl border p-4 md:p-6 space-y-5">
              <h2 className="font-medium">Antecedentes generales</h2>
              <dl className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 text-sm">
                {[
                  ["Responsable registrado", ipr.assignee_name], ["División patrocinante", ipr.sponsor_division_name],
                  ["Ejecutor", ipr.executor_name], ["Formulador", ipr.formulator_name],
                  ["Tipo", ipr.ipr_type_label ?? ipr.ipr_type], ["Mecanismo", ipr.mechanism_label ?? ipr.mechanism],
                  ["Fuente de financiamiento", ipr.funding_source], ["Estado registrado", ipr.status_label ?? ipr.status],
                  ["Fase registrada", ipr.mcd_phase_label ?? ipr.mcd_phase],
                ].map(([label, value]) => (
                  <div key={label}><dt className="text-muted-foreground mb-1">{label}</dt><dd className="break-words">{value || "Sin registro"}</dd></div>
                ))}
              </dl>
              {ipr.intended_outcome && <p className="text-sm whitespace-pre-wrap">{ipr.intended_outcome}</p>}
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" onClick={() => setActiveTab("compromisos")}>Compromisos ({ipr.commitment_count})</Button>
                <Button variant="outline" size="sm" onClick={() => setActiveTab("problemas")}>Problemas ({ipr.problem_count})</Button>
                <Button variant="outline" size="sm" onClick={() => setActiveTab("alertas")}>Alertas ({ipr.alert_count})</Button>
                <Button variant="outline" size="sm" onClick={() => setActiveTab("convenios")}>Convenios ({ipr.agreement_count})</Button>
              </div>
            </section>
          )}
          {activeTab === "antecedentes" && <TabAntecedentes iprId={id} initialSection={requestedTab} />}
          {activeTab === "compromisos" && <TabCompromisos iprId={id} canCreate={canCreateCompromiso} />}
          {activeTab === "problemas" && <TabProblemas iprId={id} canCreate={canWrite} />}
          {activeTab === "alertas" && <TabAlertas iprId={id} />}
          {activeTab === "convenios" && <TabConvenios iprId={id} canCreate={canWrite} />}
          {activeTab === "rendiciones" && <TabRendiciones iprId={id} />}
        </>
      ) : null}
    </div>
  );
}

export default function IprDetailPage() {
  const { id } = useParams<{ id: string }>();
  return <Suspense><IprDetailPageInner key={id} id={id} /></Suspense>;
}
