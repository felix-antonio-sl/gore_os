"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { searchUsers } from "@/lib/catalog-search";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { PageSkeleton } from "@/components/page-skeleton";
import { StatusBadge } from "@/components/status-badge";
import { ComboboxAsync } from "@/components/combobox-async";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ServiceRequest } from "@/types";

interface RequestDetail extends ServiceRequest {
  allowed_statuses: string[];
  can_assign: boolean;
  can_feedback: boolean;
}
const ACTION_LABELS: Record<string, string> = { EN_EVALUACION: "Evaluar", ACEPTADA: "Aceptar", EN_EJECUCION: "Iniciar atención", COMPLETADA: "Completar atención", RECHAZADA: "Rechazar" };

export default function RequestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [request, setRequest] = useState<RequestDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [responsibleId, setResponsibleId] = useState("");
  const [score, setScore] = useState("");
  const [feedback, setFeedback] = useState("");
  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setRequest(await api.get<RequestDetail>(`/api/dgi/services/requests/${id}`)); }
    catch (err) { setRequest(null); setError(err instanceof Error ? err.message : "No se pudo abrir la solicitud"); }
    finally { setLoading(false); }
  }, [id]);
  useEffect(() => { void load(); }, [load]);
  const save = async (payload: Record<string, unknown>) => {
    setSaving(true); setError(null);
    try { setRequest(await api.patch<RequestDetail>(`/api/dgi/services/requests/${id}`, payload)); }
    catch (err) { setError(err instanceof Error ? err.message : "No se pudo guardar"); }
    finally { setSaving(false); }
  };
  if (loading) return <PageSkeleton variant="detail" />;
  if (!request) return <div className="p-6"><EmptyState title="Solicitud no disponible" description={error ?? undefined}
    action={<Button onClick={() => { void load(); }}>Reintentar</Button>} /></div>;
  return <div className="p-4 sm:p-6 space-y-5">
    <PageHeader title={request.code} description={request.service_name} />
    {error ? <p role="alert" className="text-destructive text-sm">{error}</p> : null}
    <StatusBadge status={request.status} />
    <p>{request.description}</p>
    <dl className="space-y-2 text-sm">
      <div><dt className="inline text-muted-foreground">Solicitante: </dt><dd className="inline">{request.requester_name}</dd></div>
      <div><dt className="inline text-muted-foreground">Responsable: </dt><dd className="inline">{request.assigned_to_name ?? "Sin responsable individual registrado"}</dd></div>
      <div><dt className="inline text-muted-foreground">Días transcurridos: </dt><dd className="inline">{request.days_elapsed ?? "Sin registro"}</dd></div>
      <div><dt className="inline text-muted-foreground">Plazo registrado del servicio: </dt><dd className="inline">{request.sla_days == null ? "Sin registro" : `${request.sla_days} días`}</dd></div>
    </dl>
    {request.can_assign ? <div className="space-y-2 max-w-md"><Label>Responsable</Label>
      <ComboboxAsync value={responsibleId} onChange={setResponsibleId} searchFn={searchUsers} placeholder="Buscar responsable por nombre…" />
      <Button disabled={saving || !responsibleId} onClick={() => { void save({ assigned_to_id: responsibleId }); }}>Guardar responsable</Button></div> : null}
    <div className="flex flex-wrap gap-2">{request.allowed_statuses.map((target) => <Button key={target} disabled={saving}
      onClick={() => { void save({ status: target }); }}>{ACTION_LABELS[target] ?? target}</Button>)}</div>
    {request.can_feedback ? <div className="space-y-2 max-w-md"><Label htmlFor="request-score">Satisfacción (1 a 5)</Label>
      <Input id="request-score" type="number" min="1" max="5" value={score} onChange={(event) => setScore(event.target.value)} />
      <Label htmlFor="request-feedback">Comentario</Label><Textarea id="request-feedback" value={feedback} onChange={(event) => setFeedback(event.target.value)} />
      <Button disabled={saving || !score} onClick={() => { void save({ satisfaction_score: Number(score), feedback_text: feedback }); }}>Enviar evaluación</Button></div> : null}
    <Button asChild variant="outline"><Link href="/dashboard">Volver a la bandeja</Link></Button>
  </div>;
}
