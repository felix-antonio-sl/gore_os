"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { DataTable } from "@/components/data-table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { IprConvenioDrawer } from "@/components/ipr-convenio-drawer";
import { Plus } from "lucide-react";
import { EmptyState } from "@/components/empty-state";
import { formatCLP } from "@/lib/format";
import type { PaginatedResponse, ConvenioListItem } from "@/types";

interface TabConveniosProps {
  iprId: string;
  canCreate: boolean;
}

export function TabConvenios({ iprId, canCreate }: TabConveniosProps) {
  const router = useRouter();
  const [convenios, setConvenios] = useState<PaginatedResponse<ConvenioListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [showConvenioDrawer, setShowConvenioDrawer] = useState(false);

  const loadConvenios = () => {
    setLoading(true);
    api
      .get<PaginatedResponse<ConvenioListItem>>(`/api/convenios?ipr_id=${iprId}&page_size=50`)
      .then(setConvenios)
      .catch(() => setConvenios(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadConvenios();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [iprId]);

  const convenioColumns = [
    {
      key: "agreement_number",
      label: "N Convenio",
      render: (v: unknown) => <span className="font-mono text-xs">{String(v ?? "-")}</span>,
    },
    {
      key: "agreement_type_label",
      label: "Tipo",
      render: (v: unknown) => <Badge variant="outline" className="text-xs">{String(v ?? "-")}</Badge>,
    },
    {
      key: "total_amount",
      label: "Monto",
      render: (v: unknown) => (
        <span className="font-mono text-xs tabular-nums">
          {v != null ? formatCLP(Number(v)) : "-"}
        </span>
      ),
    },
    {
      key: "state",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} size="sm" />,
    },
    {
      key: "installment_count",
      label: "Cuotas",
      render: (_: unknown, row: unknown) => {
        const r = row as ConvenioListItem;
        return <span className="text-xs">{r.paid_installments}/{r.installment_count}</span>;
      },
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {convenios ? `${convenios.total} convenios` : ""}
        </p>
        {canCreate && (
          <Button size="sm" onClick={() => setShowConvenioDrawer(true)}>
            <Plus className="size-4 mr-1" />
            Agregar Convenio
          </Button>
        )}
      </div>
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !convenios || convenios.items.length === 0 ? (
        <EmptyState compact title="No hay convenios para este IPR." />
      ) : (
        <DataTable
          columns={convenioColumns}
          data={convenios.items}
          page={1}
          totalPages={1}
          total={convenios.total}
          onPageChange={() => {}}
          onRowClick={() => {
            router.push("/convenios");
          }}
          isLoading={loading}
        />
      )}
      <IprConvenioDrawer
        iprId={iprId}
        open={showConvenioDrawer}
        onClose={() => setShowConvenioDrawer(false)}
        onCreated={loadConvenios}
      />
    </div>
  );
}
