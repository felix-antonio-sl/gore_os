"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { DataTable } from "@/components/data-table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { IprProblemaDrawer } from "@/components/ipr-problema-drawer";
import { Plus } from "lucide-react";
import type { PaginatedResponse, ProblemaListItem } from "@/types";

interface TabProblemasProps {
  iprId: string;
  canCreate: boolean;
}

export function TabProblemas({ iprId, canCreate }: TabProblemasProps) {
  const [problemas, setProblemas] = useState<PaginatedResponse<ProblemaListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [showProblemaDrawer, setShowProblemaDrawer] = useState(false);

  const loadProblemas = () => {
    setLoading(true);
    api
      .get<PaginatedResponse<ProblemaListItem>>(`/api/problemas?ipr_id=${iprId}&page_size=50`)
      .then(setProblemas)
      .catch(() => setProblemas(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProblemas();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const problemaColumns = [
    {
      key: "days_open",
      label: "Dias abierto",
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
        page={1}
        totalPages={1}
        total={problemas?.total ?? 0}
        onPageChange={() => {}}
        isLoading={loading}
      />
      <IprProblemaDrawer
        iprId={iprId}
        open={showProblemaDrawer}
        onClose={() => setShowProblemaDrawer(false)}
        onCreated={loadProblemas}
      />
    </div>
  );
}
