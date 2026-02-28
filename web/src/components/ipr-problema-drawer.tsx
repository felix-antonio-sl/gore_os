"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DrawerPanel } from "@/components/drawer-panel";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { CategoryRef } from "@/types";

interface Props {
  open: boolean;
  onClose: () => void;
  iprId: string;
  onCreated: () => void;
}

export function IprProblemaDrawer({ open, onClose, iprId, onCreated }: Props) {
  const [problemTypes, setProblemTypes] = useState<CategoryRef[]>([]);
  const [impacts, setImpacts] = useState<CategoryRef[]>([]);

  const [problemTypeId, setProblemTypeId] = useState("");
  const [description, setDescription] = useState("");
  const [impactId, setImpactId] = useState("");
  const [impactDescription, setImpactDescription] = useState("");
  const [proposedSolution, setProposedSolution] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    api.get<CategoryRef[]>("/api/catalogs/categories/problem_type").then(setProblemTypes).catch(() => {});
    api.get<CategoryRef[]>("/api/catalogs/categories/impact").then(setImpacts).catch(() => {});
  }, [open]);

  const resetForm = () => {
    setProblemTypeId("");
    setDescription("");
    setImpactId("");
    setImpactDescription("");
    setProposedSolution("");
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!problemTypeId || !description) {
      setError("Complete todos los campos requeridos.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/problemas", {
        ipr_id: iprId,
        problem_type_id: problemTypeId,
        impact_id: impactId && impactId !== "none" ? impactId : null,
        description,
        impact_description: impactDescription || null,
        proposed_solution: proposedSolution || null,
      });
      resetForm();
      onClose();
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear problema");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <DrawerPanel open={open} onClose={handleClose} title="Nuevo Problema">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-sm font-medium">Tipo de problema *</label>
          <Select value={problemTypeId} onValueChange={setProblemTypeId}>
            <SelectTrigger>
              <SelectValue placeholder="Seleccione tipo" />
            </SelectTrigger>
            <SelectContent>
              {problemTypes.map((pt) => (
                <SelectItem key={pt.id} value={pt.id}>
                  {pt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Descripción del problema *</label>
          <textarea
            className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describa el problema detectado..."
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Impacto</label>
          <Select value={impactId} onValueChange={setImpactId}>
            <SelectTrigger>
              <SelectValue placeholder="Seleccione impacto" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Sin especificar</SelectItem>
              {impacts.map((imp) => (
                <SelectItem key={imp.id} value={imp.id}>
                  {imp.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Descripción del impacto</label>
          <textarea
            className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={impactDescription}
            onChange={(e) => setImpactDescription(e.target.value)}
            placeholder="Describa el impacto del problema..."
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Solución propuesta</label>
          <textarea
            className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={proposedSolution}
            onChange={(e) => setProposedSolution(e.target.value)}
            placeholder="Proponga una solución..."
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="flex gap-2 pt-2">
          <Button type="submit" disabled={submitting}>
            {submitting ? "Creando..." : "Crear Problema"}
          </Button>
          <Button type="button" variant="outline" onClick={handleClose}>
            Cancelar
          </Button>
        </div>
      </form>
    </DrawerPanel>
  );
}
