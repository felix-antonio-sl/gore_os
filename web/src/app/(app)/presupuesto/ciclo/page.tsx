"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Circle,
  Clock,
  CheckCircle2,
  SkipForward,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";

interface TrackingItem {
  id: string;
  milestone_id: string;
  ordinal: number;
  phase: string;
  quarter: string | null;
  month_label: string;
  name: string;
  responsible: string;
  deliverable: string | null;
  fiscal_year: number;
  status: string;
  planned_date: string | null;
  completed_at: string | null;
  completed_by_name: string | null;
  notes: string | null;
}

interface CycleSummary {
  fiscal_year: number;
  total_milestones: number;
  completed: number;
  en_curso: number;
  pendiente: number;
  omitido: number;
  completion_pct: number;
}

const STATUS_CONFIG: Record<
  string,
  {
    label: string;
    variant: "secondary" | "default" | "outline" | "destructive";
    className?: string;
    icon: typeof Circle;
  }
> = {
  PENDIENTE: { label: "Pendiente", variant: "secondary", icon: Circle },
  EN_CURSO: { label: "En curso", variant: "default", icon: Clock },
  COMPLETADO: {
    label: "Completado",
    variant: "outline",
    className: "border-green-500 text-green-700 bg-green-50",
    icon: CheckCircle2,
  },
  OMITIDO: { label: "Omitido", variant: "destructive", icon: SkipForward },
};

const PHASE_LABELS: Record<string, string> = {
  "T-1": "Preparacion (T-1)",
  T: "Ejecucion (T)",
  "T+1": "Cierre (T+1)",
};

const VALID_STATUSES = ["PENDIENTE", "EN_CURSO", "COMPLETADO", "OMITIDO"];

function StatusIcon({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status];
  if (!cfg) return null;
  const Icon = cfg.icon;
  const colorClass =
    status === "PENDIENTE"
      ? "text-muted-foreground"
      : status === "EN_CURSO"
        ? "text-blue-500"
        : status === "COMPLETADO"
          ? "text-green-600"
          : "text-red-500";
  return <Icon className={`size-4 ${colorClass}`} />;
}

function StatusBadgeLocal({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status];
  if (!cfg) return <Badge variant="secondary">{status}</Badge>;
  return (
    <Badge variant={cfg.variant} className={cfg.className}>
      {cfg.label}
    </Badge>
  );
}

