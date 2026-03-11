"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { DataTable } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
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
import { toast } from "sonner";
import { Plus } from "lucide-react";
import { formatDate } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import type { InteractionMatrixRow, PaginatedResponse, DivisionInteraction } from "@/types";

const TYPE_LABELS: Record<string, string> = {
  PRESUPUESTO: "Presupuesto",
  CARTERA: "Cartera",
  JURIDICO: "Jurídico",
  TECNOLOGIA: "Tecnología",
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

export default function DivisionesInteraccionPage() {
  const { user } = useAuth();
  const canWrite = user && ["JEFE_DGI", "ESP_CONTROL_GESTION"].includes(user.role_code);

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
      toast.error("Seleccione una división");
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
      toast.success("Interacción registrada");
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
      toast.error(err instanceof Error ? err.message : "Error al crear interacción");
    } finally {
      setCreating(false);
    }
  };

  const matrixColumns = [
    {
      key: "division_name",
      label: "División",
      render: (v: unknown) => <span className="font-medium text-sm">{String(v)}</span>,
    },
    {
      key: "last_interaction",
      label: "Última Interacción",
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
      label: "Próxima",
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
      label: "División",
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
      label: "Próxima",
      render: (v: unknown) => <span className="text-xs">{v ? formatDate(v as string) : "-"}</span>,
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Interacciones con Divisiones"
        description="Matriz de seguimiento de interacciones DGI — Divisiones"
        actions={
          canWrite ? (
            <Button size="sm" onClick={() => setDrawerOpen(true)}>
              <Plus className="size-4 mr-1" />
              Registrar Interacción
            </Button>
          ) : undefined
        }
      />

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
            Bitácora de Interacciones
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
      <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
        <SheetContent className="sm:max-w-lg overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Registrar Interacción</SheetTitle>
          </SheetHeader>
          <div className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label>División *</Label>
              <Select value={form.division_id} onValueChange={(v) => setForm({ ...form, division_id: v })}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar división" />
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
              <Label>Próxima reunión</Label>
              <Input type="date" value={form.next_date} onChange={(e) => setForm({ ...form, next_date: e.target.value })} />
            </div>
            <Button className="w-full" onClick={handleCreate} disabled={creating}>
              {creating ? "Registrando..." : "Registrar Interacción"}
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
