"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";

interface CategoryOption {
  id: string;
  code: string;
  label: string;
}

interface DivisionOption {
  id: string;
  name: string;
}

export default function NuevoPresupuestoPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const [divisions, setDivisions] = useState<DivisionOption[]>([]);
  const [programTypes, setProgramTypes] = useState<CategoryOption[]>([]);
  const [subtitles, setSubtitles] = useState<CategoryOption[]>([]);
  const [programCodes, setProgramCodes] = useState<CategoryOption[]>([]);

  const [fiscalYear, setFiscalYear] = useState(String(new Date().getFullYear()));
  const [divisionId, setDivisionId] = useState("");
  const [programName, setProgramName] = useState("");
  const [code, setCode] = useState("");
  const [programTypeId, setProgramTypeId] = useState("");
  const [subtitleId, setSubtitleId] = useState("");
  const [programCodeId, setProgramCodeId] = useState("");
  const [initialBudget, setInitialBudget] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canEdit = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);

  useEffect(() => {
    api.get<DivisionOption[]>("/api/catalogs/divisions").then(setDivisions).catch(() => {});
    api.get<CategoryOption[]>("/api/catalogs/categories/program_type").then(setProgramTypes).catch(() => {});
    api.get<CategoryOption[]>("/api/catalogs/categories/budget_subtitle").then(setSubtitles).catch(() => {});
    api.get<CategoryOption[]>("/api/admin/budget-program-codes").then(setProgramCodes).catch(() => {});
  }, []);

  useEffect(() => {
    if (user && !canEdit) {
      router.replace("/presupuesto");
    }
  }, [user, canEdit, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await api.post("/api/presupuesto", {
        code,
        name: programName,
        fiscal_year: parseInt(fiscalYear),
        owner_division_id: divisionId || undefined,
        program_type_id: programTypeId || undefined,
        subtitle_id: subtitleId || undefined,
        program_code_id: programCodeId || undefined,
        initial_amount: parseInt(initialBudget) || 0,
      });
      toast.success("Programa presupuestario creado");
      router.push("/presupuesto");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error al crear programa";
      setError(msg);
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (!canEdit) return null;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <Breadcrumb items={buildBreadcrumbs(pathname)} />
      <Button
        variant="ghost"
        size="sm"
        className="mb-4 gap-1"
        onClick={() => router.push("/presupuesto")}
      >
        <ArrowLeft className="size-4" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nuevo Programa Presupuestario</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Código *</label>
                <Input
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="BP-2026-001"
                  required
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Año Fiscal *</label>
                <Input
                  type="number"
                  min="2020"
                  max="2030"
                  value={fiscalYear}
                  onChange={(e) => setFiscalYear(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Nombre del Programa *</label>
              <Input
                value={programName}
                onChange={(e) => setProgramName(e.target.value)}
                placeholder="Nombre descriptivo del programa"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">División</label>
              <Select value={divisionId} onValueChange={setDivisionId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar división" />
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

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Tipo de Programa</label>
                <Select value={programTypeId} onValueChange={setProgramTypeId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    {programTypes.map((pt) => (
                      <SelectItem key={pt.id} value={pt.id}>
                        {pt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Subtítulo</label>
                <Select value={subtitleId} onValueChange={setSubtitleId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar subtítulo" />
                  </SelectTrigger>
                  <SelectContent>
                    {subtitles.map((s) => (
                      <SelectItem key={s.id} value={s.id}>
                        {s.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Programa DIPRES</label>
              <Select value={programCodeId} onValueChange={setProgramCodeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar programa DIPRES" />
                </SelectTrigger>
                <SelectContent>
                  {programCodes.map((pc) => (
                    <SelectItem key={pc.id} value={pc.id}>
                      {pc.code} — {pc.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Presupuesto Inicial (CLP)</label>
              <Input
                type="number"
                min="0"
                step="1"
                value={initialBudget}
                onChange={(e) => setInitialBudget(e.target.value)}
                placeholder="0"
              />
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear Programa"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/presupuesto")}
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
