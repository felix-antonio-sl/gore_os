"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Trash2, Rocket, Grid3X3 } from "lucide-react";
import { toast } from "sonner";
import type { ImprovementOpportunity, ImpactEffortCell } from "@/types";

interface TabOpportunitiesProps {
  processId: string;
  canEdit?: boolean;
}

const DIMENSION_OPTIONS = ["VALOR", "DUPLICACION", "ESPERAS", "MOVIMIENTOS", "ERRORES", "AUTOMATIZACION"] as const;
const IMPACT_OPTIONS = ["ALTO", "MEDIO", "BAJO"] as const;
const EFFORT_OPTIONS = ["ALTO", "MEDIO", "BAJO"] as const;
type OpportunityStatus = ImprovementOpportunity["status"];
const STATUS_TRANSITIONS: Record<OpportunityStatus, readonly OpportunityStatus[]> = {
  PROPUESTA: ["VALIDADA", "DESCARTADA"],
  VALIDADA: ["EN_EJECUCION", "DESCARTADA"],
  EN_EJECUCION: ["IMPLEMENTADA"],
  IMPLEMENTADA: [],
  DESCARTADA: [],
};

const impactColors: Record<string, string> = {
  ALTO: "bg-red-100 text-red-800 border-red-200",
  MEDIO: "bg-amber-100 text-amber-800 border-amber-200",
  BAJO: "bg-green-100 text-green-800 border-green-200",
};

