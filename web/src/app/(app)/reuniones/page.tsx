"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import type { PaginatedResponse, ReunionListItem } from "@/types";

function formatDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    return new Intl.DateTimeFormat("es-CL", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

function StatusBadgeReunion({ status }: { status: string }) {
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

export default function ReunionesPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<ReunionListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const page = Number(searchParams.get("page") ?? "1");
  const statusFilter = searchParams.get("status") ?? "";

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
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (statusFilter) params.set("status", statusFilter);

    setIsLoading(true);
    api
      .get<PaginatedResponse<ReunionListItem>>(`/api/reuniones?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, statusFilter]);

  const canCreate =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);

  const columns = [
    {
      key: "session_number",
      label: "#",
      render: (v: unknown) => (
        <span className="font-mono text-xs font-medium">{String(v ?? "-")}</span>
      ),
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
      render: (v: unknown) => <StatusBadgeReunion status={String(v ?? "")} />,
    },
    {
      key: "summary",
      label: "Resumen",
      render: (v: unknown) => (
        <span className="text-sm line-clamp-1 max-w-[250px] text-muted-foreground">
          {String(v ?? "-")}
        </span>
      ),
    },
    {
      key: "organizer_name",
      label: "Organizador",
      render: (v: unknown) => (
        <span className="text-sm">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "topic_count",
      label: "Temas",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? 0)}</Badge>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Reuniones de Crisis</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Sesiones del Comite de Crisis IPR
          </p>
        </div>
        {canCreate && (
          <Button onClick={() => router.push("/reuniones/nueva")}>
            <Plus className="size-4 mr-1" />
            Nueva Reunion
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
          const item = row as ReunionListItem;
          router.push(`/reuniones/${item.id}`);
        }}
        isLoading={isLoading}
      />
    </div>
  );
}
