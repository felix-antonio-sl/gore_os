"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { searchUsers } from "@/lib/catalog-search";
import { DataTable } from "@/components/data-table";
import { DrawerPanel } from "@/components/drawer-panel";
import { PageHeader } from "@/components/page-header";
import { PageGuard } from "@/components/page-guard";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ComboboxAsync } from "@/components/combobox-async";
import { formatDate } from "@/lib/format";
import type { ARDecision, PaginatedResponse } from "@/types";

interface DecisionDetail extends ARDecision {
  responsible_id: string | null;
  allowed_statuses: string[];
  can_edit: boolean;
}
const STATUS_LABELS: Record<string, string> = { EN_EJECUCION: "Iniciar", COMPLETADA: "Completar" };

export default function CoordinacionPage() {
  return <PageGuard allowedRoles={["JEFE_DGI", "ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD", "ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA"]}><Decisions /></PageGuard>;
}

function Decisions() {
  const router = useRouter();
  const params = useSearchParams();
  const selectedId = params.get("id");
  const page = Math.max(1, Number(params.get("page") ?? 1));
  const [data, setData] = useState<PaginatedResponse<ARDecision> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<DecisionDetail | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [responsibleId, setResponsibleId] = useState("");
  const [context, setContext] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try { setData(await api.get<PaginatedResponse<ARDecision>>(`/api/dgi/coordination/ar/decisions?page=${page}&page_size=20`)); }
    catch (err) { setData(null); setError(err instanceof Error ? err.message : "No se pudieron cargar las decisiones"); }
    finally { setLoading(false); }
  }, [page]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    if (!selectedId) return;
    let active = true;
    setDetail(null); setDetailError(null);
    api.get<DecisionDetail>(`/api/dgi/coordination/ar/decisions/${selectedId}`).then((value) => {
      if (!active) return;
      setDetail(value); setResponsibleId(value.responsible_id ?? ""); setContext(value.context ?? "");
    }).catch((err) => { if (active) setDetailError(err instanceof Error ? err.message : "No se pudo abrir la decisión"); });
    return () => { active = false; };
  }, [selectedId]);

  const navigate = (values: Record<string, string | number>) => {
    const next = new URLSearchParams(params.toString());
    for (const [key, value] of Object.entries(values)) { if (value === "") next.delete(key); else next.set(key, String(value)); }
    router.push(`/coordinacion${next.size ? `?${next}` : ""}`);
  };
  const save = async (body: Record<string, unknown>) => {
    if (!selectedId) return;
    setSaving(true); setDetailError(null);
    try {
      await api.patch(`/api/dgi/coordination/ar/decisions/${selectedId}`, body);
      setDetail(await api.get<DecisionDetail>(`/api/dgi/coordination/ar/decisions/${selectedId}`));
      await load();
    } catch (err) { setDetailError(err instanceof Error ? err.message : "No se pudo guardar"); }
    finally { setSaving(false); }
  };

  return <div className="p-4 sm:p-6 space-y-4">
    <PageHeader title="Decisiones AR" description="Revisar el pendiente, su responsable y la acción disponible." />
    <DataTable columns={[
      { key: "description", label: "Decisión" }, { key: "responsible_name", label: "Responsable" },
      { key: "status", label: "Estado", render: (value) => <StatusBadge status={String(value)} /> },
      { key: "due_date", label: "Plazo", render: (value) => value ? formatDate(String(value)) : "Sin plazo" },
    ]} data={data?.items ?? []} page={page} totalPages={data?.total_pages ?? 1} total={data?.total ?? 0}
      onPageChange={(value) => navigate({ page: value })} onRowClick={(row) => navigate({ id: (row as ARDecision).id })}
      isLoading={loading} error={error} onRetry={() => { void load(); }} emptyTitle="Sin decisiones registradas" />
    <DrawerPanel open={!!selectedId} onClose={() => navigate({ id: "" })} title="Detalle de Decisión AR">
      {detailError && <p role="alert" className="text-sm text-destructive">{detailError}</p>}
      {!detail && !detailError ? <p>Cargando decisión…</p> : detail ? <div className="space-y-4">
        <p className="font-medium">{detail.description}</p><StatusBadge status={detail.status} />
        <p className="text-sm">Responsable: {detail.responsible_name ?? "Sin responsable individual registrado"}</p>
        <p className="text-sm">Plazo: {detail.due_date ? formatDate(detail.due_date) : "Sin plazo"}</p>
        {detail.can_edit ? <>
          <div className="space-y-2"><Label>Responsable</Label><ComboboxAsync value={responsibleId} onChange={setResponsibleId}
            displayLabel={detail.responsible_name ?? ""} searchFn={searchUsers} placeholder="Buscar responsable por nombre…" /></div>
          <div className="space-y-2"><Label htmlFor="decision-context">Contexto</Label><Textarea id="decision-context" value={context} onChange={(event) => setContext(event.target.value)} /></div>
          <Button disabled={saving} onClick={() => { void save({ context, ...(responsibleId ? { responsible_id: responsibleId } : {}) }); }}>Guardar responsable y contexto</Button>
        </> : <p className="text-sm">{detail.context ?? "Sin contexto registrado"}</p>}
        <div className="flex gap-2 flex-wrap">{detail.allowed_statuses.map((target) => <Button key={target} disabled={saving}
          onClick={() => { void save({ status: target }); }}>{STATUS_LABELS[target] ?? target}</Button>)}</div>
      </div> : null}
    </DrawerPanel>
  </div>;
}
