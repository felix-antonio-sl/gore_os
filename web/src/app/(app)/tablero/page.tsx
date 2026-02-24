"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { KanbanCard } from "@/components/kanban-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import type { DGIInitiative } from "@/types";

type WipColumn = "BACKLOG" | "EN_CURSO" | "REVISION" | "COMPLETADO";

const COLUMNS: { key: WipColumn; label: string; wipLimit?: number }[] = [
  { key: "BACKLOG", label: "Backlog" },
  { key: "EN_CURSO", label: "En Curso", wipLimit: 5 },
  { key: "REVISION", label: "Revisión", wipLimit: 3 },
  { key: "COMPLETADO", label: "Completado" },
];

const COLUMN_ORDER: WipColumn[] = ["BACKLOG", "EN_CURSO", "REVISION", "COMPLETADO"];

function getColumnIndex(col: WipColumn): number {
  return COLUMN_ORDER.indexOf(col);
}

export default function TableroPage() {
  const [initiatives, setInitiatives] = useState<DGIInitiative[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [moving, setMoving] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<DGIInitiative[]>("/api/dgi/initiatives")
      .then(setInitiatives)
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

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
      setInitiatives((prev) =>
        prev.map((ini) =>
          ini.id === initiative.id
            ? { ...ini, wip_column: targetStatus, status: targetStatus }
            : ini
        )
      );
    } catch (err) {
      console.error("Error moving initiative:", err);
    } finally {
      setMoving(null);
    }
  }

  const byColumn = (col: WipColumn) =>
    initiatives.filter((i) => (i.wip_column ?? "BACKLOG") === col);

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
        <Button size="sm" variant="outline" disabled>
          <Plus className="size-4 mr-1" />
          Nueva Iniciativa
        </Button>
      </div>

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
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 items-start">
          {COLUMNS.map((col) => {
            const colItems = byColumn(col.key);
            const isOverWip = col.wipLimit !== undefined && colItems.length > col.wipLimit;

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
                        : "border-gray-300 text-gray-600"
                    }
                  >
                    {colItems.length}
                    {col.wipLimit !== undefined && `/${col.wipLimit}`}
                  </Badge>
                  {isOverWip && (
                    <span className="text-xs text-red-600 font-medium">WIP excedido</span>
                  )}
                </div>

                {/* Column bg container */}
                <div className="min-h-[120px] rounded-xl bg-gray-50 border border-gray-200 p-2 space-y-2">
                  {colItems.length === 0 ? (
                    <p className="text-xs text-muted-foreground text-center py-6 italic">
                      Sin iniciativas
                    </p>
                  ) : (
                    colItems.map((initiative) => (
                      <div
                        key={initiative.id}
                        className={
                          moving === initiative.id ? "opacity-50 pointer-events-none" : ""
                        }
                      >
                        <KanbanCard
                          initiative={initiative}
                          isFirst={col.key === "BACKLOG"}
                          isLast={col.key === "COMPLETADO"}
                          onMove={(direction) => handleMove(initiative, direction)}
                        />
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!isLoading && initiatives.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="text-muted-foreground text-sm">
            No hay iniciativas registradas.
          </p>
          <p className="text-muted-foreground text-xs mt-1">
            Usa el botón "Nueva Iniciativa" para agregar la primera.
          </p>
        </div>
      )}
    </div>
  );
}
