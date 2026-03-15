"use client";

import { useCallback, useEffect, useState } from "react";
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
import { ComboboxAsync, type ComboboxOption } from "@/components/combobox-async";
import { ArrowLeft } from "lucide-react";
import type { CategoryRef } from "@/types";

interface IprOption {
  id: string;
  codigo_bip: string;
  name: string;
}

export default function NuevoActoPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const [actTypes, setActTypes] = useState<CategoryRef[]>([]);
  const [resolutionTypes, setResolutionTypes] = useState<CategoryRef[]>([]);
  const [resolutionSubtypes, setResolutionSubtypes] = useState<CategoryRef[]>([]);

  const [actTypeId, setActTypeId] = useState("");
  const [actTypeCode, setActTypeCode] = useState("");
  const [subject, setSubject] = useState("");
  const [issuedAt, setIssuedAt] = useState(new Date().toISOString().split("T")[0]);
  const [requiresCgr, setRequiresCgr] = useState(false);
  const [issuerId, setIssuerId] = useState("");
  // Resolution fields
  const [resolutionTypeId, setResolutionTypeId] = useState("");
  const [resolutionSubtypeId, setResolutionSubtypeId] = useState("");
  const [iprId, setIprId] = useState("");
  const [budgetAmount, setBudgetAmount] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isResolucion = actTypeCode === "RESOLUCION";

  const canCreate =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION", "ANALISTA", "ASESOR_JURIDICO"].includes(user.role_code);

  useEffect(() => {
    api
      .get<CategoryRef[]>("/api/catalogs/categories/act_type")
      .then(setActTypes)
      .catch(() => {});
    api
      .get<CategoryRef[]>("/api/catalogs/categories/resolution_type")
      .then(setResolutionTypes)
      .catch(() => {});
    api
      .get<CategoryRef[]>("/api/catalogs/categories/resolution_subtype")
      .then(setResolutionSubtypes)
      .catch(() => {});
  }, []);

  const handleActTypeChange = (id: string) => {
    setActTypeId(id);
    const selected = actTypes.find((t) => t.id === id);
    setActTypeCode(selected?.code ?? "");
  };

  const searchOrgs = useCallback(
    async (q: string): Promise<ComboboxOption[]> => {
      const data = await api.get<
        { id: string; code: string; name: string; short_name: string }[]
      >(`/api/catalogs/organizations?search=${encodeURIComponent(q)}`);
      return data.map((org) => ({
        value: org.id,
        label: org.short_name || org.name,
      }));
    },
    []
  );

  const searchIprs = useCallback(
    async (q: string): Promise<ComboboxOption[]> => {
      const data = await api.get<IprOption[]>(
        `/api/catalogs/iprs?search=${encodeURIComponent(q)}`
      );
      return data.map((ipr) => ({
        value: ipr.id,
        label: `${ipr.codigo_bip} — ${ipr.name}`,
      }));
    },
    []
  );

  if (!canCreate) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">
          No tiene permisos para crear actos administrativos.
        </p>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actTypeId || !subject || !issuedAt) {
      setError("Complete todos los campos requeridos.");
      return;
    }
    if (isResolucion && !resolutionTypeId) {
      setError("Seleccione tipo de resolución.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/actos", {
        act_type_id: actTypeId,
        subject,
        issued_at: new Date(issuedAt).toISOString(),
        requires_cgr: requiresCgr,
        issuer_id: issuerId || null,
        resolution_type_id: isResolucion ? resolutionTypeId : null,
        resolution_subtype_id: isResolucion && resolutionSubtypeId ? resolutionSubtypeId : null,
        ipr_id: isResolucion && iprId ? iprId : null,
        budget_amount: isResolucion && budgetAmount ? parseFloat(budgetAmount) : null,
      });
      router.push("/actos");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear acto");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl">
      <Breadcrumb items={buildBreadcrumbs(pathname)} />
      <Button
        variant="ghost"
        size="sm"
        className="mb-4"
        onClick={() => router.push("/actos")}
      >
        <ArrowLeft className="size-4 mr-1" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nuevo Acto Administrativo</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo de acto *</label>
              <Select value={actTypeId} onValueChange={handleActTypeChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione tipo" />
                </SelectTrigger>
                <SelectContent>
                  {actTypes.map((t) => (
                    <SelectItem key={t.id} value={t.id}>
                      {t.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Materia *</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Describa la materia del acto..."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fecha de emisión *</label>
              <Input
                type="date"
                value={issuedAt}
                onChange={(e) => setIssuedAt(e.target.value)}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Emisor</label>
              <ComboboxAsync
                value={issuerId}
                onChange={setIssuerId}
                searchFn={searchOrgs}
                placeholder="Buscar organización..."
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="requires_cgr"
                checked={requiresCgr}
                onChange={(e) => setRequiresCgr(e.target.checked)}
                className="size-4 rounded border-input"
              />
              <label htmlFor="requires_cgr" className="text-sm font-medium">
                Requiere Toma de Razón CGR
              </label>
            </div>

            {/* Resolution-specific fields */}
            {isResolucion && (
              <div className="space-y-4 rounded-lg border p-4 bg-muted/30">
                <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">
                  Datos de Resolución
                </p>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium">
                    Tipo de resolución *
                  </label>
                  <Select
                    value={resolutionTypeId}
                    onValueChange={setResolutionTypeId}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Seleccione tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      {resolutionTypes.map((t) => (
                        <SelectItem key={t.id} value={t.id}>
                          {t.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium">
                    Subtipo (opcional)
                  </label>
                  <Select
                    value={resolutionSubtypeId}
                    onValueChange={setResolutionSubtypeId}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sin subtipo" />
                    </SelectTrigger>
                    <SelectContent>
                      {resolutionSubtypes.map((t) => (
                        <SelectItem key={t.id} value={t.id}>
                          {t.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium">IPR vinculada</label>
                  <ComboboxAsync
                    value={iprId}
                    onChange={setIprId}
                    searchFn={searchIprs}
                    placeholder="Buscar IPR por código o nombre..."
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Monto (CLP)</label>
                  <Input
                    type="number"
                    min="0"
                    value={budgetAmount}
                    onChange={(e) => setBudgetAmount(e.target.value)}
                    placeholder="Monto presupuestario"
                  />
                </div>
              </div>
            )}

            {error && <p className="text-sm text-red-600">{error}</p>}

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear Acto"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/actos")}
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
