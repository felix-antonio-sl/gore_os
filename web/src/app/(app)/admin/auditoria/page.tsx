"use client";

import { useEffect, useState, useCallback } from "react";
import { useSearchParams, usePathname, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { PageGuard } from "@/components/page-guard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { formatDateTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import { ChevronDown, ChevronRight, Download } from "lucide-react";
import { exportCSV } from "@/lib/csv-export";
import type { PaginatedResponse } from "@/types";

interface AuditEvent {
  id: string;
  occurred_at: string;
  event_type: string;
  event_type_label: string;
  subject_type: string;
  subject_id: string;
  actor_name: string;
  data: Record<string, unknown>;
}

interface AuditResponse {
  items: AuditEvent[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  filters: {
    event_types: { code: string; label: string }[];
    subject_types: string[];
  };
}

const EVENT_TYPE_COLORS: Record<string, string> = {
  STATE_TRANSITION: "bg-blue-100 text-blue-800",
  LOGIN: "bg-green-100 text-green-800",
  LOGIN_FAILED: "bg-red-100 text-red-800",
  PASSWORD_CHANGED: "bg-amber-100 text-amber-800",
  RISK_CREATED: "bg-orange-100 text-orange-800",
  ALERT_CREATED: "bg-rose-100 text-rose-800",
  ESCALATION_CREATED: "bg-purple-100 text-purple-800",
};

export default function AuditoriaPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const page = Number(searchParams.get("page") ?? "1");
  const eventType = searchParams.get("event_type") ?? "";
  const subjectType = searchParams.get("subject_type") ?? "";
  const dateFrom = searchParams.get("date_from") ?? "";
  const dateTo = searchParams.get("date_to") ?? "";
  const search = searchParams.get("search") ?? "";

  const [data, setData] = useState<AuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const buildUrl = useCallback(
    (overrides: Record<string, string>) => {
      const params = new URLSearchParams(searchParams.toString());
      for (const [k, v] of Object.entries(overrides)) {
        if (v) params.set(k, v);
        else params.delete(k);
      }
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "25");
    if (eventType) params.set("event_type", eventType);
    if (subjectType) params.set("subject_type", subjectType);
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);
    if (search) params.set("search", search);

    api
      .get<AuditResponse>(`/api/admin/audit?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [page, eventType, subjectType, dateFrom, dateTo, search]);

  const CSV_COLUMNS = [
    { key: "occurred_at", label: "Fecha" },
    { key: "event_type_label", label: "Tipo" },
    { key: "subject_type", label: "Entidad" },
    { key: "subject_id", label: "ID" },
    { key: "actor_name", label: "Actor" },
  ];

  return (
    <PageGuard allowedRoles={["ADMIN_SISTEMA"]}>
      <div className="p-6 space-y-4">
        <PageHeader
          title="Auditoría"
          description={`${data?.total ?? 0} eventos registrados`}
          accentColor="rose"
          actions={
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportCSV(CSV_COLUMNS, data?.items ?? [], "auditoria")}
            >
              <Download className="size-4 mr-1" />
              CSV
            </Button>
          }
        />

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          <Select
            value={eventType}
            onValueChange={(v) => router.push(buildUrl({ event_type: v === "ALL" ? "" : v, page: "1" }))}
          >
            <SelectTrigger className="w-48 h-8 text-xs">
              <SelectValue placeholder="Tipo evento" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Todos los tipos</SelectItem>
              {data?.filters?.event_types?.map((et) => (
                <SelectItem key={et.code} value={et.code}>
                  {et.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={subjectType}
            onValueChange={(v) => router.push(buildUrl({ subject_type: v === "ALL" ? "" : v, page: "1" }))}
          >
            <SelectTrigger className="w-40 h-8 text-xs">
              <SelectValue placeholder="Entidad" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Todas</SelectItem>
              {data?.filters?.subject_types?.map((st) => (
                <SelectItem key={st} value={st}>
                  {st}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Input
            type="date"
            value={dateFrom}
            onChange={(e) => router.push(buildUrl({ date_from: e.target.value, page: "1" }))}
            className="w-36 h-8 text-xs"
            placeholder="Desde"
          />
          <Input
            type="date"
            value={dateTo}
            onChange={(e) => router.push(buildUrl({ date_to: e.target.value, page: "1" }))}
            className="w-36 h-8 text-xs"
            placeholder="Hasta"
          />
          <Input
            placeholder="Buscar..."
            value={search}
            onChange={(e) => router.push(buildUrl({ search: e.target.value, page: "1" }))}
            className="w-48 h-8 text-xs"
          />
        </div>

        {/* Table */}
        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="h-10 rounded bg-muted animate-pulse" />
            ))}
          </div>
        ) : data && data.items.length > 0 ? (
          <div className="rounded-lg border overflow-hidden">
            <div className="grid grid-cols-[24px_140px_140px_120px_1fr_100px] gap-2 px-3 py-2 bg-muted/40 text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
              <span />
              <span>Fecha</span>
              <span>Tipo</span>
              <span>Entidad</span>
              <span>ID Sujeto</span>
              <span>Actor</span>
            </div>
            <div className="divide-y">
              {data.items.map((ev) => (
                <div key={ev.id}>
                  <div
                    className="grid grid-cols-[24px_140px_140px_120px_1fr_100px] gap-2 px-3 py-2 items-center cursor-pointer hover:bg-muted/30 transition-colors"
                    onClick={() => setExpandedId(expandedId === ev.id ? null : ev.id)}
                  >
                    <span className="text-muted-foreground">
                      {expandedId === ev.id ? (
                        <ChevronDown className="size-3.5" />
                      ) : (
                        <ChevronRight className="size-3.5" />
                      )}
                    </span>
                    <span className="text-xs tabular-nums">{formatDateTime(ev.occurred_at)}</span>
                    <Badge
                      variant="secondary"
                      className={cn(
                        "text-[10px] justify-center",
                        EVENT_TYPE_COLORS[ev.event_type] ?? "bg-gray-100 text-gray-800"
                      )}
                    >
                      {ev.event_type_label}
                    </Badge>
                    <span className="text-xs text-muted-foreground font-mono">{ev.subject_type}</span>
                    <span className="text-xs font-mono text-muted-foreground truncate">
                      {ev.subject_id.substring(0, 8)}…
                    </span>
                    <span className="text-xs truncate">{ev.actor_name}</span>
                  </div>
                  {expandedId === ev.id && ev.data && Object.keys(ev.data).length > 0 && (
                    <div className="px-10 pb-3">
                      <pre className="text-[10px] bg-muted/50 rounded p-2 overflow-x-auto font-mono text-muted-foreground">
                        {JSON.stringify(ev.data, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground py-8 text-center">
            No se encontraron eventos con los filtros seleccionados.
          </p>
        )}

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              Página {data.page} de {data.total_pages} ({data.total} eventos)
            </span>
            <div className="flex gap-1">
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                disabled={page <= 1}
                onClick={() => router.push(buildUrl({ page: String(page - 1) }))}
              >
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                disabled={page >= data.total_pages}
                onClick={() => router.push(buildUrl({ page: String(page + 1) }))}
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>
    </PageGuard>
  );
}
