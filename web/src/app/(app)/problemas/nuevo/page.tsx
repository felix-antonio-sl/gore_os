"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ComboboxAsync, type ComboboxOption } from "@/components/combobox-async";
import { ArrowLeft } from "lucide-react";
import type { CategoryRef } from "@/types";

interface IprOption {
  id: string;
  codigo_bip: string;
  name: string;
}

export default function NuevoProblemaPage() {
  const router = useRouter();

  const [problemTypes, setProblemTypes] = useState<CategoryRef[]>([]);
  const [impacts, setImpacts] = useState<CategoryRef[]>([]);

  const [iprId, setIprId] = useState("");
  const [problemTypeId, setProblemTypeId] = useState("");
  const [impactId, setImpactId] = useState("");
  const [description, setDescription] = useState("");
  const [impactDescription, setImpactDescription] = useState("");
  const [proposedSolution, setProposedSolution] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchIprs = useCallback(async (q: string): Promise<ComboboxOption[]> => {
    const data = await api.get<IprOption[]>(`/api/catalogs/iprs?search=${encodeURIComponent(q)}`);
    return data.map((ipr) => ({
      value: ipr.id,
      label: `${ipr.codigo_bip} — ${ipr.name}`,
    }));
  }, []);

  useEffect(() => {
    api.get<CategoryRef[]>("/api/catalogs/categories/problem_type").then(setProblemTypes).catch(() => {});
    api.get<CategoryRef[]>("/api/catalogs/categories/impact").then(setImpacts).catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!iprId || !problemTypeId || !description) {
      setError("Complete todos los campos requeridos.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/problemas", {
        ipr_id: iprId,
        problem_type_id: problemTypeId,
        impact_id: impactId || null,
        description,
        impact_description: impactDescription || null,
        proposed_solution: proposedSolution || null,
      });
      router.push("/problemas");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear problema");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl">
      <Button
        variant="ghost"
        size="sm"
        className="mb-4"
        onClick={() => router.push("/problemas")}
      >
        <ArrowLeft className="size-4 mr-1" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nuevo Problema</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">IPR asociada *</label>
              <ComboboxAsync
                value={iprId}
                onChange={setIprId}
                searchFn={searchIprs}
                placeholder="Buscar IPR por código o nombre..."
              />
            </div>

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
              <label className="text-sm font-medium">Descripcion del problema *</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describa el problema detectado..."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Descripcion del impacto</label>
              <textarea
                className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={impactDescription}
                onChange={(e) => setImpactDescription(e.target.value)}
                placeholder="Describa el impacto del problema..."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Solucion propuesta</label>
              <textarea
                className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={proposedSolution}
                onChange={(e) => setProposedSolution(e.target.value)}
                placeholder="Proponga una solucion..."
              />
            </div>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear Problema"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/problemas")}
              >
                Cancelar
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
