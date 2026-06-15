"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DrawerPanel } from "@/components/drawer-panel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { ArrowLeft, Pencil } from "lucide-react";
import { cn } from "@/lib/utils";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";
import { toast } from "sonner";
import { formatDate } from "@/lib/format";
import { DGI_ROLES } from "@/types";
import type { ProcessDetail } from "@/types";
import { TabActors } from "../components/tab-actors";
import { TabRules } from "../components/tab-rules";
import { TabMetrics } from "../components/tab-metrics";
import { TabPainPoints } from "../components/tab-pain-points";
import { TabOpportunities } from "../components/tab-opportunities";

interface UserOption {
  id: string;
  nombre: string;
  apellido_paterno: string;
  division_name: string | null;
}

interface DivisionOption {
  id: string;
  name: string;
}

const PROCESS_FSM: Record<string, string[]> = {
  IDENTIFICADO: ["EN_LEVANTAMIENTO", "SUSPENDIDO"],
  EN_LEVANTAMIENTO: ["MODELADO", "SUSPENDIDO"],
  MODELADO: ["VALIDADO", "SUSPENDIDO"],
  VALIDADO: ["PUBLICADO", "SUSPENDIDO"],
  PUBLICADO: ["SUSPENDIDO"],
  SUSPENDIDO: ["IDENTIFICADO"],
};

const STATUS_LABELS: Record<string, string> = {
  IDENTIFICADO: "Identificado",
  EN_LEVANTAMIENTO: "En Levantamiento",
  MODELADO: "Modelado",
  VALIDADO: "Validado",
  PUBLICADO: "Publicado",
  SUSPENDIDO: "Suspendido",
};

const CRITICALITY_COLORS: Record<string, string> = {
  ALTO: "bg-red-50 text-red-700 border-red-200",
  MEDIO: "bg-amber-50 text-amber-700 border-amber-200",
  BAJO: "bg-green-50 text-green-700 border-green-200",
};

