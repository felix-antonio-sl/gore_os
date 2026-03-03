"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { formatCurrency } from "@/lib/format";
import type { ActoListItem } from "@/types";

interface TabResolucionesProps {
  iprId: string;
}

export function TabResoluciones({ iprId }: TabResolucionesProps) {
  const router = useRouter();
  const [resoluciones, setResoluciones] = useState<ActoListItem[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get<{ items: ActoListItem[] }>(`/api/actos?ipr_id=${iprId}&page_size=100`)
      .then((data) => setResoluciones(data.items))
      .catch(() => setResoluciones(null))
      .finally(() => setLoading(false));
  }, [iprId]);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {resoluciones ? `${resoluciones.length} resoluciones vinculadas` : ""}
        </p>
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !resoluciones || resoluciones.length === 0 ? (
        <p className="text-sm text-muted-foreground">No hay resoluciones vinculadas a este IPR.</p>
      ) : (
        <div className="space-y-2">
          {resoluciones.map((acto) => (
            <div
              key={acto.id}
              className="rounded-md border px-3 py-2 text-sm cursor-pointer hover:bg-muted/50"
              onClick={() => router.push(`/actos?search=${encodeURIComponent(acto.act_number)}`)}
            >
              <div className="flex justify-between">
                <span className="font-mono text-xs">{acto.act_number}</span>
                <StatusBadge status={acto.state} size="sm" />
              </div>
              <p className="text-xs line-clamp-1 mt-1">{acto.subject}</p>
              <div className="flex justify-between mt-1">
                <span className="text-muted-foreground text-xs">
                  {acto.resolution_type_label ?? acto.act_type_label}
                </span>
                {acto.budget_amount !== null && acto.budget_amount !== undefined && (
                  <span className="font-mono text-xs">{formatCurrency(acto.budget_amount)}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
