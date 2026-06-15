"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DrawerPanel } from "@/components/drawer-panel";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import { AlertTriangle, Plus, RotateCw } from "lucide-react";

interface DivisionItem {
  id: string;
  code: string;
  name: string;
  organization_type: string | null;
  is_active: boolean;
  user_count: number;
}

export function TabDivisiones() {
  const [divisions, setDivisions] = useState<DivisionItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Detail / edit
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<DivisionItem | null>(null);
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editCode, setEditCode] = useState("");
  const [editSaving, setEditSaving] = useState(false);

  // Create mode
  const [creating, setCreating] = useState(false);
  const [newCode, setNewCode] = useState("");
  const [newName, setNewName] = useState("");
  const [createSaving, setCreateSaving] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const loadDivisions = () => {
    setIsLoading(true);
    setLoadError(null);
    api
      .get<DivisionItem[]>("/api/admin/divisiones")
      .then((res) => {
        setDivisions(res);
        setLoadError(null);
      })
      .catch((err) => {
        setDivisions([]);
        setLoadError(err instanceof Error ? err.message : "No se pudieron cargar las divisiones.");
      })
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadDivisions();
  }, []);

  const openDetail = (item: DivisionItem) => {
    setSelectedId(item.id);
    setSelectedItem(item);
    setEditing(false);
  };

  const startEdit = () => {
    if (!selectedItem) return;
    setEditName(selectedItem.name);
    setEditCode(selectedItem.code);
    setEditing(true);
  };

  const handleSaveEdit = async () => {
    if (!selectedItem) return;
    setEditSaving(true);
    try {
      const body: Record<string, string> = {};
      if (editName !== selectedItem.name) body.name = editName;
      if (editCode !== selectedItem.code) body.code = editCode;

      if (Object.keys(body).length > 0) {
        await api.patch(`/api/admin/divisiones/${selectedItem.id}`, body);
      }
      setEditing(false);
      loadDivisions();
      const updated = { ...selectedItem, ...body };
      setSelectedItem(updated);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEditSaving(false);
    }
  };

  const handleCreate = async () => {
    if (!newCode || !newName) {
      setCreateError("Código y nombre son requeridos.");
      return;
    }
    setCreateSaving(true);
    setCreateError(null);
    try {
      await api.post("/api/admin/divisiones", {
        code: newCode,
        name: newName,
      });
      setCreating(false);
      setNewCode("");
      setNewName("");
      loadDivisions();
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Error al crear");
    } finally {
      setCreateSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div />
        <Button onClick={() => setCreating(true)}>
          <Plus className="size-4 mr-1" />
          Nueva División
        </Button>
      </div>

      {/* Create inline form */}
      {creating && (
        <div className="rounded-lg border p-4 space-y-3 bg-muted/30">
          <p className="font-medium text-sm">Crear nueva división</p>
          <div className="flex gap-3">
            <div className="space-y-1 flex-1">
              <label className="text-sm font-medium">Código *</label>
              <Input
                value={newCode}
                onChange={(e) => setNewCode(e.target.value)}
                placeholder="Ej: DIPLADE"
              />
            </div>
            <div className="space-y-1 flex-[2]">
              <label className="text-sm font-medium">Nombre *</label>
              <Input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Nombre de la división"
              />
            </div>
          </div>
          {createError && <p className="text-sm text-red-600">{createError}</p>}
          <div className="flex gap-2">
            <Button size="sm" onClick={handleCreate} disabled={createSaving}>
              {createSaving ? "Creando..." : "Crear"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setCreating(false);
                setCreateError(null);
              }}
            >
              Cancelar
            </Button>
          </div>
        </div>
      )}

      {/* Table */}
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-10 rounded bg-muted animate-pulse" />
          ))}
        </div>
      ) : loadError ? (
        <div className="rounded-md border">
          <EmptyState
            icon={<AlertTriangle className="size-10 stroke-1 text-amber-500" />}
            title="No se pudieron cargar las divisiones"
            description={loadError}
            action={
              <Button variant="outline" size="sm" onClick={loadDivisions}>
                <RotateCw className="size-4 mr-1.5" />
                Reintentar
              </Button>
            }
          />
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Código</TableHead>
                <TableHead>Nombre</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Usuarios</TableHead>
                <TableHead>Estado</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {divisions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="py-12">
                    <EmptyState
                      title="Aún no hay divisiones"
                      description="Crea la primera división con el botón Nueva División."
                    />
                  </TableCell>
                </TableRow>
              ) : (
                divisions.map((d) => (
                  <TableRow
                    key={d.id}
                    className="cursor-pointer"
                    onClick={() => openDetail(d)}
                  >
                    <TableCell>
                      <span className="font-mono text-xs text-muted-foreground">{d.code}</span>
                    </TableCell>
                    <TableCell>
                      <span className="font-medium">{d.name}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground">
                        {d.organization_type ?? "-"}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs">
                        {d.user_count}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {d.is_active ? (
                        <Badge variant="default" className="bg-green-600 text-xs">
                          Activa
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-xs">
                          Inactiva
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Detail drawer */}
      <DrawerPanel
        open={!!selectedId}
        onClose={() => {
          setSelectedId(null);
          setEditing(false);
        }}
        title="Detalle de División"
      >
        {selectedItem ? (
          <div className="space-y-5">
            {!editing ? (
              <>
                <div>
                  <p className="font-mono text-xs text-muted-foreground">{selectedItem.code}</p>
                  <p className="font-semibold text-base mt-1">{selectedItem.name}</p>
                </div>

                <div className="rounded-lg border divide-y text-sm">
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Tipo</span>
                    <span>{selectedItem.organization_type ?? "-"}</span>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Usuarios</span>
                    <Badge variant="outline">{selectedItem.user_count}</Badge>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Estado</span>
                    {selectedItem.is_active ? (
                      <Badge variant="default" className="bg-green-600 text-xs">
                        Activa
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="text-xs">
                        Inactiva
                      </Badge>
                    )}
                  </div>
                </div>

                <Button size="sm" onClick={startEdit}>
                  Editar
                </Button>
              </>
            ) : (
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Código</label>
                  <Input value={editCode} onChange={(e) => setEditCode(e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Nombre</label>
                  <Input value={editName} onChange={(e) => setEditName(e.target.value)} />
                </div>
                <div className="flex gap-2 pt-2">
                  <Button size="sm" onClick={handleSaveEdit} disabled={editSaving}>
                    {editSaving ? "Guardando..." : "Guardar"}
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setEditing(false)}>
                    Cancelar
                  </Button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">Seleccione una división.</p>
        )}
      </DrawerPanel>
    </div>
  );
}
