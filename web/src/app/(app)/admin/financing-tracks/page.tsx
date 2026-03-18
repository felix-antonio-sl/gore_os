"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { PageGuard } from "@/components/page-guard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ExternalLink } from "lucide-react";

interface TrackSummary {
  track_code: string;
  track_label: string;
  total_iprs: number;
  by_phase: Record<string, number>;
  critical_alerts: number;
}

const PHASE_COLORS: Record<string, string> = {
  F0: "bg-gray-200 text-gray-800",
  F1: "bg-blue-100 text-blue-800",
  F2: "bg-indigo-100 text-indigo-800",
  F3: "bg-violet-100 text-violet-800",
  F4: "bg-emerald-100 text-emerald-800",
  F5: "bg-green-100 text-green-800",
};

export default function FinancingTracksPage() {
  const router = useRouter();
  const [tracks, setTracks] = useState<TrackSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<TrackSummary[]>("/api/ipr/track-summary")
      .then(setTracks)
      .catch(() => setTracks([]))
      .finally(() => setLoading(false));
  }, []);

  const totalIprs = tracks.reduce((s, t) => s + t.total_iprs, 0);
  const totalAlerts = tracks.reduce((s, t) => s + t.critical_alerts, 0);

  return (
    <PageGuard allowedRoles={["ADMIN_SISTEMA"]}>
      <div className="p-6 space-y-6">
        <PageHeader
          title="Vías de Financiamiento"
          description="Distribución de IPRs por track y fase"
          accentColor="indigo"
        />

        {/* Summary strip */}
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-lg border bg-card p-3">
            <p className="text-xs text-muted-foreground">Tracks activos</p>
            <p className="text-2xl font-semibold tabular-nums">{tracks.length}</p>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <p className="text-xs text-muted-foreground">Total IPRs con mecanismo</p>
            <p className="text-2xl font-semibold tabular-nums">{totalIprs.toLocaleString("es-CL")}</p>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <p className="text-xs text-muted-foreground">Alertas críticas</p>
            <p className={cn("text-2xl font-semibold tabular-nums", totalAlerts > 0 ? "text-red-600" : "")}>
              {totalAlerts}
            </p>
          </div>
        </div>

        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {tracks.map((track) => (
              <div
                key={track.track_code}
                className="rounded-lg border bg-card p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono text-xs">
                      {track.track_code}
                    </Badge>
                    <span className="text-sm font-medium">{track.track_label}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-semibold tabular-nums">
                      {track.total_iprs}
                    </span>
                    <span className="text-xs text-muted-foreground">IPRs</span>
                    {track.critical_alerts > 0 && (
                      <Badge variant="destructive" className="text-xs">
                        {track.critical_alerts} alertas
                      </Badge>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 text-xs"
                      onClick={() => router.push(`/ipr?mechanism=${track.track_code}`)}
                    >
                      <ExternalLink className="size-3 mr-1" />
                      Ver IPRs
                    </Button>
                  </div>
                </div>

                {/* Phase distribution bar */}
                {track.total_iprs > 0 && (
                  <div className="space-y-1.5">
                    <div className="flex h-3 rounded-full overflow-hidden">
                      {Object.entries(track.by_phase).map(([phase, count]) =>
                        count > 0 ? (
                          <div
                            key={phase}
                            className={cn("h-full", PHASE_COLORS[phase]?.split(" ")[0] ?? "bg-gray-200")}
                            style={{ width: `${(count / track.total_iprs) * 100}%` }}
                            title={`${phase}: ${count} IPRs`}
                          />
                        ) : null
                      )}
                    </div>
                    <div className="flex gap-3 flex-wrap">
                      {Object.entries(track.by_phase).map(([phase, count]) =>
                        count > 0 ? (
                          <span
                            key={phase}
                            className={cn("text-[10px] px-1.5 py-0.5 rounded font-medium tabular-nums", PHASE_COLORS[phase] ?? "")}
                          >
                            {phase}: {count}
                          </span>
                        ) : null
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </PageGuard>
  );
}