export default function ProcesoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
  const id = params.id as string;

  const [process, setProcess] = useState<ProcessDetail | null>(null);
  const [processLoading, setProcessLoading] = useState(true);

  const [showEdit, setShowEdit] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editScope, setEditScope] = useState("");
  const [editDivisionId, setEditDivisionId] = useState("");
  const [editCriticality, setEditCriticality] = useState("");
  const [editOwnerId, setEditOwnerId] = useState("");
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  const [divisions, setDivisions] = useState<DivisionOption[]>([]);
  const [usersList, setUsersList] = useState<UserOption[]>([]);

  const [transitionTarget, setTransitionTarget] = useState("");
  const [transSubmitting, setTransSubmitting] = useState(false);

  const [refreshKey, setRefreshKey] = useState(0);

  const canEdit = user && DGI_ROLES.includes(user.role_code);

  useEffect(() => {
    api
      .get<ProcessDetail>(`/api/dgi/processes/${id}`)
      .then(setProcess)
      .catch(() => setProcess(null))
      .finally(() => setProcessLoading(false));
  }, [id]);

  const refreshDetail = () => {
    api
      .get<ProcessDetail>(`/api/dgi/processes/${id}`)
      .then(setProcess)
      .catch(() => {});
  };

  const openEditDrawer = () => {
    if (!process) return;
    setEditName(process.name);
    setEditDescription(process.description ?? "");
    setEditScope(process.scope ?? "");
    setEditDivisionId(process.division_id ?? "");
    setEditCriticality(process.criticality);
    setEditOwnerId(process.owner_id ?? "");
    setEditError(null);
    setShowEdit(true);
    if (divisions.length === 0) {
      api.get<DivisionOption[]>("/api/catalogs/divisions").then(setDivisions).catch(() => {});
    }
    if (usersList.length === 0) {
      api.get<UserOption[]>("/api/catalogs/users").then(setUsersList).catch(() => {});
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editName.trim()) {
      setEditError("El nombre es requerido.");
      return;
    }
    setEditSubmitting(true);
    setEditError(null);
    const body: Record<string, unknown> = {};
    if (editName.trim() !== (process?.name ?? "")) body.name = editName.trim();
    if (editDescription.trim() !== (process?.description ?? "")) body.description = editDescription.trim();
    if (editScope.trim() !== (process?.scope ?? "")) body.scope = editScope.trim();
    if (editDivisionId !== (process?.division_id ?? "")) body.division_id = editDivisionId || null;
    if (editCriticality !== process?.criticality) body.criticality = editCriticality;
    if (editOwnerId !== (process?.owner_id ?? "")) body.owner_id = editOwnerId || null;
    try {
      await api.patch(`/api/dgi/processes/${id}`, body);
      setShowEdit(false);
      refreshDetail();
      setRefreshKey((k) => k + 1);
      toast.success("Proceso actualizado");
    } catch (err) {
      setEditError(err instanceof Error ? err.message : "Error al actualizar");
    } finally {
      setEditSubmitting(false);
    }
  };

  const handleTransition = async () => {
    if (!transitionTarget) return;
    setTransSubmitting(true);
    try {
      await api.patch(`/api/dgi/processes/${id}`, { status: transitionTarget });
      refreshDetail();
      setTransitionTarget("");
      setRefreshKey((k) => k + 1);
      toast.success("Estado actualizado");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al transicionar");
    } finally {
      setTransSubmitting(false);
    }
  };

  const validTransitions = process ? (PROCESS_FSM[process.status] ?? []) : [];

  if (processLoading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-40 rounded bg-muted animate-pulse" />
        <div className="h-32 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (!process) {
    return (
      <div className="p-6">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="size-4 mr-2" />
          Volver
        </Button>
        <p className="mt-4 text-muted-foreground">Proceso no encontrado.</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <Breadcrumb items={buildBreadcrumbs(pathname, process?.code ?? process?.name)} />
      <Button variant="ghost" size="sm" onClick={() => router.back()}>
        <ArrowLeft className="size-4 mr-2" />
        Volver a Procesos
      </Button>

      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="font-mono text-xs text-muted-foreground">{process.code ?? "-"}</span>
              <Badge variant="outline" className="text-xs">{process.status}</Badge>
              <Badge variant="outline" className={cn("text-xs", CRITICALITY_COLORS[process.criticality] ?? "")}>
                {process.criticality}
              </Badge>
            </div>
            <h1 className="text-xl font-bold">{process.name}</h1>
            {process.description && (
              <p className="text-sm text-muted-foreground mt-1">{process.description}</p>
            )}
          </div>
          <div className="shrink-0">
            {canEdit && (
              <Button size="sm" variant="outline" onClick={openEditDrawer}>
                <Pencil className="size-4 mr-1" />
                Editar
              </Button>
            )}
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {process.division_name && (
            <div>
              <span className="text-muted-foreground">División: </span>
              <span className="font-medium">{process.division_name}</span>
            </div>
          )}
          {process.owner_name && (
            <div>
              <span className="text-muted-foreground">Propietario: </span>
              <span className="font-medium">{process.owner_name}</span>
            </div>
          )}
          {process.scope && (
            <div>
              <span className="text-muted-foreground">Alcance: </span>
              <span className="font-medium">{process.scope}</span>
            </div>
          )}
          <div>
            <span className="text-muted-foreground">BPMN: </span>
            <span className="font-medium">{process.bpmn_count}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Creado: </span>
            <span className="font-medium">{formatDate(process.created_at)}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Actualizado: </span>
            <span className="font-medium">{formatDate(process.updated_at)}</span>
          </div>
        </div>
      </div>

      {canEdit && validTransitions.length > 0 && (
        <div className="rounded-xl border bg-card p-4">
          <h3 className="text-sm font-medium mb-3">Avanzar Estado</h3>
          <div className="flex items-end gap-3 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <Select value={transitionTarget} onValueChange={setTransitionTarget}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Seleccionar estado destino..." />
                </SelectTrigger>
                <SelectContent>
                  {validTransitions.map((s) => (
                    <SelectItem key={s} value={s}>
                      {STATUS_LABELS[s] ?? s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              size="sm"
              disabled={!transitionTarget || transSubmitting}
              onClick={handleTransition}
            >
              {transSubmitting ? "Transicionando..." : "Transicionar"}
            </Button>
          </div>
        </div>
      )}

      <Tabs defaultValue="actores">
        <TabsList className="flex-wrap">
          <TabsTrigger value="actores">Actores</TabsTrigger>
          <TabsTrigger value="reglas">Reglas</TabsTrigger>
          <TabsTrigger value="metricas">Métricas</TabsTrigger>
          <TabsTrigger value="dolor">Puntos de Dolor</TabsTrigger>
          <TabsTrigger value="oportunidades">Oportunidades</TabsTrigger>
        </TabsList>

        <TabsContent value="actores" className="mt-4">
          <TabActors key={refreshKey} processId={id} canEdit={!!canEdit} />
        </TabsContent>

        <TabsContent value="reglas" className="mt-4">
          <TabRules key={refreshKey} processId={id} canEdit={!!canEdit} />
        </TabsContent>

        <TabsContent value="metricas" className="mt-4">
          <TabMetrics key={refreshKey} processId={id} canEdit={!!canEdit} />
        </TabsContent>

        <TabsContent value="dolor" className="mt-4">
          <TabPainPoints key={refreshKey} processId={id} canEdit={!!canEdit} />
        </TabsContent>

        <TabsContent value="oportunidades" className="mt-4">
          <TabOpportunities key={refreshKey} processId={id} canEdit={!!canEdit} />
        </TabsContent>
      </Tabs>

      <DrawerPanel
        open={showEdit}
        onClose={() => setShowEdit(false)}
        title="Editar Proceso"
      >
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Nombre *</label>
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder="Nombre del proceso"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Descripción</label>
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              placeholder="Descripción del proceso"
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 min-h-[80px]"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Alcance</label>
            <Input
              value={editScope}
              onChange={(e) => setEditScope(e.target.value)}
              placeholder="Alcance del proceso"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">División</label>
            <Select value={editDivisionId} onValueChange={setEditDivisionId}>
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
            <Select value={editCriticality} onValueChange={setEditCriticality}>
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

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Propietario</label>
            <Select value={editOwnerId} onValueChange={setEditOwnerId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione propietario" />
              </SelectTrigger>
              <SelectContent>
                {usersList.map((u) => (
                  <SelectItem key={u.id} value={u.id}>
                    {u.nombre} {u.apellido_paterno}
                    {u.division_name ? ` (${u.division_name})` : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {editError && (
            <p className="text-sm text-red-600">{editError}</p>
          )}

          <div className="flex gap-2 pt-2">
            <Button type="submit" disabled={editSubmitting}>
              {editSubmitting ? "Guardando..." : "Guardar"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowEdit(false)}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </DrawerPanel>
    </div>
  );
}
