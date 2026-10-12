"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { AlertCard } from "@/components/alert-card";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import type { PaginatedResponse, AlertaListItem } from "@/types";

interface TabAlertasProps {
  iprId: string;
}

export function TabAlertas({ iprId }: TabAlertasProps) {
  const router = useRouter();
  const [alertas, setAlertas] = useState<PaginatedResponse<AlertaListItem> | null>(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    queueMicrotask(() => {
      if (active) { setLoading(true); setError(null); }
    });

    api
      .get<PaginatedResponse<AlertaListItem>>(
        `/api/alertas?subject_type=core.ipr&subject_id=${iprId}&page=${page}&page_size=50`
      )
      .then((response) => {
        if (active) setAlertas(response);
      })
      .catch((err) => {
        if (active) { setAlertas(null); setError(err instanceof Error ? err.message : "No se pudieron consultar las alertas."); }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [iprId, page]);

  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) return <p role="alert" className="text-sm text-destructive">{error}</p>;

  if (!alertas || alertas.items.length === 0) {
    return (
      <EmptyState
        compact
        title="Sin alertas activas"
        description="No hay alertas registradas para esta IPR."
      />
    );
  }

  return (
    <div className="space-y-3">
      {alertas.items.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onViewSubject={(type, subjectId) => {
            if (type === "core.ipr") router.push(`/ipr/${subjectId}`);
            else if (type === "core.agreement") router.push(`/convenios?id=${subjectId}`);
            else if (type === "core.operational_commitment") router.push(`/compromisos?id=${subjectId}`);
            else if (type === "core.ipr_problem") router.push(`/problemas?id=${subjectId}`);
          }}
        />
      ))}
      {alertas.total_pages > 1 && <div className="flex items-center justify-between text-sm">
        <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage((value) => value - 1)}>Anterior</Button>
        <span>{page} / {alertas.total_pages}</span>
        <Button variant="outline" size="sm" disabled={page >= alertas.total_pages} onClick={() => setPage((value) => value + 1)}>Siguiente</Button>
      </div>}
    </div>
  );
}
