"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, ArrowRight, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";
import { PageHeader } from "@/components/page-header";
import { PageSkeleton } from "@/components/page-skeleton";
import { EmptyState } from "@/components/empty-state";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { ActionItem, ActionItemsResponse } from "@/types";

const CATEGORY_NAMES: Record<ActionItem["category"], string> = {
  COMPROMISO: "Compromisos", ALERTA: "Alertas", DECISION: "Decisiones",
  ESCALAMIENTO: "Escalamientos", SLA: "Servicios", RIESGO: "Riesgos",
  FIRMA: "Firmas", RENDICION: "Rendiciones", IPR: "IPR",
};
const PAGE_SIZE = 20;

export default function WorkInboxPage() {
  const { user } = useAuth();
  const userId = user?.id;
  const [data, setData] = useState<ActionItemsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [assignment, setAssignment] = useState("all");
  const [page, setPage] = useState(1);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await api.get<ActionItemsResponse>("/api/dashboard/action-items"));
    } catch (err) {
      setData(null);
      setError(err instanceof Error ? err.message : "No se pudo cargar la bandeja");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!userId) return;
    void load();
    const refresh = () => { void load(); };
    window.addEventListener("focus", refresh);
    return () => window.removeEventListener("focus", refresh);
  }, [userId, load]);

  const search = query.trim().toLocaleLowerCase("es-CL");
  const filtered = (data?.items ?? []).filter((item) =>
    (category === "all" || item.category === category) &&
    (assignment === "all" || item.responsible_id === userId) &&
    (!search || [item.title, item.subtitle, item.responsible_name].some((value) =>
      value?.toLocaleLowerCase("es-CL").includes(search)
    ))
  );
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const visible = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  if (loading && !data && !error) return <PageSkeleton variant="list" />;

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6">
      <PageHeader
        title="Bandeja de trabajo"
        description="Pendientes, responsable, estado y siguiente acción en tu ámbito."
        actions={
          <Button variant="outline" size="sm" onClick={() => { void load(); }} disabled={loading}>
            <RefreshCw data-icon="inline-start" />Actualizar
          </Button>
        }
      />
      {error ? (
        <EmptyState icon={<AlertTriangle className="size-10" />} title="No se pudo cargar la bandeja" description={error}
          action={<Button variant="outline" onClick={() => { void load(); }}>Reintentar</Button>} />
      ) : data ? (
        <>
          <div className="flex flex-wrap items-center gap-3" aria-live="polite">
            <Badge variant="secondary">{data.scope_label}</Badge>
            <span className="text-sm">{data.summary}</span>
            <Button asChild variant="link" size="sm" className="sm:ml-auto">
              <Link href="/panorama">Ver panorama y herramientas</Link>
            </Button>
          </div>
          <div className="flex flex-wrap gap-3">
            <Input aria-label="Buscar pendientes" placeholder="Buscar pendiente o responsable…" value={query}
              onChange={(event) => { setQuery(event.target.value); setPage(1); }} className="sm:max-w-sm" />
            <Select value={category} onValueChange={(value) => { setCategory(value); setPage(1); }}>
              <SelectTrigger aria-label="Tipo de pendiente" className="w-full sm:w-48"><SelectValue /></SelectTrigger>
              <SelectContent><SelectGroup>
                <SelectItem value="all">Todos los tipos</SelectItem>
                {Object.entries(CATEGORY_NAMES).map(([code, label]) => <SelectItem key={code} value={code}>{label}</SelectItem>)}
              </SelectGroup></SelectContent>
            </Select>
            <Select value={assignment} onValueChange={(value) => { setAssignment(value); setPage(1); }}>
              <SelectTrigger aria-label="Asignación" className="w-full sm:w-52"><SelectValue /></SelectTrigger>
              <SelectContent><SelectGroup>
                <SelectItem value="all">Todo mi ámbito</SelectItem>
                <SelectItem value="mine">Asignados a mí</SelectItem>
              </SelectGroup></SelectContent>
            </Select>
          </div>
          {data.limited_sources.length > 0 ? (
            <p className="text-sm text-muted-foreground">
              {data.limited_sources.join(", ")}: se muestra un corte de atención. Puedes consultar el resto en su herramienta.
            </p>
          ) : null}
          {filtered.length === 0 ? (
            <EmptyState title={data.items.length ? "Sin resultados para estos filtros" : "Sin pendientes en tu ámbito"}
              description={data.items.length ? "Ajusta la búsqueda o la asignación." : "La bandeja se actualiza al volver o con el botón Actualizar."} />
          ) : (
            <div className="grid gap-4 lg:grid-cols-2" aria-busy={loading}>
              {visible.map((item) => (
                <Card key={`${item.category}-${item.id}`}>
                  <CardHeader>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="outline">{CATEGORY_NAMES[item.category]}</Badge>
                      <Badge variant="secondary">{item.state_label ?? "Sin estado registrado"}</Badge>
                      {item.days_remaining !== null ? <TemporalIndicator daysRemaining={item.days_remaining} state={item.state ?? ""} /> : null}
                    </div>
                    <CardTitle>{item.title}</CardTitle>
                    {item.subtitle ? <CardDescription>{item.subtitle}</CardDescription> : null}
                  </CardHeader>
                  <CardContent>
                    <dl className="flex flex-col gap-2 text-sm">
                      <div><dt className="inline text-muted-foreground">Responsable: </dt><dd className="inline">{item.responsible_name ?? "Sin responsable individual registrado"}</dd></div>
                      {item.deadline ? <div><dt className="inline text-muted-foreground">Plazo: </dt><dd className="inline">{formatDate(item.deadline)}</dd></div> : null}
                    </dl>
                  </CardContent>
                  <CardFooter>
                    <Button asChild size="sm" variant="outline">
                      <Link href={item.action_route} aria-label={`${item.action_label}: ${item.title}`}>
                        {item.action_label}<ArrowRight data-icon="inline-end" />
                      </Link>
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
          {filtered.length > PAGE_SIZE ? (
            <div className="flex flex-wrap items-center justify-between gap-3">
              <span className="text-sm text-muted-foreground">Página {currentPage} de {totalPages} · {filtered.length} pendientes</span>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled={currentPage === 1} onClick={() => setPage(currentPage - 1)}>Anterior</Button>
                <Button variant="outline" size="sm" disabled={currentPage === totalPages} onClick={() => setPage(currentPage + 1)}>Siguiente</Button>
              </div>
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
