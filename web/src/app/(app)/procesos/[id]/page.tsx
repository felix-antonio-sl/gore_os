"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { PageSkeleton } from "@/components/page-skeleton";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
interface ProcessContext { code: string; name: string; description: string | null; scope: string | null; status_label: string; division_name: string | null; owner_name: string | null }

export default function ProcessContextPage() {
  const { id } = useParams<{ id: string }>();
  const [process, setProcess] = useState<ProcessContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    api.get<ProcessContext>(`/api/dgi/processes/${id}`).then((value) => { if (active) setProcess(value); })
      .catch((err) => { if (active) setError(err instanceof Error ? err.message : "No se pudo consultar el proceso"); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [id]);
  if (loading) return <PageSkeleton variant="detail" />;
  return <div className="p-4 sm:p-6 space-y-4">
    {process ? <><PageHeader title={process.name} description={`${process.code} · Contexto del riesgo`} />
      <p className="text-sm">Estado registrado: {process.status_label}</p>
      <p className="text-sm">Responsable: {process.owner_name ?? "Sin responsable individual registrado"}</p>
      <p className="text-sm">División: {process.division_name ?? "Sin división registrada"}</p>
      <p>{process.description ?? "Sin descripción registrada"}</p><p>{process.scope ?? ""}</p></>
      : <EmptyState title="Proceso no disponible" description={error ?? undefined} />}
    <Button asChild variant="outline"><Link href="/dashboard">Volver a la bandeja</Link></Button>
  </div>;
}
