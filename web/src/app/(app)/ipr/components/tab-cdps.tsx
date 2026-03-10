"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { formatDate, formatCurrency } from "@/lib/format";
import { EmptyState } from "@/components/empty-state";
import type { BudgetCommitmentItem } from "@/types";

interface TabCdpsProps {
  iprId: string;
}

export function TabCdps({ iprId }: TabCdpsProps) {
  const [cdps, setCdps] = useState<BudgetCommitmentItem[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    queueMicrotask(() => {
      if (active) setLoading(true);
    });

    api
      .get<BudgetCommitmentItem[]>(`/api/presupuesto/cdps-por-ipr/${iprId}`)
      .then((response) => {
        if (active) setCdps(response);
      })
      .catch(() => {
        if (active) setCdps(null);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [iprId]);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {cdps ? `${cdps.length} CDPs vinculados` : ""}
        </p>
      </div>
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !cdps || cdps.length === 0 ? (
        <EmptyState compact title="No hay CDPs vinculados a este IPR." />
      ) : (
        <div className="space-y-2">
          {cdps.map((cdp) => (
            <div key={cdp.id} className="rounded-md border px-3 py-2 text-sm">
              <div className="flex justify-between">
                <span className="font-mono text-xs">{cdp.commitment_number}</span>
                {cdp.status_label && <StatusBadge status={cdp.status_label} size="sm" />}
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-muted-foreground text-xs">
                  {cdp.issued_at ? formatDate(cdp.issued_at) : "-"}
                  {cdp.expires_at ? ` → ${formatDate(cdp.expires_at)}` : ""}
                </span>
                <span className="font-mono text-xs">{formatCurrency(cdp.amount)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
