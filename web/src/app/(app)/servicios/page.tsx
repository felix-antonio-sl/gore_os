"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { StatusBadge } from "@/components/status-badge";
import type { PaginatedResponse, ServiceRequest } from "@/types";

export default function ServiceRequestsPage() {
  const router = useRouter();
  const params = useSearchParams();
  const query = params.toString();
  const page = Math.max(1, Number(params.get("page") ?? 1));
  const [data, setData] = useState<PaginatedResponse<ServiceRequest> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const apiParams = new URLSearchParams(query); apiParams.set("page_size", "20");
      setData(await api.get<PaginatedResponse<ServiceRequest>>(`/api/dgi/services/requests?${apiParams}`));
    } catch (err) { setData(null); setError(err instanceof Error ? err.message : "No se pudieron cargar las solicitudes"); }
    finally { setLoading(false); }
  }, [query]);
  useEffect(() => { void load(); }, [load]);
  return <div className="p-4 sm:p-6 space-y-4">
    <PageHeader title="Solicitudes de servicio" description="Pendientes y atención según el alcance de tu rol." />
    <DataTable columns={[
      { key: "code", label: "Solicitud" }, { key: "service_name", label: "Servicio" },
      { key: "description", label: "Descripción" }, { key: "assigned_to_name", label: "Responsable" },
      { key: "status", label: "Estado", render: (value) => <StatusBadge status={String(value)} /> },
      { key: "days_elapsed", label: "Días transcurridos" },
    ]} data={data?.items ?? []} total={data?.total ?? 0} page={page} totalPages={data?.total_pages ?? 1}
      onPageChange={(value) => { const next = new URLSearchParams(query); next.set("page", String(value)); router.push(`/servicios?${next}`); }}
      onRowClick={(row) => router.push(`/servicios/solicitudes/${(row as ServiceRequest).id}`)} isLoading={loading}
      error={error} onRetry={() => { void load(); }} emptyTitle="Sin solicitudes en tu ámbito" />
  </div>;
}
