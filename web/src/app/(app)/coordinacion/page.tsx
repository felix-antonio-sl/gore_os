"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Plus, AlertTriangle, Lightbulb, CheckCircle2 } from "lucide-react";
import { formatDate } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import type { PaginatedResponse, ARDecision } from "@/types";

const DECISION_TYPE_COLORS: Record<string, string> = {
  PRIORIDAD: "bg-blue-50 text-blue-700 border-blue-200",
  RECURSO: "bg-green-50 text-green-700 border-green-200",
  ESCALAMIENTO: "bg-orange-50 text-orange-700 border-orange-200",
  ESTRATEGIA: "bg-purple-50 text-purple-700 border-purple-200",
};

const STATUS_COLORS: Record<string, string> = {
  PENDIENTE: "bg-amber-50 text-amber-700 border-amber-200",
  EN_EJECUCION: "bg-blue-50 text-blue-700 border-blue-200",
  COMPLETADA: "bg-green-50 text-green-700 border-green-200",
};

interface ARPrepData {
  initiatives: { count: number; top: { id: string; code: string; name: string; status: string }[] };
  alerts: { count: number; top: { id: string; message: string; severity: string }[] };
  decisions: { count: number; top: ARDecision[] };
}

export default function CoordinacionPage() {
  const { user } = useAuth();
  const canWrite = user && ["JEFE_DGI", "ESP_CONTROL_GESTION"].includes(user.role_code);

  const [activeTab, setActiveTab] = useState("prep");
  const [prep, setPrep] = useState<ARPrepData | null>(null);
  const [prepLoading, setPrepLoading] = useState(true);

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

  const fetchPrep = () => {
    setPrepLoading(true);
    api
      .get<ARPrepData>("/api/dgi/coordination/ar/prep")
      .then(setPrep)
      .catch(() => toast.error("Error al cargar preparación AR"))
      .finally(() => setPrepLoading(false));
  };

  const fetchDecisions = () => {
    setDecisionsLoading(true);
    api
      .get<PaginatedResponse<ARDecision>>("/api/dgi/coordination/ar/decisions?page=1&page_size=50")
      .then(setDecisions)
      .catch(() => toast.error("Error al cargar decisiones"))
      .finally(() => setDecisionsLoading(false));
  };

  useEffect(() => {
    fetchPrep();
    fetchDecisions();
  }, []);

  const handleCreate = async () => {
    if (!form.description.trim()) {
      toast.error("La descripción es obligatoria");
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
      toast.success("Decisión AR creada");
      setDrawerOpen(false);
      setForm({ description: "", decision_type: "PRIORIDAD", due_date: "", context: "" });
      fetchDecisions();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear decisión");
    } finally {
      setCreating(false);
    }
  };

  const handleTransition = async (id: string, targetStatus: string) => {
    try {
      await api.patch(`/api/dgi/coordination/ar/decisions/${id}`, {
        status: targetStatus,
      });
      toast.success("Estado actualizado");
      fetchDecisions();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al actualizar");
    }
  };

  const columns = [
    {
      key: "description",
      label: "Descripción",
      render: (v: unknown) => <span className="text-sm max-w-sm line-clamp-2">{String(v)}</span>,
    },
    {
      key: "decision_type",
      label: "Tipo",
      render: (v: unknown, row: unknown) => {
        const r = row as ARDecision;
        return (
          <Badge variant="outline" className={`text-xs ${DECISION_TYPE_COLORS[r.decision_type] ?? ""}`}>
            {r.decision_type_label}
          </Badge>
        );
      },
    },
    {
      key: "status",
      label: "Estado",
      render: (v: unknown, row: unknown) => {
        const r = row as ARDecision;
        return (
          <Badge variant="outline" className={`text-xs ${STATUS_COLORS[r.status] ?? ""}`}>
            {r.status_label}
          </Badge>
        );
      },
    },
    {
      key: "responsible_name",
      label: "Responsable",
      render: (v: unknown) => <span className="text-sm">{String(v ?? "-")}</span>,
    },
    {
      key: "due_date",
      label: "Plazo",
      render: (v: unknown) => {
        if (!v) return <span className="text-xs text-muted-foreground">-</span>;
        const d = new Date(v as string);
        const now = new Date();
        const daysLeft = Math.ceil((d.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        let color = "";
        if (daysLeft < 0) color = "text-red-600 font-semibold";
        else if (daysLeft <= 3) color = "text-amber-600";
        return <span className={`text-xs ${color}`}>{formatDate(v as string)}</span>;
      },
    },
    {
      key: "actions",
      label: "",
      render: (_v: unknown, row: unknown) => {
        const r = row as ARDecision;
        if (!canWrite) return null;
        if (r.status === "PENDIENTE") {
          return (
            <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); handleTransition(r.id, "EN_EJECUCION"); }}>
              Iniciar
            </Button>
          );
        }
        if (r.status === "EN_EJECUCION") {
          return (
            <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); handleTransition(r.id, "COMPLETADA"); }}>
              Completar
            </Button>
          );
        }
        return null;
      },
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Coordinación AR"
        description="Preparación de reuniones con Administrador Regional y seguimiento de decisiones"
      />

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="prep">Preparación AR</TabsTrigger>
          <TabsTrigger value="decisions">Decisiones AR</TabsTrigger>
        </TabsList>

        <TabsContent value="prep" className="space-y-4 mt-4">
          {prepLoading ? (
            <div className="grid gap-4 sm:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-40 rounded-xl bg-muted animate-pulse" />
              ))}
            </div>
          ) : prep ? (
            <div className="grid gap-4 sm:grid-cols-3">
              {/* Initiatives card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Lightbulb className="size-4 text-blue-500" />
                    Iniciativas Activas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{prep.initiatives.count}</p>
                  <div className="mt-2 space-y-1">
                    {prep.initiatives.top.map((ini) => (
                      <p key={ini.id} className="text-xs text-muted-foreground truncate">
                        {ini.code} — {ini.name}
                      </p>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Alerts card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <AlertTriangle className="size-4 text-red-500" />
                    Alertas Pendientes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{prep.alerts.count}</p>
                  <div className="mt-2 space-y-1">
                    {prep.alerts.top.map((al) => (
                      <p key={al.id} className="text-xs text-muted-foreground truncate">
                        [{al.severity}] {al.message}
                      </p>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Decisions card */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <CheckCircle2 className="size-4 text-amber-500" />
                    Decisiones Abiertas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{prep.decisions.count}</p>
                  <div className="mt-2 space-y-1">
                    {prep.decisions.top.map((dec) => (
                      <p key={dec.id} className="text-xs text-muted-foreground truncate">
                        [{dec.decision_type_label}] {dec.description}
                      </p>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <EmptyState title="Sin datos" description="No se pudo cargar la preparación AR" />
          )}
        </TabsContent>

        <TabsContent value="decisions" className="space-y-4 mt-4">
          {canWrite && (
            <div className="flex justify-end">
              <Button size="sm" onClick={() => setDrawerOpen(true)}>
                <Plus className="size-4 mr-1" />
                Nueva Decisión
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
        </TabsContent>
      </Tabs>

      {/* Create decision drawer */}
      <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
        <SheetContent className="sm:max-w-lg overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Nueva Decisión AR</SheetTitle>
          </SheetHeader>
          <div className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label>Tipo</Label>
              <Select
                value={form.decision_type}
                onValueChange={(v) => setForm({ ...form, decision_type: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PRIORIDAD">Prioridad</SelectItem>
                  <SelectItem value="RECURSO">Recurso</SelectItem>
                  <SelectItem value="ESCALAMIENTO">Escalamiento</SelectItem>
                  <SelectItem value="ESTRATEGIA">Estrategia</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Descripción *</Label>
              <Textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Descripción de la decisión"
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label>Contexto</Label>
              <Textarea
                value={form.context}
                onChange={(e) => setForm({ ...form, context: e.target.value })}
                placeholder="Situación que motivó la decisión"
                rows={2}
              />
            </div>
            <div className="space-y-2">
              <Label>Plazo</Label>
              <Input
                type="date"
                value={form.due_date}
                onChange={(e) => setForm({ ...form, due_date: e.target.value })}
              />
            </div>
            <Button className="w-full" onClick={handleCreate} disabled={creating}>
              {creating ? "Creando..." : "Crear Decisión"}
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
