"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { DataTable } from "@/components/data-table";
import { TemporalIndicator } from "@/components/temporal-indicator";
import { Button } from "@/components/ui/button";
import { IprCompromisoDrawer } from "@/components/ipr-compromiso-drawer";
import { Plus } from "lucide-react";
import type { PaginatedResponse, CompromisoListItem } from "@/types";

interface TabCompromisosProps {
  iprId: string;
  canCreate: boolean;
}

export function TabCompromisos({ iprId, canCreate }: TabCompromisosProps) {
  const [compromisos, setCompromisos] = useState<PaginatedResponse<CompromisoListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCompromisoDrawer, setShowCompromisoDrawer] = useState(false);

  const loadCompromisos = () => {
    setLoading(true);
    api
      .get<PaginatedResponse<CompromisoListItem>>(`/api/compromisos?ipr_id=${iprId}&page_size=50`)
      .then(setCompromisos)
      .catch(() => setCompromisos(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCompromisos();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const compromisoColumns = [
    { key: "description", label: "Descripción" },
    { key: "responsible_name", label: "Responsable" },
    {
      key: "due_date",
      label: "Vence",
      render: (_: unknown, row: unknown) => {
        const r = row as CompromisoListItem;
        return <TemporalIndicator daysRemaining={r.days_remaining} state={r.state} />;
      },
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
          {compromisos ? `${compromisos.total} compromisos` : ""}
        </p>
        {canCreate && (
          <Button size="sm" onClick={() => setShowCompromisoDrawer(true)}>
            <Plus className="size-4 mr-1" />
            Nuevo Compromiso
          </Button>
        )}
      </div>
      <DataTable
        columns={compromisoColumns}
        data={compromisos?.items ?? []}
        page={1}
        totalPages={1}
        total={compromisos?.total ?? 0}
        onPageChange={() => {}}
        isLoading={loading}
      />
      <IprCompromisoDrawer
        iprId={iprId}
        open={showCompromisoDrawer}
        onClose={() => setShowCompromisoDrawer(false)}
        onCreated={loadCompromisos}
      />
    </div>
  );
}
