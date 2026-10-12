"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DataTable } from "@/components/data-table";
import { DrawerPanel } from "@/components/drawer-panel";
import { FilterBar } from "@/components/filter-bar";
import { PageHeader } from "@/components/page-header";
import { rendicionesConfig, RendicionDetailPanel, type RendicionItem } from "./components";

export default function RendicionesPage() {
  const router = useRouter();
  const params = useSearchParams();
  const query = params.toString();
  const selectedId = params.get("id");
  const page = Math.max(1, Number(params.get("page") ?? 1));
  const [data, setData] = useState<{ items: unknown[]; total: number; totalPages: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setData(await rendicionesConfig.fetchData(new URLSearchParams(query))); }
    catch (err) { setData(null); setError(err instanceof Error ? err.message : "No se pudieron cargar las rendiciones"); }
    finally { setLoading(false); }
  }, [query]);
  useEffect(() => { void load(); }, [load]);
  const navigate = (changes: Record<string, string | number>) => {
    const next = new URLSearchParams(query);
    for (const [key, value] of Object.entries(changes)) { if (value === "") next.delete(key); else next.set(key, String(value)); }
    router.push(`/rendiciones${next.size ? `?${next}` : ""}`);
  };
  const close = () => navigate({ id: "" });
  return <div className="space-y-4 p-4 sm:p-6">
    <PageHeader title="Rendiciones" description="Estado, responsable, revisión y trazabilidad de la rendición."
      actions={<rendicionesConfig.CreateAction onRefresh={() => { void load(); }} />} />
    <FilterBar filters={rendicionesConfig.filters} values={{ state: params.get("state") ?? "" }}
      onChange={(key, value) => navigate({ [key]: value, page: 1 })}
      searchValue={params.get("search") ?? ""} onSearchChange={(value) => navigate({ search: value, page: 1 })}
      searchPlaceholder={rendicionesConfig.searchPlaceholder} onClear={() => router.push("/rendiciones")} />
    <DataTable columns={rendicionesConfig.columns} data={data?.items ?? []} page={page} totalPages={data?.totalPages ?? 1}
      total={data?.total ?? 0} onPageChange={(value) => navigate({ page: value })}
      onRowClick={(row) => navigate({ id: (row as RendicionItem).id })} isLoading={loading} error={error}
      onRetry={() => { void load(); }} emptyTitle="Sin rendiciones para estos filtros" />
    <DrawerPanel open={!!selectedId} onClose={close} title="Detalle de Rendición" wide>
      {selectedId ? <RendicionDetailPanel key={selectedId} item={{ id: selectedId }} onClose={close}
        onRefresh={() => { close(); void load(); }} /> : null}
    </DrawerPanel>
  </div>;
}
