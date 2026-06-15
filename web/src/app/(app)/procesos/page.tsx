"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
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
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";
import { Plus } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { DGI_ROLES } from "@/types";
import type { PaginatedResponse, ProcessListItem } from "@/types";

const STATUS_OPTIONS = [
  { value: "IDENTIFICADO", label: "Identificado" },
  { value: "EN_LEVANTAMIENTO", label: "En Levantamiento" },
  { value: "MODELADO", label: "Modelado" },
  { value: "VALIDADO", label: "Validado" },
  { value: "PUBLICADO", label: "Publicado" },
  { value: "SUSPENDIDO", label: "Suspendido" },
];

const CRITICALITY_OPTIONS = [
  { value: "ALTO", label: "Alto" },
  { value: "MEDIO", label: "Medio" },
  { value: "BAJO", label: "Bajo" },
];

const CRITICALITY_COLORS: Record<string, string> = {
  ALTO: "bg-red-50 text-red-700 border-red-200",
  MEDIO: "bg-amber-50 text-amber-700 border-amber-200",
  BAJO: "bg-green-50 text-green-700 border-green-200",
};

const STATUS_LABELS: Record<string, string> = Object.fromEntries(
  STATUS_OPTIONS.map((o) => [o.value, o.label])
);

const CRITICALITY_LABELS: Record<string, string> = Object.fromEntries(
  CRITICALITY_OPTIONS.map((o) => [o.value, o.label])
);

interface DivisionOption {
  id: string;
  name: string;
}

