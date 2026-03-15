"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { EmptyState } from "@/components/empty-state";
import { formatDate, formatCLP } from "@/lib/format";
import { FileCheck } from "lucide-react";
import { cn } from "@/lib/utils";

interface Rendicion {
  id: string;
  code: string;
  agreement_number: string | null;
  amount: number | null;
  state: string;
  state_label: string;
  days_in_state: number | null;
  submitted_at: string | null;
}

interface TabRendicionesProps {
  iprId: string;
}

const SLA_LIMITS: Record<string, number> = {
  EN_REVISION_RTF: 7,
  VISADA_RTF: 1,
  EN_REVISION_UCR: 2,
  OBSERVADA: 15,
};

export function TabRendiciones({ iprId }: TabRendicionesProps) {
  const [items, setItems] = useState<Rendicion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ items: Rendicion[] }>(`/api/dgi/data/rendiciones?ipr_id=${iprId}&page_size=50`)
      .then((res) => setItems(res.items ?? []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [iprId]);

  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-12 bg-muted animate-pulse rounded" />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <EmptyState
        compact
        icon={<FileCheck className="size-8" />}
        title="Sin rendiciones para este IPR"
        description="Las rendiciones se generan a partir de los convenios asociados."
      />
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">{items.length} rendiciones</p>
      <div className="space-y-1.5">
        {items.map((r) => {
          const sla = SLA_LIMITS[r.state];
          const days = r.days_in_state ?? 0;
          const isUrgent = sla != null && days > sla * 0.7;
          const isOverdue = sla != null && days >= sla;

          return (
            <div
              key={r.id}
              className={cn(
                "flex items-center gap-3 p-3 rounded-lg border text-xs",
                isOverdue && "bg-red-50 border-red-200 dark:bg-red-950/20",
                isUrgent && !isOverdue && "bg-amber-50 border-amber-200 dark:bg-amber-950/20",
              )}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="font-mono text-muted-foreground">{r.code}</span>
                  {r.agreement_number && (
                    <span className="text-muted-foreground">Conv. {r.agreement_number}</span>
                  )}
                </div>
                {r.submitted_at && (
                  <span className="text-muted-foreground">Presentada: {formatDate(r.submitted_at)}</span>
                )}
              </div>

              {r.amount != null && (
                <span className="font-mono tabular-nums text-muted-foreground shrink-0">
                  {formatCLP(r.amount)}
                </span>
              )}

              {sla != null && (
                <div className="flex items-center gap-1.5 shrink-0">
                  <div className="w-10 h-1.5 rounded-full bg-muted overflow-hidden">
                    <div
                      className={cn(
                        "h-full rounded-full",
                        isOverdue ? "bg-red-500" : isUrgent ? "bg-amber-500" : "bg-green-500"
                      )}
                      style={{ width: `${Math.min(100, (days / sla) * 100)}%` }}
                    />
                  </div>
                  <span className={cn(
                    "tabular-nums text-[10px]",
                    isOverdue ? "text-red-600 font-medium" : "text-muted-foreground"
                  )}>
                    {days}/{sla}d
                  </span>
                </div>
              )}

              <StatusBadge status={r.state} size="sm" />
            </div>
          );
        })}
      </div>
    </div>
  );
}
