"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { formatDateTime } from "@/lib/format";
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Sesiones CORE</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Sesiones del Consejo Regional de Nuble
          </p>
        </div>
        {canCreate && (
          <Button onClick={() => router.push("/core-sessions/nueva")}>
            <Plus className="size-4 mr-1" />
            Nueva Sesion
          </Button>
        )}
      </div>

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
