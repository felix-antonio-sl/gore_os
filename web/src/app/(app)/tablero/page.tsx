"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { KanbanCard } from "@/components/kanban-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { Plus, BarChart3 } from "lucide-react";
import { LeanMetricsPanel } from "./components/lean-metrics-panel";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  useDroppable,
} from "@dnd-kit/core";
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { cn } from "@/lib/utils";
import type { DGIInitiative } from "@/types";

interface UserOption {
  id: string;
  nombre: string;
  apellido_paterno: string;
}

type WipColumn = "BACKLOG" | "EN_CURSO" | "REVISION" | "COMPLETADO";

const COLUMNS: { key: WipColumn; label: string; wipLimit?: number }[] = [
  { key: "BACKLOG", label: "Backlog" },
  { key: "EN_CURSO", label: "En Curso", wipLimit: 5 },
  { key: "REVISION", label: "Revisión", wipLimit: 2 },
  { key: "COMPLETADO", label: "Completado" },
];

const COLUMN_ORDER: WipColumn[] = ["BACKLOG", "EN_CURSO", "REVISION", "COMPLETADO"];

function getColumnIndex(col: WipColumn): number {
  return COLUMN_ORDER.indexOf(col);
}

/* ── Droppable column wrapper ─────────────────────────────────────────── */
function DroppableColumn({
  id,
  children,
}: {
  id: string;
  children: React.ReactNode;
}) {
  const { setNodeRef, isOver } = useDroppable({ id });
  return (
    <div
      ref={setNodeRef}
      className={cn(
        "min-h-[120px] rounded-xl border p-2 space-y-2 transition-colors",
        isOver
          ? "bg-blue-50 border-blue-300 border-dashed"
          : "bg-gray-50 border-gray-200"
      )}
    >
      {children}
    </div>
  );
}

/* ── Sortable card wrapper ────────────────────────────────────────────── */
function SortableCard({
  id,
  children,
}: {
  id: string;
  children: React.ReactNode;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style: React.CSSProperties = {
    transform: transform
      ? `translate3d(${transform.x}px, ${transform.y}px, 0)`
      : undefined,
    transition,
    zIndex: isDragging ? 50 : undefined,
    opacity: isDragging ? 0.3 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} {...listeners} {...attributes}>
      {children}
    </div>
  );
}