export default function ProcesosPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<ProcessListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [showCreate, setShowCreate] = useState(false);
  const [createName, setCreateName] = useState("");
  const [createDescription, setCreateDescription] = useState("");
  const [createScope, setCreateScope] = useState("");
  const [createDivisionId, setCreateDivisionId] = useState("");
  const [createCriticality, setCreateCriticality] = useState("");
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [divisions, setDivisions] = useState<DivisionOption[]>([]);

  const canCreate = user && DGI_ROLES.includes(user.role_code);

  const page = Number(searchParams.get("page") ?? "1");
  const status = searchParams.get("status") ?? "";
  const criticality = searchParams.get("criticality") ?? "";
  const search = searchParams.get("search") ?? "";

  const filterValues: Record<string, string> = { status, criticality };

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

  const handleFilterChange = (key: string, value: string) => {
    router.push(buildUrl({ [key]: value, page: 1 }));
  };

  const handleSearchChange = (value: string) => {
    router.push(buildUrl({ search: value, page: 1 }));
  };

  const handleClear = () => router.push(pathname);
  const handlePageChange = (newPage: number) => router.push(buildUrl({ page: newPage }));

  const fetchData = useCallback(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (status) params.set("status", status);
    if (criticality) params.set("criticality", criticality);
    if (search) params.set("search", search);

    setIsLoading(true);
    setLoadError(null);
    api
      .get<PaginatedResponse<ProcessListItem>>(`/api/dgi/processes?${params.toString()}`)
      .then((res) => {
        setData(res);
        setLoadError(null);
      })
      .catch((err: Error) => {
        setData(null);
        setLoadError(err?.message || "No se pudieron cargar los procesos.");
      })
      .finally(() => setIsLoading(false));
  }, [page, status, criticality, search]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const openCreateDrawer = () => {
    setCreateName("");
    setCreateDescription("");
    setCreateScope("");
    setCreateDivisionId("");
    setCreateCriticality("");
    setCreateError(null);
    setShowCreate(true);
    if (divisions.length === 0) {
      api.get<DivisionOption[]>("/api/catalogs/divisions").then(setDivisions).catch(() => {});
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createName.trim()) {
      setCreateError("El nombre es requerido.");
      return;
    }
    setCreateSubmitting(true);
    setCreateError(null);
    const body: Record<string, unknown> = { name: createName.trim() };
    if (createDescription.trim()) body.description = createDescription.trim();
    if (createScope.trim()) body.scope = createScope.trim();
    if (createDivisionId) body.division_id = createDivisionId;
    if (createCriticality) body.criticality = createCriticality;
    try {
      await api.post("/api/dgi/processes", body);
      toast.success("Proceso creado");
      setShowCreate(false);
      fetchData();
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Error al crear proceso");
    } finally {
      setCreateSubmitting(false);
    }
  };

  const columns = [
    {
      key: "code",
      label: "Código",
      render: (v: unknown) => (
        <span className="font-mono text-xs">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "name",
      label: "Nombre",
    },
    {
      key: "division_name",
      label: "División",
    },
    {
      key: "owner_name",
      label: "Propietario",
    },
    {
      key: "status",
      label: "Estado",
      render: (v: unknown) => {
        const code = String(v ?? "");
        return (
          <Badge variant="outline" className="text-xs">{STATUS_LABELS[code] ?? code}</Badge>
        );
      },
    },
    {
      key: "criticality",
      label: "Criticidad",
      render: (v: unknown) => {
        const code = String(v ?? "");
        return (
          <Badge variant="outline" className={`text-xs ${CRITICALITY_COLORS[code] ?? ""}`}>
            {CRITICALITY_LABELS[code] ?? code}
          </Badge>
        );
      },
    },
    {
      key: "bpmn_count",
      label: "BPMN",
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Catálogo de Procesos"
        description="Gestión del catálogo de procesos institucionales"
        accentColor="cyan"
        actions={
          canCreate ? (
            <Button size="sm" onClick={openCreateDrawer}>
              <Plus className="size-4 mr-1" />
              Nuevo Proceso
            </Button>
          ) : undefined
        }
      />

      <FilterBar
        filters={[
          { key: "status", label: "Estado", options: STATUS_OPTIONS },
          { key: "criticality", label: "Criticidad", options: CRITICALITY_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar por nombre o código..."
        searchValue={search}
        onSearchChange={handleSearchChange}
      />

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        page={page}
        totalPages={data?.total_pages ?? 1}
        total={data?.total ?? 0}
        onPageChange={handlePageChange}
        onRowClick={(row) => {
          const item = row as ProcessListItem;
          router.push(`/procesos/${item.id}`);
        }}
        isLoading={isLoading}
        error={loadError}
        onRetry={fetchData}
        hasActiveFilters={Boolean(status || criticality || search)}
        onClearFilters={handleClear}
        emptyTitle="Aún no hay procesos"
        emptyDescription={canCreate ? "Crea el primer proceso institucional para comenzar." : "Cuando se registren procesos, aparecerán aquí."}
      />

      <DrawerPanel
        open={showCreate}
        onClose={() => setShowCreate(false)}
        title="Nuevo Proceso"
        isDirty={
          !createSubmitting &&
          Boolean(
            createName.trim() ||
              createDescription.trim() ||
              createScope.trim() ||
              createDivisionId ||
              createCriticality
          )
        }
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Nombre *</label>
            <Input
              value={createName}
              onChange={(e) => setCreateName(e.target.value)}
              placeholder="Nombre del proceso"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripción</label>
            <textarea
              value={createDescription}
              onChange={(e) => setCreateDescription(e.target.value)}
              placeholder="Descripción del proceso"
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 min-h-[80px]"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Alcance</label>
            <Input
              value={createScope}
              onChange={(e) => setCreateScope(e.target.value)}
              placeholder="Alcance del proceso"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">División</label>
            <Select value={createDivisionId} onValueChange={setCreateDivisionId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione división" />
              </SelectTrigger>
              <SelectContent>
                {divisions.map((d) => (
                  <SelectItem key={d.id} value={d.id}>
                    {d.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Criticidad</label>
            <Select value={createCriticality} onValueChange={setCreateCriticality}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione criticidad" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALTO">Alto</SelectItem>
                <SelectItem value="MEDIO">Medio</SelectItem>
                <SelectItem value="BAJO">Bajo</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {createError && (
            <p className="text-sm text-red-600">{createError}</p>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={createSubmitting}>
              {createSubmitting ? "Creando..." : "Crear"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowCreate(false)}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>
    </div>
  );
}
