"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { formatCLP, formatDate } from "@/lib/format";
import { DataTable } from "@/components/data-table";
import { DrawerPanel } from "@/components/drawer-panel";
import { FilterBar } from "@/components/filter-bar";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { TimelineHistory } from "@/components/timeline-history";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import type { ActoDetail, ConvenioDetail, CategoryRef, HistoryEntry, PaginatedResponse } from "@/types";

type Kind = "actos" | "convenios";
type Detail = ActoDetail | ConvenioDetail;
interface SignatureTransition extends CategoryRef { blocked?: boolean; reason?: string }

export function SignatureWorkList({ kind }: { kind: Kind }) {
  const router = useRouter();
  const params = useSearchParams();
  const selectedId = params.get("id");
  const page = Math.max(1, Number(params.get("page") ?? 1));
  const search = params.get("search") ?? "";
  const state = params.get("state") ?? params.get("estado") ?? "";
  const [data, setData] = useState<PaginatedResponse<Detail> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [transitions, setTransitions] = useState<SignatureTransition[]>([]);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [pending, setPending] = useState<CategoryRef | null>(null);
  const [saving, setSaving] = useState(false);
  const endpoint = `/api/${kind}`;
  const isAct = kind === "actos";
  const title = isAct ? "Actos" : "Convenios";
  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const query = new URLSearchParams({ page: String(page), page_size: "20" });
      if (search) query.set("search", search);
      if (state) query.set("state", state);
      setData(await api.get<PaginatedResponse<Detail>>(`${endpoint}?${query}`));
    } catch (err) { setData(null); setError(err instanceof Error ? err.message : "No se pudieron cargar los registros"); }
    finally { setLoading(false); }
  }, [endpoint, page, search, state]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    if (!selectedId) return;
    let active = true;
    setDetail(null); setTransitions([]); setDetailError(null);
    Promise.all([api.get<Detail>(`${endpoint}/${selectedId}`), api.get<SignatureTransition[]>(`${endpoint}/${selectedId}/transiciones`)]).then(([record, actions]) => {
      if (active) { setDetail(record); setTransitions(actions); }
    }).catch((err) => { if (active) setDetailError(err instanceof Error ? err.message : "No se pudo abrir el registro"); });
    return () => { active = false; };
  }, [endpoint, selectedId]);
  const navigate = (changes: Record<string, string | number>) => {
    const query = new URLSearchParams(params.toString());
    for (const [key, value] of Object.entries(changes)) { if (value === "") query.delete(key); else query.set(key, String(value)); }
    router.push(`/${kind}${query.size ? `?${query}` : ""}`);
  };
  const applyTransition = async () => {
    if (!selectedId || !pending) return;
    setSaving(true); setDetailError(null);
    try {
      await api.patch(`${endpoint}/${selectedId}`, { state_id: pending.id });
      const [record, actions] = await Promise.all([api.get<Detail>(`${endpoint}/${selectedId}`), api.get<SignatureTransition[]>(`${endpoint}/${selectedId}/transiciones`)]);
      setDetail(record); setTransitions(actions); setPending(null); await load();
    } catch (err) { setDetailError(err instanceof Error ? err.message : "No se pudo cambiar el estado"); setPending(null); }
    finally { setSaving(false); }
  };
  const agreement = !isAct ? detail as ConvenioDetail | null : null;
  const act = isAct ? detail as ActoDetail | null : null;
  const relatedRenditions = agreement?.renditions ?? [];
  const history: HistoryEntry[] = detail?.history?.map((entry) => ({ ...entry, previous_state: entry.previous_state ?? null, comment: entry.comment ?? null })) ?? [];
  return <div className="space-y-4 p-4 sm:p-6">
    <PageHeader title={title} description="Consultar el contexto y ejecutar las transiciones disponibles para tu rol." />
    <FilterBar filters={[]} values={{}} onChange={() => {}} searchValue={search}
      onSearchChange={(value) => navigate({ search: value, page: 1 })} searchPlaceholder={`Buscar ${title.toLowerCase()}…`}
      onClear={() => router.push(`/${kind}`)} />
    <DataTable columns={[
      { key: isAct ? "act_number" : "agreement_number", label: "Número" },
      { key: isAct ? "subject" : "agreement_type_label", label: isAct ? "Materia" : "Tipo" },
      { key: "state", label: "Estado", render: (value) => <StatusBadge status={String(value)} /> },
      { key: isAct ? "issuer_name" : "receiver_name", label: isAct ? "Emisor" : "Contraparte" },
      { key: "ipr_codigo_bip", label: "IPR" },
    ]} data={data?.items ?? []} total={data?.total ?? 0} page={page} totalPages={data?.total_pages ?? 1}
      onPageChange={(value) => navigate({ page: value })} onRowClick={(row) => navigate({ id: (row as Detail).id })}
      isLoading={loading} error={error} onRetry={() => { void load(); }} emptyTitle={`Sin ${title.toLowerCase()} para estos filtros`} />
    <DrawerPanel open={!!selectedId} onClose={() => navigate({ id: "" })} title={isAct ? "Detalle de Acto" : "Detalle de Convenio"} wide>
      {detailError ? <p role="alert" className="text-sm text-destructive">{detailError}</p> : null}
      {!detail && !detailError ? <p>Cargando registro…</p> : detail ? <div className="space-y-4">
        <h2 className="font-semibold">{act?.subject ?? agreement?.agreement_number ?? "Convenio sin número"}</h2>
        <StatusBadge status={detail.state} />
        {act ? <dl className="space-y-2 text-sm">
          <div><dt>Tipo</dt><dd>{act.act_type_label}</dd></div>
          <div><dt>Emisor</dt><dd>{act.issuer_name ?? "Sin registro"}</dd></div>
          <div><dt>Firmante</dt><dd>{act.signer_name ?? "Sin registro"}</dd></div>
          <div><dt>Fecha de emisión</dt><dd>{formatDate(act.issued_at)}</dd></div>
          <div><dt>Revisión CGR</dt><dd>{act.requires_cgr ? "Requerida" : "No registrada como requerida"} · {act.cgr_outcome_label ?? "Sin resultado registrado"}</dd></div>
          {act.resolution_type_label ? <div><dt>Resolución</dt><dd>{act.resolution_type_label} · {act.resolution_subtype_label}</dd></div> : null}
          {act.budget_amount != null ? <div><dt>Monto</dt><dd>{formatCLP(act.budget_amount)}</dd></div> : null}
        </dl> : agreement ? <dl className="space-y-2 text-sm">
          <div><dt>Tipo</dt><dd>{agreement.agreement_type_label}</dd></div>
          <div><dt>Contraparte</dt><dd>{agreement.receiver_name ?? "Sin registro"}</dd></div>
          <div><dt>Referente técnico</dt><dd>{agreement.technical_referent_name ?? "Sin registro"}</dd></div>
          <div><dt>Monto</dt><dd>{agreement.total_amount == null ? "Sin registro" : formatCLP(agreement.total_amount)}</dd></div>
          <div><dt>Vigencia</dt><dd>{formatDate(agreement.valid_from)} — {formatDate(agreement.valid_to)}</dd></div>
          <div><dt>Revisión CGR</dt><dd>{agreement.cgr_outcome_label ?? "Sin resultado registrado"}</dd></div>
        </dl> : null}
        {detail.ipr_id ? <Button asChild variant="outline"><Link href={`/ipr/${detail.ipr_id}`}>Consultar IPR {detail.ipr_codigo_bip}</Link></Button> : null}
        <div className="flex flex-wrap gap-2">{transitions.map((transition) => <Button key={transition.id} disabled={saving || transition.blocked} title={transition.reason}
          onClick={() => setPending(transition)}>{["FIRMADO", "FIRMADO_GORE"].includes(transition.code) ? "Firmar" : transition.label}</Button>)}</div>
        {transitions.filter((transition) => transition.blocked).map((transition) => <p key={transition.id} className="text-sm text-muted-foreground">{transition.label}: {transition.reason}</p>)}
        {agreement?.installments.length ? <div><h3 className="font-medium mb-2">Cuotas registradas</h3><DataTable columns={[
          { key: "installment_number", label: "Cuota" }, { key: "amount", label: "Monto", render: (value) => formatCLP(Number(value)) },
          { key: "payment_status_label", label: "Estado" }, { key: "due_date", label: "Plazo", render: (value) => formatDate(String(value)) },
        ]} data={agreement.installments} page={1} totalPages={1} total={agreement.installments.length} onPageChange={() => {}} /></div> : null}
        {relatedRenditions.length ? <div><h3 className="font-medium mb-2">Rendiciones relacionadas</h3>
          {relatedRenditions.map((rendition) => <p key={rendition.id}><Link className="text-primary underline" href={`/rendiciones?id=${rendition.id}`}>Rendición {rendition.id.slice(0, 8)} · {rendition.state_label}</Link></p>)}</div> : null}
        <TimelineHistory entries={history} />
        <Button asChild variant="outline"><Link href="/dashboard">Volver a la bandeja</Link></Button>
      </div> : null}
    </DrawerPanel>
    <ConfirmDialog variant="default" open={!!pending} onOpenChange={(open) => { if (!open) setPending(null); }} title="Confirmar cambio de estado"
      description={`Se registrará el cambio a ${pending?.label ?? ""}.`} confirmLabel={saving ? "Guardando…" : "Confirmar"}
      onConfirm={() => { void applyTransition(); }} />
  </div>;
}