export default function TableroPage() {
  const router = useRouter();
  const [initiatives, setInitiatives] = useState<DGIInitiative[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [moving, setMoving] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [metricsOpen, setMetricsOpen] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } })
  );

  // Users catalog for responsable select
  const [users, setUsers] = useState<UserOption[]>([]);

  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formTargetDate, setFormTargetDate] = useState("");
  const [formTotalDays, setFormTotalDays] = useState("");
  const [formResponsableId, setFormResponsableId] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .get<DGIInitiative[]>("/api/dgi/initiatives")
      .then(setInitiatives)
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [refreshKey]);

  useEffect(() => {
    api.get<UserOption[]>("/api/catalogs/users").then(setUsers).catch(() => {});
  }, []);

  const byColumn = (col: WipColumn) =>
    initiatives
      .filter((i) => (i.wip_column ?? "BACKLOG") === col)
      .sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0));

  function openCreate() {
    setEditingId(null);
    setFormName("");
    setFormDescription("");
    setFormTargetDate("");
    setFormTotalDays("");
    setFormResponsableId("");
    setDialogOpen(true);
  }

  function openEdit(initiative: DGIInitiative) {
    setEditingId(initiative.id);
    setFormName(initiative.name);
    setFormDescription(initiative.description ?? "");
    setFormTargetDate(initiative.target_date ?? "");
    setFormTotalDays(initiative.total_days?.toString() ?? "");
    setFormResponsableId(initiative.responsible_id ?? "");
    setDialogOpen(true);
  }

  async function handleSave() {
    if (!formName.trim()) return;
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {
        name: formName.trim(),
        description: formDescription.trim() || null,
        target_date: formTargetDate || null,
        total_days: formTotalDays ? parseInt(formTotalDays) : null,
        responsible_id: formResponsableId || null,
      };

      if (editingId) {
        await api.patch(`/api/dgi/initiatives/${editingId}`, payload);
      } else {
        await api.post("/api/dgi/initiatives", { ...payload, status: "BACKLOG" });
      }
      setDialogOpen(false);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar iniciativa");
    } finally {
      setSaving(false);
    }
  }

  async function handleMove(initiative: DGIInitiative, direction: "left" | "right") {
    const currentIdx = getColumnIndex(initiative.wip_column as WipColumn);
    const targetIdx = direction === "right" ? currentIdx + 1 : currentIdx - 1;
    if (targetIdx < 0 || targetIdx >= COLUMN_ORDER.length) return;
    const targetStatus = COLUMN_ORDER[targetIdx];

    setMoving(initiative.id);
    try {
      await api.post<DGIInitiative>(`/api/dgi/initiatives/${initiative.id}/move`, {
        status: targetStatus,
      });
      setRefreshKey((k) => k + 1);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al mover iniciativa");
    } finally {
      setMoving(null);
    }
  }

  /* ── Find which column an initiative belongs to ─────────────────────── */
  function findColumn(id: string): WipColumn | null {
    const ini = initiatives.find((i) => i.id === id);
    return ini ? ((ini.wip_column ?? "BACKLOG") as WipColumn) : null;
  }

  function handleDragStart(event: DragStartEvent) {
    setActiveId(event.active.id as string);
  }

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    setActiveId(null);
    if (!over) return;

    const activeIdStr = active.id as string;
    const overId = over.id as string;

    const sourceColumn = findColumn(activeIdStr);
    if (!sourceColumn) return;

    // Check if dropped on a column header or on another card
    const isColumnDrop = COLUMN_ORDER.includes(overId as WipColumn);
    const targetColumn = isColumnDrop
      ? (overId as WipColumn)
      : findColumn(overId);

    if (!targetColumn) return;

    if (sourceColumn === targetColumn) {
      // ── Same column: reorder ───────────────────────────────────────
      const colItems = byColumn(sourceColumn);
      const oldIndex = colItems.findIndex((i) => i.id === activeIdStr);
      const newIndex = colItems.findIndex((i) => i.id === overId);
      if (oldIndex === -1 || newIndex === -1 || oldIndex === newIndex) return;

      const reordered = arrayMove(colItems, oldIndex, newIndex);

      // Optimistic update
      setInitiatives((prev) => {
        const others = prev.filter(
          (i) => (i.wip_column ?? "BACKLOG") !== sourceColumn
        );
        return [
          ...others,
          ...reordered.map((item, idx) => ({ ...item, sort_order: idx })),
        ];
      });

      // Persist
      try {
        await api.post("/api/dgi/initiatives/reorder", {
          initiative_ids: reordered.map((i) => i.id),
        });
      } catch (err) {
        toast.error("Error al reordenar");
        setRefreshKey((k) => k + 1);
      }
    } else {
      // ── Different column: move + insert at position ────────────────
      const movedItem = initiatives.find((i) => i.id === activeIdStr);
      if (!movedItem) return;

      const targetColItems = byColumn(targetColumn);

      // Determine insertion index: drop on card → insert before it, drop on column → append
      let insertIndex = targetColItems.length;
      if (!isColumnDrop) {
        const overIndex = targetColItems.findIndex((i) => i.id === overId);
        if (overIndex !== -1) insertIndex = overIndex;
      }

      // Build new column order with the moved card inserted
      const newOrder = [...targetColItems];
      newOrder.splice(insertIndex, 0, {
        ...movedItem,
        wip_column: targetColumn,
        status: targetColumn,
      });

      // Optimistic update: remove from source, insert in target
      setInitiatives((prev) => {
        const without = prev.filter(
          (i) =>
            i.id !== activeIdStr &&
            (i.wip_column ?? "BACKLOG") !== targetColumn
        );
        return [
          ...without,
          ...newOrder.map((item, idx) => ({ ...item, sort_order: idx })),
        ];
      });

      // Persist: move first (changes status), then reorder (fixes position)
      setMoving(activeIdStr);
      try {
        await api.post<DGIInitiative>(
          `/api/dgi/initiatives/${activeIdStr}/move`,
          { status: targetColumn }
        );
        await api.post("/api/dgi/initiatives/reorder", {
          initiative_ids: newOrder.map((i) => i.id),
        });
      } catch (err) {
        toast.error(
          err instanceof Error ? err.message : "Error al mover iniciativa"
        );
        setRefreshKey((k) => k + 1);
      } finally {
        setMoving(null);
      }
    }
  }

  const activeInitiative = activeId
    ? initiatives.find((i) => i.id === activeId)
    : null;

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive">
          Error al cargar el tablero: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Tablero de Iniciativas DGI</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Gestión visual de iniciativas DMAIC en curso
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={metricsOpen ? "default" : "outline"}
            onClick={() => setMetricsOpen((v) => !v)}
          >
            <BarChart3 className="size-4 mr-1" />
            Métricas
          </Button>
          <Button size="sm" variant="outline" onClick={openCreate}>
            <Plus className="size-4 mr-1" />
            Nueva Iniciativa
          </Button>
        </div>
      </div>

      <LeanMetricsPanel open={metricsOpen} />

      {/* Kanban Board */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {COLUMNS.map((col) => (
            <div key={col.key} className="space-y-3">
              <div className="h-8 rounded bg-muted animate-pulse" />
              {Array.from({ length: 2 }).map((_, i) => (
                <div key={i} className="h-28 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ))}
        </div>
      ) : (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 items-start">
            {COLUMNS.map((col) => {
              const colItems = byColumn(col.key);
              const isOverWip =
                col.wipLimit !== undefined && colItems.length > col.wipLimit;
              const isAtCapacity =
                col.wipLimit !== undefined && colItems.length === col.wipLimit;

              return (
                <div key={col.key} className="flex flex-col gap-3">
                  {/* Column header */}
                  <div className="flex items-center gap-2 px-1">
                    <h2 className="text-sm font-semibold">{col.label}</h2>
                    <Badge
                      variant="outline"
                      className={
                        isOverWip
                          ? "border-red-400 text-red-600"
                          : isAtCapacity
                          ? "border-amber-400 text-amber-600"
                          : "border-gray-300 text-gray-600"
                      }
                    >
                      {colItems.length}
                      {col.wipLimit !== undefined && `/${col.wipLimit}`}
                    </Badge>
                    {isOverWip && (
                      <span className="text-xs text-red-600 font-medium">
                        WIP excedido
                      </span>
                    )}
                  </div>

                  {/* Column container — droppable + sortable */}
                  <DroppableColumn id={col.key}>
                    <SortableContext
                      items={colItems.map((i) => i.id)}
                      strategy={verticalListSortingStrategy}
                    >
                      {colItems.length === 0 ? (
                        <p className="text-xs text-muted-foreground text-center py-6 italic">
                          Sin iniciativas
                        </p>
                      ) : (
                        colItems.map((initiative) => (
                          <SortableCard key={initiative.id} id={initiative.id}>
                            <div
                              className={
                                moving === initiative.id
                                  ? "opacity-50 pointer-events-none"
                                  : "cursor-grab active:cursor-grabbing"
                              }
                              onClick={() => {
                                if (!moving) router.push(`/tablero/${initiative.id}`);
                              }}
                            >
                              <KanbanCard
                                initiative={initiative}
                                isFirst={col.key === "BACKLOG"}
                                isLast={col.key === "COMPLETADO"}
                                onMove={(direction) =>
                                  handleMove(initiative, direction)
                                }
                              />
                            </div>
                          </SortableCard>
                        ))
                      )}
                    </SortableContext>
                  </DroppableColumn>
                </div>
              );
            })}
          </div>

          {/* Drag overlay — shows card being dragged */}
          <DragOverlay>
            {activeInitiative ? (
              <div className="opacity-90 rotate-2 shadow-lg">
                <KanbanCard initiative={activeInitiative} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      )}

      {!isLoading && initiatives.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="text-muted-foreground text-sm">
            No hay iniciativas registradas.
          </p>
          <p className="text-muted-foreground text-xs mt-1">
            Usa el botón &quot;Nueva Iniciativa&quot; para agregar la primera.
          </p>
        </div>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{editingId ? "Editar Iniciativa" : "Nueva Iniciativa"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <div className="space-y-2">
              <label htmlFor="ini-name" className="text-sm font-medium">Nombre *</label>
              <Input
                id="ini-name"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Nombre de la iniciativa"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="ini-desc" className="text-sm font-medium">Descripción</label>
              <textarea
                id="ini-desc"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Descripción (opcional)"
                rows={3}
                className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="ini-responsable" className="text-sm font-medium">Responsable</label>
              <Select value={formResponsableId} onValueChange={setFormResponsableId}>
                <SelectTrigger id="ini-responsable">
                  <SelectValue placeholder="Seleccione responsable" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Sin asignar</SelectItem>
                  {users.map((u) => (
                    <SelectItem key={u.id} value={u.id}>
                      {u.nombre} {u.apellido_paterno}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="ini-target" className="text-sm font-medium">Fecha objetivo</label>
                <Input
                  id="ini-target"
                  type="date"
                  value={formTargetDate}
                  onChange={(e) => setFormTargetDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="ini-days" className="text-sm font-medium">Días totales</label>
                <Input
                  id="ini-days"
                  type="number"
                  value={formTotalDays}
                  onChange={(e) => setFormTotalDays(e.target.value)}
                  placeholder="ej: 30"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSave} disabled={saving || !formName.trim()}>
                {saving ? "Guardando..." : editingId ? "Guardar Cambios" : "Crear Iniciativa"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
