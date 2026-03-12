"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { CockpitJefeDGIView } from "@/components/cockpit-jefe-dgi";
import { CockpitControlGestionView } from "@/components/cockpit-control-gestion";
import { CockpitProcesosView } from "@/components/cockpit-procesos";
import { CockpitTDView } from "@/components/cockpit-td";
import type {
  CockpitJefeDGI,
  CockpitControlGestion,
  CockpitProcesos,
  CockpitTD,
} from "@/types";

type DGICockpitData =
  | { role: "JEFE_DGI"; data: CockpitJefeDGI }
  | { role: "ESP_CONTROL_GESTION"; data: CockpitControlGestion }
  | { role: "ESP_PROCESOS"; data: CockpitProcesos }
  | { role: "ESP_TD"; data: CockpitTD };

export function DgiCockpitRouter() {
  const { user } = useAuth();
  const [cockpit, setCockpit] = useState<DGICockpitData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<unknown>("/api/dgi/cockpit")
      .then((raw) => {
        if (!user) return;
        const role = user.role_code;
        if (role === "JEFE_DGI") {
          setCockpit({ role: "JEFE_DGI", data: raw as CockpitJefeDGI });
        } else if (role === "ESP_CONTROL_GESTION") {
          setCockpit({ role: "ESP_CONTROL_GESTION", data: raw as CockpitControlGestion });
        } else if (role === "ESP_PROCESOS") {
          setCockpit({ role: "ESP_PROCESOS", data: raw as CockpitProcesos });
        } else if (role === "ESP_TD") {
          setCockpit({ role: "ESP_TD", data: raw as CockpitTD });
        }
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [user]);

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="space-y-2">
          <div className="h-8 w-64 rounded bg-muted animate-pulse" />
          <div className="h-4 w-48 rounded bg-muted animate-pulse" />
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-24 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-48 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive">
          Error al cargar el cockpit DGI: {error}
        </div>
      </div>
    );
  }

  if (!cockpit) {
    return (
      <div className="p-6">
        <div className="rounded-md bg-muted px-4 py-3 text-sm text-muted-foreground">
          No hay datos de cockpit disponibles para tu rol.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {cockpit.role === "JEFE_DGI" && <CockpitJefeDGIView data={cockpit.data} />}
      {cockpit.role === "ESP_CONTROL_GESTION" && (
        <CockpitControlGestionView data={cockpit.data} />
      )}
      {cockpit.role === "ESP_PROCESOS" && <CockpitProcesosView data={cockpit.data} />}
      {cockpit.role === "ESP_TD" && <CockpitTDView data={cockpit.data} />}
    </div>
  );
}
