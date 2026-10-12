"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { DataTable } from "@/components/data-table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ProblemaCreateDrawer } from "@/components/problema-create-drawer";
import { Plus } from "lucide-react";
import type { PaginatedResponse, ProblemaListItem } from "@/types";

interface TabProblemasProps {
  iprId: string;
  canCreate: boolean;
}

export function TabProblemas({ iprId, canCreate }: TabProblemasProps) {
  const router = useRouter();
  const [problemas, setProblemas] = useState<PaginatedResponse<ProblemaListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [showProblemaDrawer, setShowProblemaDrawer] = useState(false);

  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const loadProblemas = useCallback(() => {
    setLoading(true);
    setError(null);
    api.get<PaginatedResponse<ProblemaListItem>>(`/api/problemas?ipr_id=${iprId}&page=${page}&page_size=50`)
      .then(setProblemas)
      .catch((err) => { setProblemas(null); setError(err instanceof Error ? err.message : "No se pudo consultar el trabajo relacionado."); })
      .finally(() => setLoading(false));
  }, [iprId, page]);
  useEffect(() => {
    let active = true;
    queueMicrotask(() => { if (active) loadProblemas(); });
    return () => { active = false; };
  }, [loadProblemas]);

  const problemaColumns = [
    {
      key: "days_open",
      label: "Días abierto",
      render: (v: unknown) => <span className="text-xs tabular-nums">{String(v ?? 0)}d</span>,
    },
    { key: "problem_type_label", label: "Tipo" },
    {
      key: "impact_label",
      label: "Impacto",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "-")}</Badge>
      ),
    },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {problemas ? `${problemas.total} problemas` : ""}
        </p>
        {canCreate && (
          <Button size="sm" onClick={() => setShowProblemaDrawer(true)}>
            <Plus className="size-4 mr-1" />
            Nuevo Problema
          </Button>
        )}
      </div>
      <DataTable
        columns={problemaColumns}
        data={problemas?.items ?? []}
        page={page}
        totalPages={problemas?.total_pages ?? 1}
        total={problemas?.total ?? 0}
        onPageChange={setPage}
        onRowClick={(row) => router.push(`/problemas?id=${(row as ProblemaListItem).id}`)}
        isLoading={loading}
        error={error}
        onRetry={loadProblemas}
        emptyTitle="Aún no hay problemas registrados"
        emptyDescription="Registra el primer problema detectado en esta IPR."
      />
      <ProblemaCreateDrawer
        iprId={iprId}
        open={showProblemaDrawer}
        onClose={() => setShowProblemaDrawer(false)}
        onCreated={loadProblemas}
      />
    </div>
  );
}