export function TabOpportunities({ processId, canEdit = false }: TabOpportunitiesProps) {
  const [items, setItems] = useState<ImprovementOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [dimension, setDimension] = useState("");
  const [description, setDescription] = useState("");
  const [impact, setImpact] = useState("");
  const [effort, setEffort] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [creatingInitiativeId, setCreatingInitiativeId] = useState<string | null>(null);
  const [showMatrix, setShowMatrix] = useState(false);
  const [matrix, setMatrix] = useState<ImpactEffortCell[]>([]);
  const [loadingMatrix, setLoadingMatrix] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .get<ImprovementOpportunity[]>(`/api/dgi/processes/${processId}/opportunities`)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  const loadMatrix = () => {
    setLoadingMatrix(true);
    api
      .get<ImpactEffortCell[]>("/api/dgi/processes/impact-effort")
      .then(setMatrix)
      .catch(() => setMatrix([]))
      .finally(() => setLoadingMatrix(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [processId]);

  const resetForm = () => {
    setDimension("");
    setDescription("");
    setImpact("");
    setEffort("");
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dimension || !description.trim() || !impact || !effort) return;
    setSubmitting(true);
    try {
      await api.post(`/api/dgi/processes/${processId}/opportunities`, {
        dimension,
        description: description.trim(),
        impact,
        effort,
      });
      toast.success("Oportunidad registrada");
      resetForm();
      setShowForm(false);
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear oportunidad");
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      await api.patch(`/api/dgi/processes/${processId}/opportunities/${id}`, {
        status: newStatus,
      });
      toast.success("Estado actualizado");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al actualizar estado");
    }
  };

  const handleCreateInitiative = async (opp: ImprovementOpportunity) => {
    setCreatingInitiativeId(opp.id);
    try {
      const initiative = await api.post<{ id: string }>("/api/dgi/initiatives", {
        name: opp.description,
        status: "BACKLOG",
      });
      try {
        await api.patch(`/api/dgi/processes/${processId}/opportunities/${opp.id}`, {
          initiative_id: initiative.id,
          status: "EN_EJECUCION",
        });
        toast.success("Iniciativa creada y vinculada");
      } catch {
        toast.error("Iniciativa creada pero no se pudo vincular. Vincule manualmente.");
      }
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear iniciativa");
    } finally {
      setCreatingInitiativeId(null);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await api.delete(`/api/dgi/processes/${processId}/opportunities/${deleteId}`);
      toast.success("Oportunidad eliminada");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al eliminar oportunidad");
    } finally {
      setDeleting(false);
      setDeleteId(null);
    }
  };

  const columns = [
    {
      key: "description",
      label: "Descripción",
      className: "text-xs max-w-xs",
      render: (v: unknown) => (
        <span className="text-xs line-clamp-2">{String(v ?? "")}</span>
      ),
    },
    {
      key: "dimension",
      label: "Dimensión",
      className: "text-xs",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "")}</Badge>
      ),
    },
    {
      key: "impact",
      label: "Impacto",
      className: "text-xs",
      render: (v: unknown) => {
        const val = String(v ?? "");
        if (!val) return <span className="text-xs text-muted-foreground">—</span>;
        return (
          <Badge variant="outline" className={`text-xs ${impactColors[val] ?? ""}`}>
            {val}
          </Badge>
        );
      },
    },
    {
      key: "effort",
      label: "Esfuerzo",
      className: "text-xs",
      render: (v: unknown) => {
        const val = String(v ?? "");
        if (!val) return <span className="text-xs text-muted-foreground">—</span>;
        return <Badge variant="outline" className="text-xs">{val}</Badge>;
      },
    },
    {
      key: "status",
      label: "Estado",
      className: "text-xs",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">{String(v ?? "")}</Badge>
      ),
    },
    {
      key: "initiative_code",
      label: "Iniciativa",
      className: "text-xs",
      render: (v: unknown) => {
        const val = v as string | null;
        if (val) return <span className="text-xs font-mono text-blue-600">{val}</span>;
        return <span className="text-xs text-muted-foreground">Sin vincular</span>;
      },
    },
    {
      key: "id",
      label: "",
      className: "w-40",
      render: (_: unknown, row: unknown) => {
        const r = row as ImprovementOpportunity;
        return (
          <div className="flex items-center gap-1">
            <Select
              value={r.status}
              onValueChange={(val) => handleStatusChange(r.id, val)}
              disabled={STATUS_TRANSITIONS[r.status].length === 0}
            >
              <SelectTrigger className="h-7 text-xs w-28">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {[r.status, ...STATUS_TRANSITIONS[r.status]].map((s) => (
                  <SelectItem key={s} value={s} className="text-xs">{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {!r.initiative_id && r.status === "VALIDADA" && (
              <Button
                size="sm"
                variant="ghost"
                className="size-7 p-0 text-muted-foreground hover:text-blue-600"
                disabled={creatingInitiativeId === r.id}
                onClick={() => handleCreateInitiative(r)}
                title="Crear Iniciativa"
              >
                <Rocket className="size-3.5" />
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              className="size-7 p-0 text-muted-foreground hover:text-red-600"
              onClick={() => setDeleteId(r.id)}
            >
              <Trash2 className="size-3.5" />
            </Button>
          </div>
        );
      },
    },
  ];

  if (!loading && items.length === 0 && !showForm) {
    return (
      <div>
        <div className="flex items-center justify-between mb-4">
          <EmptyState compact title="Sin oportunidades de mejora registradas" />
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant={showMatrix ? "secondary" : "outline"}
              onClick={() => {
                const next = !showMatrix;
                setShowMatrix(next);
                if (next) loadMatrix();
              }}
            >
              <Grid3X3 className="size-4 mr-1" />
              Matriz
            </Button>
            {canEdit && (
              <Button size="sm" onClick={() => setShowForm(true)}>
                <Plus className="size-4 mr-1" />
                Agregar Oportunidad
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {items.length} {items.length === 1 ? "oportunidad" : "oportunidades"}
        </p>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={showMatrix ? "secondary" : "outline"}
            onClick={() => {
              const next = !showMatrix;
              setShowMatrix(next);
              if (next) loadMatrix();
            }}
          >
            <Grid3X3 className="size-4 mr-1" />
            Matriz
          </Button>
          {canEdit && (
            <Button size="sm" onClick={() => { resetForm(); setShowForm(!showForm); }}>
              <Plus className="size-4 mr-1" />
              Agregar Oportunidad
            </Button>
          )}
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-4 rounded-md border p-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Dimensión *</label>
              <Select value={dimension} onValueChange={setDimension}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione dimensión" />
                </SelectTrigger>
                <SelectContent>
                  {DIMENSION_OPTIONS.map((d) => (
                    <SelectItem key={d} value={d}>{d}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Impacto *</label>
              <Select value={impact} onValueChange={setImpact}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione impacto" />
                </SelectTrigger>
                <SelectContent>
                  {IMPACT_OPTIONS.map((i) => (
                    <SelectItem key={i} value={i}>{i}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Esfuerzo *</label>
              <Select value={effort} onValueChange={setEffort}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione esfuerzo" />
                </SelectTrigger>
                <SelectContent>
                  {EFFORT_OPTIONS.map((e) => (
                    <SelectItem key={e} value={e}>{e}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripción *</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describa la oportunidad de mejora..."
            />
          </div>
          <div className="flex gap-2 pt-1">
            <Button type="submit" size="sm" disabled={submitting || !dimension || !description.trim() || !impact || !effort}>
              {submitting ? "Guardando..." : "Agregar"}
            </Button>
            <Button type="button" size="sm" variant="outline" onClick={() => setShowForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      )}

      {showMatrix && (
        <div className="mb-4 rounded-md border p-4">
          <h4 className="text-sm font-medium mb-3">Matriz Impacto/Esfuerzo</h4>
          {loadingMatrix ? (
            <div className="h-40 bg-muted animate-pulse rounded" />
          ) : (
            <div className="grid grid-cols-4 gap-1 text-xs">
              {/* Header row */}
              <div />
              <div className="text-center font-medium py-1">Bajo</div>
              <div className="text-center font-medium py-1">Medio</div>
              <div className="text-center font-medium py-1">Alto</div>
              {/* Data rows */}
              {["ALTO", "MEDIO", "BAJO"].map((impact) => (
                <div key={`row-${impact}`} className="contents">
                  <div className="font-medium py-2 flex items-center">
                    {impact}
                  </div>
                  {["BAJO", "MEDIO", "ALTO"].map((effort) => {
                    const cell = matrix.find((c) => c.impact === impact && c.effort === effort);
                    const count = cell?.count ?? 0;
                    const isQuickWin = impact === "ALTO" && effort === "BAJO";
                    return (
                      <div
                        key={`${impact}-${effort}`}
                        className={`rounded-md border p-2 text-center min-h-[48px] flex flex-col items-center justify-center ${
                          isQuickWin && count > 0
                            ? "bg-green-50 border-green-300"
                            : count > 0
                            ? "bg-blue-50 border-blue-200"
                            : "bg-gray-50 border-gray-200"
                        }`}
                      >
                        <span className="text-lg font-bold">{count}</span>
                        {isQuickWin && count > 0 && (
                          <span className="text-[10px] text-green-700 font-medium">Quick Win</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
              {/* Axis labels */}
              <div className="col-span-4 text-center text-[10px] text-muted-foreground mt-1">
                Esfuerzo &rarr;
              </div>
            </div>
          )}
          <div className="text-[10px] text-muted-foreground mt-1">&uarr; Impacto</div>
        </div>
      )}

      <DataTable
        columns={columns}
        data={items}
        page={1}
        totalPages={1}
        total={items.length}
        onPageChange={() => {}}
        isLoading={loading}
      />

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => { if (!open) setDeleteId(null); }}
        title="Eliminar oportunidad"
        description="¿Está seguro de que desea eliminar esta oportunidad de mejora? Esta acción no se puede deshacer."
        onConfirm={handleDelete}
        loading={deleting}
      />
    </div>
  );
}
