"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { rendicionesConfig, type RendicionItem } from "../../rendiciones/components";
import type { PaginatedResponse } from "@/types";

export function TabRendiciones({ iprId }: { iprId: string }) {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PaginatedResponse<RendicionItem> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const load = useCallback(() => {
    setLoading(true); setError(null);
    api.get<PaginatedResponse<RendicionItem>>(`/api/dgi/data/rendiciones?ipr_id=${iprId}&page=${page}&page_size=50`)
      .then(setData)
      .catch((err) => { setData(null); setError(err instanceof Error ? err.message : "No se pudieron consultar las rendiciones."); })
      .finally(() => setLoading(false));
  }, [iprId, page]);
  useEffect(() => {
    let active = true;
    queueMicrotask(() => { if (active) load(); });
    return () => { active = false; };
  }, [load]);
  return <DataTable columns={rendicionesConfig.columns} data={data?.items ?? []}
    page={page} totalPages={data?.total_pages ?? 1} total={data?.total ?? 0} onPageChange={setPage}
    onRowClick={(row) => router.push(`/rendiciones?id=${(row as RendicionItem).id}`)}
    isLoading={loading} error={error} onRetry={load} emptyTitle="Sin rendiciones para este expediente" />;
}
