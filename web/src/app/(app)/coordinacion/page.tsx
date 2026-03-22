"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DrawerPanel } from "@/components/drawer-panel";
import { toast } from "sonner";
import { Plus, Lightbulb, AlertTriangle, ArrowUpRight, MessageSquare } from "lucide-react";
import { formatDate, formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { useTabParam } from "@/hooks/use-tab-param";
import type {
  PaginatedResponse,
  ARDecision,
  InteractionMatrixRow,
  DivisionInteraction,
  TDSessionListItem,
  TDSessionDetail,
  TDTopicItem,
} from "@/types";

// ─── Decisiones Tab Constants ────────────────────────────────────────────────

const DECISION_TYPE_COLORS: Record<string, string> = {
  PRIORIDAD: "bg-blue-50 text-blue-700 border-blue-200",
  RECURSO: "bg-green-50 text-green-700 border-green-200",
  ESCALAMIENTO: "bg-orange-50 text-orange-700 border-orange-200",
  ESTRATEGIA: "bg-purple-50 text-purple-700 border-purple-200",
};

const DECISION_STATUS_COLORS: Record<string, string> = {
  PENDIENTE: "bg-amber-50 text-amber-700 border-amber-200",
  EN_EJECUCION: "bg-blue-50 text-blue-700 border-blue-200",
  COMPLETADA: "bg-green-50 text-green-700 border-green-200",
};

// ─── Divisiones Tab Constants ────────────────────────────────────────────────

const TYPE_LABELS: Record<string, string> = {
  PRESUPUESTO: "Presupuesto",
  CARTERA: "Cartera",
  JURIDICO: "Juridico",
  TECNOLOGIA: "Tecnologia",
  PROCESO: "Proceso",
  GENERAL: "General",
};

function daysSinceColor(dateStr: string | null): string {
  if (!dateStr) return "text-red-600";
  const days = Math.floor((Date.now() - new Date(dateStr).getTime()) / (1000 * 60 * 60 * 24));
  if (days <= 7) return "text-green-600";
  if (days <= 14) return "text-amber-600";
  return "text-red-600";
}

// ─── Comite TD Constants ─────────────────────────────────────────────────────

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

// ─── Decisiones Tab ──────────────────────────────────────────────────────────

interface ARPrepData {
  initiatives: { count: number; top: { id: string; code: string; name: string; status: string }[] };
  alerts: { count: number; top: { id: string; message: string; severity: string }[] };
  decisions: { count: number; top: ARDecision[] };
}

function DecisionesTab({ canWrite }: { canWrite: boolean }) {
  const router = useRouter();
  const [prep, setPrep] = useState<ARPrepData | null>(null);
  const [decisions, setDecisions] = useState<PaginatedResponse<ARDecision> | null>(null);
  const [decisionsLoading, setDecisionsLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  const [form, setForm] = useState({
    description: "",
    decision_type: "PRIORIDAD",
    due_date: "",
    context: "",
  });

  const fetchDecisions = () => {
    setDecisionsLoading(true);
    api
      .get<PaginatedResponse<ARDecision>>("/api/dgi/coordination/ar/decisions?page=1&page_size=50")
      .then(setDecisions)
      .catch(() => toast.error("Error al cargar decisiones"))
      .finally(() => setDecisionsLoading(false));
  };

  useEffect(() => {
    api.get<ARPrepData>("/api/dgi/coordination/ar/prep").then(setPrep).catch(() => {});
    fetchDecisions();
  }, []);

  const handleCreate = async () => {
    if (!form.description.trim()) {
      toast.error("La descripcion es obligatoria");
      return;
    }
    setCreating(true);
    try {
      await api.post("/api/dgi/coordination/ar/decisions", {
        description: form.description,
        decision_type: form.decision_type,
        due_date: form.due_date || undefined,
        context: form.context || undefined,
      });
      toast.success("Decision AR creada");
      setDrawerOpen(false);
      setForm({ description: "", decision_type: "PRIORIDAD", due_date: "", context: "" });
      fetchDecisions();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear decision");
    } finally {
      setCreating(false);
    }
  };

  const handleTransition = async (id: string, targetStatus: string) => {
    try {
      await api.patch(`/api/dgi/coordination/ar/decisions/${id}`, { status: targetStatus });
      toast.success("Estado actualizado");
      fetchDecisions();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al actualizar");
    }
  };

  const columns = [
    {
      key: "description", label: "Descripcion",
      render: (v: unknown) => <span className="text-sm max-w-sm line-clamp-2">{String(v)}</span>,
    },
    {
      key: "decision_type", label: "Tipo",
      render: (_v: unknown, row: unknown) => {
        const r = row as ARDecision;
        return <Badge variant="outline" className={`text-xs ${DECISION_TYPE_COLORS[r.decision_type] ?? ""}`}>{r.decision_type_label}</Badge>;
      },
    },
    {
      key: "status", label: "Estado",
      render: (_v: unknown, row: unknown) => {
        const r = row as ARDecision;
        return <Badge variant="outline" className={`text-xs ${DECISION_STATUS_COLORS[r.status] ?? ""}`}>{r.status_label}</Badge>;
      },
    },
    {
      key: "responsible_name", label: "Responsable",
      render: (v: unknown) => <span className="text-sm">{String(v ?? "-")}</span>,
    },
    {
      key: "due_date", label: "Plazo",
      render: (v: unknown) => {
        if (!v) return <span className="text-xs text-muted-foreground">-</span>;
        const d = new Date(v as string);
        const daysLeft = Math.ceil((d.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
        const color = daysLeft < 0 ? "text-red-600 font-semibold" : daysLeft <= 3 ? "text-amber-600" : "";
        return <span className={`text-xs ${color}`}>{formatDate(v as string)}</span>;
      },
    },
    {
      key: "actions", label: "",
      render: (_v: unknown, row: unknown) => {
        const r = row as ARDecision;
        if (!canWrite) return null;
        if (r.status === "PENDIENTE")
          return <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); handleTransition(r.id, "EN_EJECUCION"); }}>Iniciar</Button>;
        if (r.status === "EN_EJECUCION")
          return <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); handleTransition(r.id, "COMPLETADA"); }}>Completar</Button>;
        return null;
      },
    },
  ];

  return (
    <div className="space-y-4">
      {/* Compact prep summary */}
      {prep && (prep.initiatives.count > 0 || prep.alerts.count > 0) && (
        <div className="flex flex-wrap gap-3 text-xs">
          {prep.initiatives.count > 0 && (
            <button
              onClick={() => router.push("/tablero")}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition-colors dark:bg-blue-950/30 dark:text-blue-300 dark:border-blue-800"
            >
              <Lightbulb className="size-3.5" />
              {prep.initiatives.count} iniciativas activas
              <ArrowUpRight className="size-3" />
            </button>
          )}
          {prep.alerts.count > 0 && (
            <button
              onClick={() => router.push("/alertas")}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 transition-colors dark:bg-red-950/30 dark:text-red-300 dark:border-red-800"
            >
              <AlertTriangle className="size-3.5" />
              {prep.alerts.count} alertas pendientes
              <ArrowUpRight className="size-3" />
            </button>
          )}
        </div>
      )}

      {canWrite && (
        <div className="flex justify-end">
          <Button size="sm" onClick={() => setDrawerOpen(true)}>
            <Plus className="size-4 mr-1" />
            Nueva Decision
          </Button>
        </div>
      )}

      <DataTable
        columns={columns}
        data={decisions?.items ?? []}
        page={1}
        totalPages={1}
        total={decisions?.total ?? 0}
        onPageChange={() => {}}
        isLoading={decisionsLoading}
      />

      <DrawerPanel open={drawerOpen} onClose={() => setDrawerOpen(false)} title="Nueva Decision AR">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Tipo</Label>
            <Select value={form.decision_type} onValueChange={(v) => setForm({ ...form, decision_type: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="PRIORIDAD">Prioridad</SelectItem>
                <SelectItem value="RECURSO">Recurso</SelectItem>
                <SelectItem value="ESCALAMIENTO">Escalamiento</SelectItem>
                <SelectItem value="ESTRATEGIA">Estrategia</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Descripcion *</Label>
            <Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Descripcion de la decision" rows={3} />
          </div>
          <div className="space-y-2">
            <Label>Contexto</Label>
            <Textarea value={form.context} onChange={(e) => setForm({ ...form, context: e.target.value })} placeholder="Situacion que motivo la decision" rows={2} />
          </div>
          <div className="space-y-2">
            <Label>Plazo</Label>
            <Input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
          </div>
          <Button className="w-full" onClick={handleCreate} disabled={creating}>
            {creating ? "Creando..." : "Crear Decision"}
          </Button>
        </div>
      </DrawerPanel>
    </div>
  );
}

// ─── Divisiones Tab ──────────────────────────────────────────────────────────

function DivisionesTab({ canWrite }: { canWrite: boolean }) {
  const [matrix, setMatrix] = useState<InteractionMatrixRow[]>([]);
  const [matrixLoading, setMatrixLoading] = useState(true);
  const [interactions, setInteractions] = useState<PaginatedResponse<DivisionInteraction> | null>(null);
  const [intLoading, setIntLoading] = useState(true);
  const [selectedDivision, setSelectedDivision] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  const [form, setForm] = useState({
    division_id: "",
    interaction_type: "GENERAL",
    interaction_date: new Date().toISOString().split("T")[0],
    notes: "",
    next_date: "",
  });

  const fetchMatrix = () => {
    setMatrixLoading(true);
    api
      .get<InteractionMatrixRow[]>("/api/dgi/coordination/interactions/matrix")
      .then(setMatrix)
      .catch(() => toast.error("Error al cargar matriz"))
      .finally(() => setMatrixLoading(false));
  };

  const fetchInteractions = (divId?: string) => {
    setIntLoading(true);
    const divParam = divId ? `&division_id=${divId}` : "";
    api
      .get<PaginatedResponse<DivisionInteraction>>(
        `/api/dgi/coordination/interactions?page=1&page_size=50${divParam}`
      )
      .then(setInteractions)
      .catch(() => {})
      .finally(() => setIntLoading(false));
  };

  useEffect(() => {
    fetchMatrix();
    fetchInteractions();
  }, []);

  const handleDivisionClick = (divId: string) => {
    setSelectedDivision(divId === selectedDivision ? null : divId);
    fetchInteractions(divId === selectedDivision ? undefined : divId);
  };

  const handleCreate = async () => {
    if (!form.division_id) {
      toast.error("Seleccione una division");
      return;
    }
    setCreating(true);
    try {
      await api.post("/api/dgi/coordination/interactions", {
        division_id: form.division_id,
        interaction_type: form.interaction_type,
        interaction_date: form.interaction_date || undefined,
        notes: form.notes || undefined,
        next_date: form.next_date || undefined,
        topics: [],
        agreements: [],
        participants: [],
      });
      toast.success("Interaccion registrada");
      setDrawerOpen(false);
      setForm({
        division_id: "",
        interaction_type: "GENERAL",
        interaction_date: new Date().toISOString().split("T")[0],
        notes: "",
        next_date: "",
      });
      fetchMatrix();
      fetchInteractions(selectedDivision || undefined);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear interaccion");
    } finally {
      setCreating(false);
    }
  };

  const matrixColumns = [
    {
      key: "division_name",
      label: "Division",
      render: (v: unknown) => <span className="font-medium text-sm">{String(v)}</span>,
    },
    {
      key: "last_interaction",
      label: "Ultima Interaccion",
      render: (v: unknown) => {
        if (!v) return <span className="text-xs text-red-600">Sin registro</span>;
        return (
          <span className={`text-xs ${daysSinceColor(v as string)}`}>
            {formatDate(v as string)}
          </span>
        );
      },
    },
    {
      key: "next_planned",
      label: "Proxima",
      render: (v: unknown) => {
        if (!v) return <span className="text-xs text-muted-foreground">-</span>;
        return <span className="text-xs">{formatDate(v as string)}</span>;
      },
    },
    {
      key: "interaction_count",
      label: "Total",
      render: (v: unknown) => <span className="text-sm font-mono">{String(v)}</span>,
    },
    {
      key: "pending_agreements",
      label: "Acuerdos Pend.",
      render: (v: unknown) => {
        const n = Number(v);
        return (
          <Badge variant="outline" className={n > 0 ? "text-amber-700 border-amber-200" : ""}>
            {n}
          </Badge>
        );
      },
    },
    {
      key: "dominant_type",
      label: "Tipo Principal",
      render: (v: unknown) => (
        <span className="text-xs">{v ? TYPE_LABELS[String(v)] ?? String(v) : "-"}</span>
      ),
    },
  ];

  const intColumns = [
    {
      key: "division_name",
      label: "Division",
      render: (v: unknown) => <span className="text-sm">{String(v)}</span>,
    },
    {
      key: "interaction_type",
      label: "Tipo",
      render: (_v: unknown, row: unknown) => {
        const r = row as DivisionInteraction;
        return <Badge variant="outline" className="text-xs">{r.interaction_type_label}</Badge>;
      },
    },
    {
      key: "interaction_date",
      label: "Fecha",
      render: (v: unknown) => <span className="text-xs">{formatDate(v as string)}</span>,
    },
    {
      key: "topics",
      label: "Temas",
      render: (v: unknown) => {
        const topics = v as string[];
        return <span className="text-xs">{topics.length > 0 ? topics.join(", ") : "-"}</span>;
      },
    },
    {
      key: "next_date",
      label: "Proxima",
      render: (v: unknown) => <span className="text-xs">{v ? formatDate(v as string) : "-"}</span>,
    },
  ];

  return (
    <div className="space-y-6">
      {canWrite && (
        <div className="flex justify-end">
          <Button size="sm" onClick={() => setDrawerOpen(true)}>
            <Plus className="size-4 mr-1" />
            Registrar Interaccion
          </Button>
        </div>
      )}

      {/* Matrix */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Matriz de Divisiones</CardTitle>
        </CardHeader>
        <CardContent>
          {matrixLoading ? (
            <div className="h-40 bg-muted animate-pulse rounded" />
          ) : matrix.length === 0 ? (
            <EmptyState compact title="Sin datos" description="No hay divisiones registradas" />
          ) : (
            <DataTable
              columns={matrixColumns}
              data={matrix}
              page={1}
              totalPages={1}
              total={matrix.length}
              onPageChange={() => {}}
              onRowClick={(row) => handleDivisionClick((row as InteractionMatrixRow).division_id)}
              isLoading={false}
            />
          )}
        </CardContent>
      </Card>

      {/* Interaction log */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Bitacora de Interacciones
            {selectedDivision && (
              <Button
                variant="ghost"
                size="sm"
                className="ml-2"
                onClick={() => { setSelectedDivision(null); fetchInteractions(); }}
              >
                Ver todas
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={intColumns}
            data={interactions?.items ?? []}
            page={1}
            totalPages={1}
            total={interactions?.total ?? 0}
            onPageChange={() => {}}
            isLoading={intLoading}
          />
        </CardContent>
      </Card>

      {/* Create drawer */}
      <DrawerPanel open={drawerOpen} onClose={() => setDrawerOpen(false)} title="Registrar Interaccion">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Division *</Label>
            <Select value={form.division_id} onValueChange={(v) => setForm({ ...form, division_id: v })}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar division" />
              </SelectTrigger>
              <SelectContent>
                {matrix.map((m) => (
                  <SelectItem key={m.division_id} value={m.division_id}>
                    {m.division_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Tipo</Label>
            <Select value={form.interaction_type} onValueChange={(v) => setForm({ ...form, interaction_type: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {Object.entries(TYPE_LABELS).map(([code, label]) => (
                  <SelectItem key={code} value={code}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Fecha</Label>
            <Input type="date" value={form.interaction_date} onChange={(e) => setForm({ ...form, interaction_date: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label>Notas</Label>
            <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={3} />
          </div>
          <div className="space-y-2">
            <Label>Proxima reunion</Label>
            <Input type="date" value={form.next_date} onChange={(e) => setForm({ ...form, next_date: e.target.value })} />
          </div>
          <Button className="w-full" onClick={handleCreate} disabled={creating}>
            {creating ? "Registrando..." : "Registrar Interaccion"}
          </Button>
        </div>
      </DrawerPanel>
    </div>
  );
}

// ─── Comite TD Tab ───────────────────────────────────────────────────────────

function ComiteTDTab({ isDGI }: { isDGI: boolean }) {
  const [data, setData] = useState<PaginatedResponse<TDSessionListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [detail, setDetail] = useState<TDSessionDetail | null>(null);
  const [newSubject, setNewSubject] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  // Create form
  const [createDate, setCreateDate] = useState("");
  const [createDesc, setCreateDesc] = useState("");
  const [createLocation, setCreateLocation] = useState("");

  const fetchData = () => {
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
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchData(); }, [page, statusFilter]);

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
      label: "Descripcion",
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
    <div className="space-y-4">
      {isDGI && (
        <div className="flex justify-end">
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="size-4 mr-1" />
            Nueva Sesion
          </Button>
        </div>
      )}

      <div className="flex gap-2">
        {["", "PROGRAMADA", "EN_CURSO", "FINALIZADA"].map((s) => (
          <Button
            key={s}
            variant={statusFilter === s ? "default" : "outline"}
            size="sm"
            onClick={() => { setStatusFilter(s); setPage(1); }}
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
        onPageChange={setPage}
        onRowClick={handleSelect}
        isLoading={isLoading}
      />

      {/* Detail panel */}
      {detail && (
        <div className="rounded-lg border bg-card p-4 space-y-3 animate-in fade-in duration-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-sm">
                Sesion #{detail.session_number}
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
                    Iniciar Sesion
                  </Button>
                )}
                {detail.status === "EN_CURSO" && (
                  <Button size="sm" variant="outline" onClick={() => handleAction("finalizar")}>
                    Finalizar Sesion
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
        title="Nueva Sesion TD"
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
            <label className="text-sm font-medium">Descripcion</label>
            <Input
              value={createDesc}
              onChange={(e) => setCreateDesc(e.target.value)}
              placeholder="Tema principal de la sesion"
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Ubicacion</label>
            <Input
              value={createLocation}
              onChange={(e) => setCreateLocation(e.target.value)}
              placeholder="Sala, videoconferencia, etc."
              className="mt-1"
            />
          </div>
          <Button onClick={handleCreate} disabled={!createDate} className="w-full">
            Crear Sesion
          </Button>
        </div>
      </DrawerPanel>
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function CoordinacionPage() {
  const { user } = useAuth();
  const [tab, setTab] = useTabParam("decisiones");

  const canWrite = user != null && ["JEFE_DGI", "ESP_CONTROL_GESTION"].includes(user.role_code);
  const isDGI = user != null && DGI_ROLES.includes(user.role_code);

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Coordinacion"
        description="Decisiones AR, interacciones con divisiones y Comite TD"
        accentColor="cyan"
      />

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="decisiones">Decisiones</TabsTrigger>
          <TabsTrigger value="divisiones">Divisiones</TabsTrigger>
          <TabsTrigger value="comite-td">Comite TD</TabsTrigger>
        </TabsList>

        <TabsContent value="decisiones" className="mt-4">
          <DecisionesTab canWrite={canWrite} />
        </TabsContent>

        <TabsContent value="divisiones" className="mt-4">
          <DivisionesTab canWrite={canWrite} />
        </TabsContent>

        <TabsContent value="comite-td" className="mt-4">
          <ComiteTDTab isDGI={isDGI} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
