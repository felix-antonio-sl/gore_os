"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Calendar, Users, FileText } from "lucide-react";
import { formatDateTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import { PageHeader } from "@/components/page-header";
import type { PaginatedResponse, CoreSessionListItem } from "@/types";

function StatusBadge({ status }: { status: string }) {
  switch (status) {
    case "PROGRAMADA":
      return (
        <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-blue-400 text-blue-600">
          Programada
        </Badge>
      );
    case "EN_CURSO":
      return (
        <Badge variant="default" className="text-[10px] px-1.5 py-0 bg-amber-500 animate-pulse">
          En Curso
        </Badge>
      );
    case "FINALIZADA":
      return (
        <Badge variant="default" className="text-[10px] px-1.5 py-0 bg-green-600">
          Finalizada
        </Badge>
      );
    default:
      return <Badge variant="secondary" className="text-[10px] px-1.5 py-0">{status}</Badge>;
  }
}

function SessionTypeBadge({ type }: { type: string }) {
  if (type === "EXTRAORDINARIA") {
    return <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-orange-400 text-orange-600">Extraordinaria</Badge>;
  }
  return <Badge variant="outline" className="text-[10px] px-1.5 py-0">Ordinaria</Badge>;
}

const MANAGER_ROLES = ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "SECRETARIO_EJECUTIVO"];

export default function CoreSessionsPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<CoreSessionListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [nextSession, setNextSession] = useState<CoreSessionListItem | null>(null);

  // Role awareness
  const role = user?.role_code;
  const isConsejero = role === "CONSEJERO_REGIONAL";
  const isSecretario = role === "SECRETARIO_EJECUTIVO";
  const isGobernador = role === "GOBERNADOR";
  const hasContextCard = isConsejero || isSecretario || isGobernador;

  const page = Number(searchParams.get("page") ?? "1");
  const statusFilter = searchParams.get("status") ?? "";
  const typeFilter = searchParams.get("session_type") ?? "";

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) params.delete(k);
        else params.set(k, String(v));
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  const handlePageChange = (newPage: number) => router.push(buildUrl({ page: newPage }));

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (statusFilter) params.set("status", statusFilter);
    if (typeFilter) params.set("session_type", typeFilter);

    queueMicrotask(() => {
      if (active) setIsLoading(true);
    });

    api
      .get<PaginatedResponse<CoreSessionListItem>>(`/api/core-sessions?${params.toString()}`)
      .then((response) => {
        if (active) setData(response);
      })
      .catch(() => {
        if (active) setData(null);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [page, statusFilter, typeFilter]);

  // Fetch next upcoming session (PROGRAMADA or EN_CURSO)
  useEffect(() => {
    if (!hasContextCard) return;
    // Try EN_CURSO first (active session takes priority)
    api
      .get<PaginatedResponse<CoreSessionListItem>>("/api/core-sessions?status=EN_CURSO&page_size=1")
      .then((r) => {
        if (r.items.length > 0) {
          setNextSession(r.items[0]);
        } else {
          // Fall back to next PROGRAMADA
          return api
            .get<PaginatedResponse<CoreSessionListItem>>("/api/core-sessions?status=PROGRAMADA&page_size=1")
            .then((r2) => setNextSession(r2.items[0] ?? null));
        }
      })
      .catch(() => setNextSession(null));
  }, [hasContextCard]);

  const canCreate = user && MANAGER_ROLES.includes(user.role_code);

  const columns = [
    {
      key: "session_number",
      label: "#",
      render: (v: unknown) => (
        <span className="font-mono text-xs font-medium">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "session_type",
      label: "Tipo",
      render: (v: unknown) => <SessionTypeBadge type={String(v ?? "")} />,
    },
    {
      key: "scheduled_at",
      label: "Fecha",
      render: (v: unknown) => (
        <span className="text-sm">{formatDateTime(v as string)}</span>
      ),
    },
    {
      key: "status",
      label: "Estado",
      render: (v: unknown) => <StatusBadge status={String(v ?? "")} />,
    },
    {
      key: "topic_count",
      label: "Temas",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? 0)}</Badge>
      ),
    },
    {
      key: "quorum_reached",
      label: "Quorum",
      render: (v: unknown) => (
        <span className="text-sm">
          {v === true ? "Si" : v === false ? "No" : "-"}
        </span>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Sesiones CORE"
        description={
          isConsejero
            ? "Sesiones del Consejo Regional"
            : isSecretario
              ? "Preparación y gestión de sesiones"
              : "Sesiones del Consejo Regional de Ñuble"
        }
        accentColor="violet"
        actions={
          canCreate ? (
            <Button onClick={() => router.push("/core-sessions/nueva")}>
              <Plus className="size-4 mr-1" />
              Nueva Sesión
            </Button>
          ) : undefined
        }
      />

      {/* Context card — next session */}
      {nextSession && hasContextCard && (
        <div
          className={cn(
            "rounded-lg border bg-card overflow-hidden cursor-pointer hover:bg-muted/50 transition-colors",
            nextSession.status === "EN_CURSO" && "border-l-4 border-l-amber-400"
          )}
          onClick={() => router.push(`/core-sessions/${nextSession.id}`)}
        >
          <div className="px-4 py-4">
            <div className="flex items-center gap-2 mb-3">
              <StatusBadge status={nextSession.status} />
              <SessionTypeBadge type={nextSession.session_type} />
              <span className="text-sm font-medium ml-auto">
                Sesión #{nextSession.session_number}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <Calendar className="size-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Fecha</p>
                  <p className="text-sm font-medium">{formatDateTime(nextSession.scheduled_at)}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <FileText className="size-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Temas</p>
                  <p className="text-sm font-medium">
                    {nextSession.topic_count > 0
                      ? `${nextSession.topic_count} en agenda`
                      : "Sin agenda"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Users className="size-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Quorum</p>
                  <p className="text-sm font-medium">
                    {nextSession.quorum_reached === true
                      ? "Alcanzado"
                      : nextSession.quorum_reached === false
                        ? "No alcanzado"
                        : "9/16 requerido"}
                  </p>
                </div>
              </div>
            </div>

            {isSecretario && nextSession.status === "PROGRAMADA" && nextSession.topic_count === 0 && (
              <p className="text-xs text-amber-600 mt-3 font-medium">
                Preparar agenda — agregar temas de votación
              </p>
            )}
          </div>
        </div>
      )}

      <div className="flex gap-2">
        {["", "PROGRAMADA", "EN_CURSO", "FINALIZADA"].map((s) => (
          <Button
            key={s}
            variant={statusFilter === s ? "default" : "outline"}
            size="sm"
            onClick={() => router.push(buildUrl({ status: s, page: 1 }))}
          >
            {s === "" ? "Todas" : s === "PROGRAMADA" ? "Programadas" : s === "EN_CURSO" ? "En Curso" : "Finalizadas"}
          </Button>
        ))}
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        page={page}
        totalPages={data?.total_pages ?? 1}
        total={data?.total ?? 0}
        onPageChange={handlePageChange}
        onRowClick={(row) => {
          const item = row as CoreSessionListItem;
          router.push(`/core-sessions/${item.id}`);
        }}
        isLoading={isLoading}
      />
    </div>
  );
}
