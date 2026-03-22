"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { DrawerPanel } from "@/components/drawer-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus } from "lucide-react";
import { formatDateTime } from "@/lib/format";
import { PageHeader } from "@/components/page-header";
import type { PaginatedResponse, ReunionListItem } from "@/types";

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
  const [refreshKey, setRefreshKey] = useState(0);

  // Create drawer state
  const [createOpen, setCreateOpen] = useState(false);
  const [createScheduledAt, setCreateScheduledAt] = useState("");
  const [createLocation, setCreateLocation] = useState("");
  const [createSummary, setCreateSummary] = useState("");
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

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

  const resetCreateForm = () => {
    setCreateScheduledAt("");
    setCreateLocation("");
    setCreateSummary("");
    setCreateError(null);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createScheduledAt) {
      setCreateError("Debe indicar la fecha y hora de la reunion.");
      return;
    }

    setCreateSubmitting(true);
    setCreateError(null);
    try {
      const result = await api.post<{ id: string; session_id: string }>("/api/reuniones", {
        scheduled_at: new Date(createScheduledAt).toISOString(),
        location: createLocation || null,
        summary: createSummary || null,
      });
      setCreateOpen(false);
      resetCreateForm();
      setRefreshKey((k) => k + 1);
      router.push(`/reuniones/${result.id}`);
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Error al crear reunion");
    } finally {
      setCreateSubmitting(false);
    }
  };

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (statusFilter) params.set("status", statusFilter);

    queueMicrotask(() => {
      if (active) setIsLoading(true);
    });

    api
      .get<PaginatedResponse<ReunionListItem>>(`/api/reuniones?${params.toString()}`)
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
  }, [page, statusFilter, refreshKey]);

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
      <PageHeader
        title="Reuniones de Crisis"
        description="Sesiones del Comite de Crisis IPR"
        accentColor="violet"
        actions={
          canCreate ? (
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="size-4 mr-1" />
              Nueva Reunion
            </Button>
          ) : undefined
        }
      />

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

      {/* Create Drawer */}
      <DrawerPanel
        open={createOpen}
        onClose={() => { setCreateOpen(false); resetCreateForm(); }}
        title="Nueva Reunion de Crisis"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Fecha y hora *</label>
            <Input
              type="datetime-local"
              value={createScheduledAt}
              onChange={(e) => setCreateScheduledAt(e.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Ubicacion</label>
            <Input
              type="text"
              value={createLocation}
              onChange={(e) => setCreateLocation(e.target.value)}
              placeholder="Sala de reuniones, oficina, etc."
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Resumen / Motivo</label>
            <textarea
              className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={createSummary}
              onChange={(e) => setCreateSummary(e.target.value)}
              placeholder="Describa brevemente el motivo de la reunion..."
            />
          </div>

          {createError && (
            <p className="text-sm text-red-600">{createError}</p>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={createSubmitting}>
              {createSubmitting ? "Creando..." : "Crear Reunion"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => { setCreateOpen(false); resetCreateForm(); }}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>
    </div>
  );
}
