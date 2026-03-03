"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { AlertCard } from "@/components/alert-card";
import type { PaginatedResponse, AlertaListItem } from "@/types";

interface TabAlertasProps {
  iprId: string;
}

export function TabAlertas({ iprId }: TabAlertasProps) {
  const router = useRouter();
  const [alertas, setAlertas] = useState<PaginatedResponse<AlertaListItem> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get<PaginatedResponse<AlertaListItem>>(
        `/api/alertas?subject_type=core.ipr&subject_id=${iprId}&page_size=50`
      )
      .then(setAlertas)
      .catch(() => setAlertas(null))
      .finally(() => setLoading(false));
  }, [iprId]);

  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  if (!alertas || alertas.items.length === 0) {
    return <p className="text-sm text-muted-foreground">No hay alertas para este IPR.</p>;
  }

  return (
    <div className="space-y-3">
      {alertas.items.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onViewSubject={(type, subjectId) => {
            if (type === "core.ipr") router.push(`/ipr/${subjectId}`);
            else if (type === "core.agreement") router.push("/convenios");
            else if (type === "core.operational_commitment") router.push("/compromisos");
            else if (type === "core.ipr_problem") router.push("/problemas");
          }}
        />
      ))}
    </div>
  );
}
