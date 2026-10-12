"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import type { RiskListItem, PaginatedResponse } from "@/types";

export default function RisksPage() {
  const router = useRouter(); const params = useSearchParams();
  const page = Math.max(1, Number(params.get("page") ?? 1));
  const [data, setData] = useState<PaginatedResponse<RiskListItem> | null>(null);
  const [loading, setLoading] = useState(true); const [error, setError] = useState<string | null>(null);
  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setData(await api.get<PaginatedResponse<RiskListItem>>(`/api/risk?page=${page}&page_size=20`)); }
    catch (err) { setData(null); setError(err instanceof Error ? err.message : "No se pudieron cargar los riesgos"); }
    finally { setLoading(false); }
  }, [page]);
  useEffect(() => { void load(); }, [load]);
  return <div className="p-4 sm:p-6 space-y-4"><PageHeader title="Riesgos" description="Revisión, mitigación y contexto en tu ámbito." />
    <DataTable columns={[{ key: "code", label: "Código" }, { key: "name", label: "Riesgo" }, { key: "subject_label", label: "Contexto" },
      { key: "status", label: "Estado", render: (value) => <StatusBadge status={String(value)} /> }, { key: "probability_label", label: "Probabilidad" }]}
      data={data?.items ?? []} page={page} totalPages={data?.total_pages ?? 1} total={data?.total ?? 0}
      onPageChange={(value) => router.push(`/riesgos?page=${value}`)} onRowClick={(row) => router.push(`/riesgos/${(row as RiskListItem).id}`)}
      isLoading={loading} error={error} onRetry={() => { void load(); }} emptyTitle="Sin riesgos en tu ámbito" />
  </div>;
}