export default function CicloPresupuestarioPage() {
  const { user } = useAuth();
  const currentYear = new Date().getFullYear();

  const [year, setYear] = useState(currentYear);
  const [items, setItems] = useState<TrackingItem[]>([]);
  const [summary, setSummary] = useState<CycleSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [notInitialized, setNotInitialized] = useState(false);
  const [initializing, setInitializing] = useState(false);

  // Dialog state
  const [editItem, setEditItem] = useState<TrackingItem | null>(null);
  const [editStatus, setEditStatus] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const canAdmin =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"].includes(user.role_code);
  const canEdit =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION"].includes(
      user.role_code
    );

  const yearOptions: number[] = [];
  for (let y = currentYear - 2; y <= currentYear + 2; y++) {
    yearOptions.push(y);
  }

  const loadData = useCallback(async (fy: number) => {
    setLoading(true);
    setNotInitialized(false);
    try {
      const [timeline, sum] = await Promise.all([
        api.get<TrackingItem[]>(`/api/presupuesto/ciclo/${fy}`),
        api.get<CycleSummary>(`/api/presupuesto/ciclo/${fy}/resumen`),
      ]);
      setItems(timeline);
      setSummary(sum);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "";
      if (msg.includes("no inicializado") || msg.includes("404")) {
        setNotInitialized(true);
        setItems([]);
        setSummary(null);
      } else {
        toast.error("Error al cargar el ciclo presupuestario");
        setItems([]);
        setSummary(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData(year);
  }, [year, loadData]);

  const handleInitialize = async () => {
    setInitializing(true);
    try {
      await api.post(`/api/presupuesto/ciclo/${year}`);
      toast.success(`Ciclo ${year} inicializado`);
      await loadData(year);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error al inicializar ciclo"
      );
    } finally {
      setInitializing(false);
    }
  };

  const openEdit = (item: TrackingItem) => {
    setEditItem(item);
    setEditStatus(item.status);
    setEditNotes(item.notes ?? "");
  };

  const handleSave = async () => {
    if (!editItem) return;
    setSaving(true);
    try {
      await api.patch(`/api/presupuesto/ciclo/tracking/${editItem.id}`, {
        status: editStatus,
        notes: editNotes || null,
      });
      toast.success("Hito actualizado");
      setEditItem(null);
      await loadData(year);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error al actualizar hito"
      );
    } finally {
      setSaving(false);
    }
  };

  // Group items by phase
  const phases = ["T-1", "T", "T+1"];
  const grouped = phases.map((phase) => ({
    phase,
    label: PHASE_LABELS[phase] ?? phase,
    items: items.filter((i) => i.phase === phase),
  }));

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <PageHeader
        title="Ciclo Presupuestario"
        description="Timeline de hitos del ciclo presupuestario anual"
        accentColor="emerald"
      />

      {/* Year selector + summary */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            className="size-8"
            onClick={() => setYear((y) => y - 1)}
            disabled={year <= currentYear - 2}
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Select
            value={String(year)}
            onValueChange={(v) => setYear(Number(v))}
          >
            <SelectTrigger className="w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {yearOptions.map((y) => (
                <SelectItem key={y} value={String(y)}>
                  {y}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="icon"
            className="size-8"
            onClick={() => setYear((y) => y + 1)}
            disabled={year >= currentYear + 2}
          >
            <ChevronRight className="size-4" />
          </Button>
        </div>

        {summary && (
          <Badge variant="outline" className="text-sm px-3 py-1">
            {summary.completion_pct}% completado ({summary.completed}/
            {summary.total_milestones})
          </Badge>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </div>
      ) : notInitialized ? (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <p className="text-muted-foreground text-sm">
            El ciclo presupuestario {year} no ha sido inicializado.
          </p>
          {canAdmin && (
            <Button onClick={handleInitialize} disabled={initializing}>
              {initializing ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Inicializando...
                </>
              ) : (
                "Inicializar Ciclo"
              )}
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-8">
          {grouped.map((group) => (
            <div key={group.phase}>
              <h2 className="text-lg font-semibold mb-4">{group.label}</h2>
              <div className="relative pl-6 border-l-2 border-muted space-y-0">
                {group.items.map((item) => (
                  <div key={item.id} className="relative pb-6 last:pb-0">
                    {/* Timeline dot */}
                    <div className="absolute -left-[calc(1.5rem+1px)] flex items-center justify-center size-6 rounded-full bg-background border-2 border-muted">
                      <StatusIcon status={item.status} />
                    </div>

                    {/* Card */}
                    <button
                      type="button"
                      className="w-full text-left rounded-lg border p-4 hover:bg-accent/50 transition-colors cursor-pointer"
                      onClick={() => canEdit && openEdit(item)}
                      disabled={!canEdit}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-mono text-muted-foreground">
                              #{item.ordinal}
                            </span>
                            <span className="font-medium text-sm">
                              {item.name}
                            </span>
                          </div>
                          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                            <span>{item.month_label}</span>
                            <span>{item.responsible}</span>
                            {item.deliverable && (
                              <span className="italic">
                                {item.deliverable}
                              </span>
                            )}
                          </div>
                          {item.completed_at && (
                            <p className="text-xs text-muted-foreground mt-1.5">
                              Completado: {formatDate(item.completed_at)}
                              {item.completed_by_name &&
                                ` por ${item.completed_by_name}`}
                            </p>
                          )}
                          {item.notes && (
                            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                              {item.notes}
                            </p>
                          )}
                        </div>
                        <StatusBadgeLocal status={item.status} />
                      </div>
                    </button>
                  </div>
                ))}
                {group.items.length === 0 && (
                  <p className="text-sm text-muted-foreground py-2">
                    Sin hitos en esta fase
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit dialog */}
      <Dialog
        open={!!editItem}
        onOpenChange={(open) => !open && setEditItem(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editItem && (
                <>
                  #{editItem.ordinal} {editItem.name}
                </>
              )}
            </DialogTitle>
          </DialogHeader>
          {editItem && (
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Estado</label>
                <Select value={editStatus} onValueChange={setEditStatus}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {VALID_STATUSES.map((s) => (
                      <SelectItem key={s} value={s}>
                        {STATUS_CONFIG[s]?.label ?? s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Notas</label>
                <textarea
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  placeholder="Notas opcionales..."
                />
              </div>
              <div className="text-xs text-muted-foreground space-y-0.5">
                <p>Mes: {editItem.month_label}</p>
                <p>Responsable: {editItem.responsible}</p>
                {editItem.deliverable && (
                  <p>Entregable: {editItem.deliverable}</p>
                )}
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setEditItem(null)}
              disabled={saving}
            >
              Cancelar
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Guardando...
                </>
              ) : (
                "Guardar"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
