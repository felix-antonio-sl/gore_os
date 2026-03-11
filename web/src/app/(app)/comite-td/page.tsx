"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DrawerPanel } from "@/components/drawer-panel";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { Plus, MessageSquare } from "lucide-react";
import { formatDateTime } from "@/lib/format";
import type { PaginatedResponse, TDSessionListItem, TDSessionDetail, TDTopicItem } from "@/types";

const DGI_ROLES = ["JEFE_DGI", "ESP_TD", "ESP_CONTROL_GESTION", "ESP_PROCESOS"];

function StatusBadgeTD({ status }: { status: string }) {
  switch (status) {
    case "PROGRAMADA":
      return (
        <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-blue-400 text-blue-600">
          Programada
        </Badge>
      );
    case "EN_CURSO":
      return (
        <Badge variant="default" className="text-[10px] px-1.5 py-0 bg-amber-500">
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

export default function ComiteTDPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const [data, setData] = useState<PaginatedResponse<TDSessionListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [detail, setDetail] = useState<TDSessionDetail | null>(null);
  const [newSubject, setNewSubject] = useState("");

  // Create form
  const [createDate, setCreateDate] = useState("");
  const [createDesc, setCreateDesc] = useState("");
  const [createLocation, setCreateLocation] = useState("");

  const page = Number(searchParams.get("page") ?? "1");
  const statusFilter = searchParams.get("status") ?? "";

  const isDGI = user && DGI_ROLES.includes(user.role_code);

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

  const fetchData = useCallback(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (statusFilter) params.set("status", statusFilter);

    setIsLoading(true);
    api
      .get<PaginatedResponse<TDSessionListItem>>(`/api/dgi/td-sessions?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, statusFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSelect = async (row: unknown) => {
    const item = row as TDSessionListItem;
    if (detail?.id === item.id) {
      setDetail(null);
      return;
    }
    try {
      const d = await api.get<TDSessionDetail>(`/api/dgi/td-sessions/${item.id}`);
      setDetail(d);
    } catch {
      setDetail(null);
    }
  };

  const refreshDetail = async () => {
    if (!detail) return;
    try {
      const d = await api.get<TDSessionDetail>(`/api/dgi/td-sessions/${detail.id}`);
      setDetail(d);
    } catch { /* handled */ }
  };

  const handleCreate = async () => {
    if (!createDate) return;
    try {
      await api.post("/api/dgi/td-sessions", {
        scheduled_at: createDate,
        description: createDesc || null,
        location: createLocation || null,
      });
      setShowCreate(false);
      setCreateDate("");
      setCreateDesc("");
      setCreateLocation("");
      fetchData();
    } catch { /* error handled by ApiClient */ }
  };

  const handleAction = async (action: "iniciar" | "finalizar") => {
    if (!detail) return;
    try {
      await api.patch(`/api/dgi/td-sessions/${detail.id}?action=${action}`, {});
      fetchData();
      refreshDetail();
    } catch { /* error handled by ApiClient */ }
  };

  const handleAddTopic = async () => {
    if (!detail || !newSubject.trim()) return;
    try {
      await api.post(`/api/dgi/td-sessions/${detail.id}/topics`, {
        subject: newSubject.trim(),
      });
      setNewSubject("");
      refreshDetail();
    } catch { /* error handled by ApiClient */ }
  };

  const handleUpdateAgreement = async (topicId: string, agreement: string) => {
    if (!detail) return;
    try {
      await api.patch(`/api/dgi/td-sessions/${detail.id}/topics/${topicId}`, {
        agreement,
      });
      refreshDetail();
    } catch { /* error handled by ApiClient */ }
  };

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
      render: (v: unknown) => <span className="text-sm">{formatDateTime(v as string)}</span>,
    },
    {
      key: "status",
      label: "Estado",
      render: (v: unknown) => <StatusBadgeTD status={String(v ?? "")} />,
    },
    {
      key: "description",
      label: "Descripción",
      render: (v: unknown) => (
        <span className="text-sm line-clamp-1 max-w-[250px] text-muted-foreground">
          {String(v ?? "-")}
        </span>
      ),
    },
    {
      key: "topic_count",
      label: "Temas",
      render: (v: unknown) => <Badge variant="outline" className="text-xs">{String(v ?? 0)}</Badge>,
    },
    {
      key: "pending_agreements",
      label: "Pendientes",
      render: (v: unknown) => {
        const n = Number(v ?? 0);
        return n > 0 ? (
          <Badge variant="destructive" className="text-xs">{n}</Badge>
        ) : (
          <span className="text-xs text-muted-foreground">0</span>
        );
      },
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Comité de Transformación Digital"
        description="Sesiones y acuerdos del equipo TD"
        actions={
          isDGI ? (
            <Button onClick={() => setShowCreate(true)}>
              <Plus className="size-4 mr-1" />
              Nueva Sesión
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
        onPageChange={(p) => router.push(buildUrl({ page: p }))}
        onRowClick={handleSelect}
        isLoading={isLoading}
      />

      {/* Detail panel — shown below table when a session is selected */}
      {detail && (
        <div className="rounded-lg border bg-card p-4 space-y-3 animate-in fade-in duration-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-sm">
                Sesión #{detail.session_number}
                <StatusBadgeTD status={detail.status} />
              </h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                {formatDateTime(detail.scheduled_at)}
                {detail.location && ` — ${detail.location}`}
              </p>
            </div>
            {isDGI && (
              <div className="flex gap-2">
                {detail.status === "PROGRAMADA" && (
                  <Button size="sm" onClick={() => handleAction("iniciar")}>
                    Iniciar Sesión
                  </Button>
                )}
                {detail.status === "EN_CURSO" && (
                  <Button size="sm" variant="outline" onClick={() => handleAction("finalizar")}>
                    Finalizar Sesión
                  </Button>
                )}
                <Button size="sm" variant="ghost" onClick={() => setDetail(null)}>
                  Cerrar
                </Button>
              </div>
            )}
          </div>

          {/* Topics */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Temas ({detail.topics.length})</h4>
            {detail.topics.length === 0 ? (
              <EmptyState compact title="Sin temas registrados" />
            ) : (
              <div className="space-y-1">
                {detail.topics.map((t: TDTopicItem) => (
                  <div key={t.id} className="flex items-start gap-2 p-2 rounded bg-muted/50 border text-sm">
                    <span className="font-mono text-xs text-muted-foreground mt-0.5">
                      {t.topic_number}.
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium">{t.subject}</p>
                      {t.agreement ? (
                        <p className="text-xs text-green-700 mt-0.5">
                          <MessageSquare className="size-3 inline mr-1" />
                          {t.agreement}
                        </p>
                      ) : isDGI && detail.status !== "FINALIZADA" ? (
                        <AgreementInput
                          onSave={(val) => handleUpdateAgreement(t.id, val)}
                        />
                      ) : (
                        <p className="text-xs text-muted-foreground mt-0.5 italic">
                          Sin acuerdo
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Add topic */}
            {isDGI && detail.status !== "FINALIZADA" && (
              <div className="flex gap-2 mt-2">
                <Input
                  placeholder="Nuevo tema..."
                  value={newSubject}
                  onChange={(e) => setNewSubject(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleAddTopic()}
                  className="text-sm"
                />
                <Button size="sm" onClick={handleAddTopic}>
                  Agregar
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Drawer */}
      <DrawerPanel
        open={showCreate}
        onClose={() => setShowCreate(false)}
        title="Nueva Sesión TD"
      >
        <div className="space-y-4 p-4">
          <div>
            <label className="text-sm font-medium">Fecha y hora *</label>
            <Input
              type="datetime-local"
              value={createDate}
              onChange={(e) => setCreateDate(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Descripción</label>
            <Input
              value={createDesc}
              onChange={(e) => setCreateDesc(e.target.value)}
              placeholder="Tema principal de la sesión"
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Ubicación</label>
            <Input
              value={createLocation}
              onChange={(e) => setCreateLocation(e.target.value)}
              placeholder="Sala, videoconferencia, etc."
              className="mt-1"
            />
          </div>
          <Button onClick={handleCreate} disabled={!createDate} className="w-full">
            Crear Sesión
          </Button>
        </div>
      </DrawerPanel>
    </div>
  );
}

function AgreementInput({ onSave }: { onSave: (val: string) => void }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState("");

  if (!editing) {
    return (
      <button
        onClick={() => setEditing(true)}
        className="text-xs text-blue-600 hover:underline mt-0.5"
      >
        + Registrar acuerdo
      </button>
    );
  }

  return (
    <div className="flex gap-1 mt-1">
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && value.trim()) {
            onSave(value.trim());
            setEditing(false);
            setValue("");
          }
        }}
        placeholder="Acuerdo..."
        className="text-xs h-7"
        autoFocus
      />
      <Button
        size="sm"
        className="h-7 text-xs"
        onClick={() => {
          if (value.trim()) {
            onSave(value.trim());
            setEditing(false);
            setValue("");
          }
        }}
      >
        OK
      </Button>
    </div>
  );
}
