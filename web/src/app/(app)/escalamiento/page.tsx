"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DrawerPanel } from "@/components/drawer-panel";
import { toast } from "sonner";
import { Plus } from "lucide-react";
import { formatDateTime } from "@/lib/format";
import { DeadlineCell } from "@/components/deadline-cell";
import { useAuth } from "@/lib/auth";
import { ESCALATION_LEVEL_COLORS, ESCALATION_STATUS_COLORS } from "@/lib/status-colors";
import { DGI_ROLES } from "@/types";
import type { PaginatedResponse, Escalation } from "@/types";

const STATUS_TABS = ["TODOS", "ABIERTO", "EN_GESTION", "RESUELTO", "CERRADO"];

export default function EscalamientoPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const canCreate = user && ["JEFE_DGI", "ESP_CONTROL_GESTION"].includes(user.role_code);

  const [data, setData] = useState<PaginatedResponse<Escalation> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  // Form state
  const [form, setForm] = useState({
    level: "NIVEL_1",
    situation: "",
    impact: "",
    recommendation: "",
  });

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

  const fetchData = () => {
    setLoading(true);
    setError(null);
    const statusParam = statusFilter && statusFilter !== "TODOS" ? `&status=${statusFilter}` : "";
    api
      .get<PaginatedResponse<Escalation>>(
        `/api/dgi/escalations?page=${page}&page_size=20${statusParam}`
      )
      .then((res) => {
        setData(res);
        setError(null);
      })
      .catch(() => {
        setData(null);
        setError("No se pudieron cargar los escalamientos.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, [page, statusFilter]);

  const handleCreate = async () => {
    if (!form.situation.trim() || !form.impact.trim()) {
      toast.error("Situación e impacto son obligatorios");
      return;
    }
    setCreating(true);
    try {
      const result = await api.post<Escalation>("/api/dgi/escalations", {
        level: form.level,
        situation: form.situation,
        impact: form.impact,
        recommendation: form.recommendation || undefined,
      });
      toast.success(`Escalamiento ${result.code} creado`);
      setDrawerOpen(false);
      setForm({ level: "NIVEL_1", situation: "", impact: "", recommendation: "" });
      router.push(`/escalamiento/${result.id}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear escalamiento");
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    {
      key: "code",
      label: "Código",
      render: (v: unknown) => <span className="font-mono text-xs">{String(v ?? "-")}</span>,
    },
    {
      key: "level",
      label: "Nivel",
      render: (v: unknown, row: unknown) => {
        const r = row as Escalation;
        return (
          <Badge variant="outline" className={`text-xs ${ESCALATION_LEVEL_COLORS[r.level] ?? ""}`}>
            {r.level_label}
          </Badge>
        );
      },
    },
    {
      key: "situation",
      label: "Situación",
      render: (v: unknown) => (
        <span className="text-sm line-clamp-2 max-w-xs">{String(v ?? "-")}</span>
      ),
    },
    {
      key: "escalated_to",
      label: "Escalado a",
      render: (v: unknown) => <span className="text-sm">{String(v ?? "-")}</span>,
    },
    {
      key: "deadline",
      label: "Plazo",
      render: (v: unknown) => <DeadlineCell date={v ? String(v) : null} />,
    },
    {
      key: "status",
      label: "Estado",
      render: (v: unknown, row: unknown) => {
        const r = row as Escalation;
        return (
          <Badge variant="outline" className={`text-xs ${ESCALATION_STATUS_COLORS[r.status] ?? ""}`}>
            {r.status_label}
          </Badge>
        );
      },
    },
    {
      key: "created_at",
      label: "Creado",
      render: (v: unknown) => <span className="text-xs">{formatDateTime(v as string)}</span>,
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Escalamientos"
        description="Protocolo de escalamiento institucional — 4 niveles"
        accentColor="orange"
        actions={
          canCreate ? (
            <Button size="sm" onClick={() => setDrawerOpen(true)}>
              <Plus className="size-4 mr-1" />
              Nuevo Escalamiento
            </Button>
          ) : undefined
        }
      />

      {/* Status filter tabs */}
      <div className="flex gap-1 flex-wrap">
        {STATUS_TABS.map((tab) => (
          <Button
            key={tab}
            variant={
              (statusFilter === tab || (!statusFilter && tab === "TODOS"))
                ? "default"
                : "outline"
            }
            size="sm"
            onClick={() =>
              router.push(
                buildUrl({ status: tab === "TODOS" ? "" : tab, page: 1 })
              )
            }
          >
            {tab === "TODOS"
              ? "Todos"
              : tab === "EN_GESTION"
                ? "En Gestión"
                : tab.charAt(0) + tab.slice(1).toLowerCase()}
          </Button>
        ))}
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        page={page}
        totalPages={data?.total_pages ?? 1}
        total={data?.total ?? 0}
        onPageChange={(p) => router.push(buildUrl({ page: p }))}
        onRowClick={(row) => router.push(`/escalamiento/${(row as Escalation).id}`)}
        isLoading={loading}
        error={error}
        onRetry={fetchData}
        hasActiveFilters={!!statusFilter && statusFilter !== "TODOS"}
        onClearFilters={() => router.push(buildUrl({ status: "", page: 1 }))}
        emptyTitle="Sin escalamientos"
        emptyDescription="Cuando se registre un escalamiento institucional, aparecerá aquí."
      />

      {/* Create drawer */}
      <DrawerPanel open={drawerOpen} onClose={() => setDrawerOpen(false)} title="Nuevo Escalamiento">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Nivel</Label>
              <Select value={form.level} onValueChange={(v) => setForm({ ...form, level: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="NIVEL_1">Nivel 1 — Jefe DGI (4h)</SelectItem>
                  <SelectItem value="NIVEL_2">Nivel 2 — Admin Regional (24h)</SelectItem>
                  <SelectItem value="NIVEL_3">Nivel 3 — AR + Mesa (48h)</SelectItem>
                  <SelectItem value="NIVEL_4">Nivel 4 — Gobernador</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Situación *</Label>
              <Textarea
                value={form.situation}
                onChange={(e) => setForm({ ...form, situation: e.target.value })}
                placeholder="Descripción de la situación que requiere escalamiento"
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label>Impacto *</Label>
              <Textarea
                value={form.impact}
                onChange={(e) => setForm({ ...form, impact: e.target.value })}
                placeholder="Impacto en la gestión institucional"
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label>Recomendación</Label>
              <Textarea
                value={form.recommendation}
                onChange={(e) => setForm({ ...form, recommendation: e.target.value })}
                placeholder="Recomendación de acción"
                rows={2}
              />
            </div>
            <Button className="w-full" onClick={handleCreate} disabled={creating}>
              {creating ? "Creando..." : "Crear Escalamiento"}
            </Button>
          </div>
      </DrawerPanel>
    </div>
  );
}
