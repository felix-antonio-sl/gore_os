"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { toast } from "sonner";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowLeft } from "lucide-react";

interface CategoryOption {
  id: string;
  code: string;
  label: string;
}

interface DivisionOption {
  id: string;
  code: string;
  name: string;
}

export default function NuevaIprPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const [iprTypes, setIprTypes] = useState<CategoryOption[]>([]);
  const [statuses, setStatuses] = useState<CategoryOption[]>([]);
  const [divisions, setDivisions] = useState<DivisionOption[]>([]);
  const [mechanisms, setMechanisms] = useState<CategoryOption[]>([]);
  const [fundingSources, setFundingSources] = useState<CategoryOption[]>([]);
  const [mcdPhases, setMcdPhases] = useState<CategoryOption[]>([]);

  const [codigoBip, setCodigoBip] = useState("");
  const [name, setName] = useState("");
  const [iprTypeId, setIprTypeId] = useState("");
  const [statusId, setStatusId] = useState("");
  const [divisionId, setDivisionId] = useState("");
  const [mechanismId, setMechanismId] = useState("");
  const [fundingSourceId, setFundingSourceId] = useState("");
  const [mcdPhaseId, setMcdPhaseId] = useState("");
  const [description, setDescription] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [nameError, setNameError] = useState<string | null>(null);
  const [confirmCancelOpen, setConfirmCancelOpen] = useState(false);

  const isDirty =
    !!codigoBip ||
    !!name ||
    !!iprTypeId ||
    !!statusId ||
    !!divisionId ||
    !!mechanismId ||
    !!fundingSourceId ||
    !!mcdPhaseId ||
    !!description;

  const requestCancel = () => {
    if (isDirty) {
      setConfirmCancelOpen(true);
    } else {
      router.push("/ipr");
    }
  };

  useEffect(() => {
    api.get<CategoryOption[]>("/api/catalogs/categories/ipr_type").then(setIprTypes).catch(() => {});
    api.get<CategoryOption[]>("/api/catalogs/categories/ipr_state").then(setStatuses).catch(() => {});
    api.get<DivisionOption[]>("/api/catalogs/divisions").then(setDivisions).catch(() => {});
    api.get<CategoryOption[]>("/api/catalogs/categories/mechanism").then(setMechanisms).catch(() => {});
    api.get<CategoryOption[]>("/api/catalogs/categories/funding_source").then(setFundingSources).catch(() => {});
    api.get<CategoryOption[]>("/api/catalogs/categories/mcd_phase").then(setMcdPhases).catch(() => {});
  }, []);

  const canCreate =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"].includes(user.role_code);

  if (!canCreate) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">No tiene permisos para crear IPR.</p>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setNameError("El nombre es requerido.");
      return;
    }

    setSubmitting(true);
    setNameError(null);
    try {
      const res = await api.post<{ id: string; codigo_bip?: string }>("/api/ipr", {
        codigo_bip: codigoBip || "",
        name,
        ipr_type_id: iprTypeId || null,
        status_id: statusId || null,
        sponsor_division_id: divisionId || null,
        mechanism_id: mechanismId || null,
        funding_source_id: fundingSourceId || null,
        mcd_phase_id: mcdPhaseId || null,
        description: description || null,
      });
      toast.success(`IPR ${res.codigo_bip || codigoBip || name} creada`);
      router.push(`/ipr/${res.id}?tab=partes`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear IPR");
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
        onClick={requestCancel}
      >
        <ArrowLeft className="size-4 mr-1" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nueva IPR</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Código BIP</label>
              <Input
                value={codigoBip}
                onChange={(e) => setCodigoBip(e.target.value)}
                placeholder="Dejar vacío para auto-generar"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Nombre *</label>
              <Input
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (nameError) setNameError(null);
                }}
                placeholder="Nombre de la IPR"
                aria-invalid={!!nameError || undefined}
              />
              {nameError && <p className="text-xs text-red-600">{nameError}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo de IPR</label>
              <Select value={iprTypeId} onValueChange={setIprTypeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione tipo" />
                </SelectTrigger>
                <SelectContent>
                  {iprTypes.map((t) => (
                    <SelectItem key={t.id} value={t.id}>
                      {t.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Estado inicial</label>
              <Select value={statusId} onValueChange={setStatusId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione estado" />
                </SelectTrigger>
                <SelectContent>
                  {statuses.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">División patrocinante</label>
              <Select value={divisionId} onValueChange={setDivisionId}>
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
              <label className="text-sm font-medium">Mecanismo</label>
              <Select value={mechanismId} onValueChange={setMechanismId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione mecanismo" />
                </SelectTrigger>
                <SelectContent>
                  {mechanisms.map((m) => (
                    <SelectItem key={m.id} value={m.id}>
                      {m.code} — {m.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fuente de financiamiento</label>
              <Select value={fundingSourceId} onValueChange={setFundingSourceId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione fuente" />
                </SelectTrigger>
                <SelectContent>
                  {fundingSources.map((f) => (
                    <SelectItem key={f.id} value={f.id}>
                      {f.code} — {f.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fase MCD</label>
              <Select value={mcdPhaseId} onValueChange={setMcdPhaseId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione fase" />
                </SelectTrigger>
                <SelectContent>
                  {mcdPhases.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.code} — {p.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Descripción</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Descripción de la IPR..."
              />
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear IPR"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={requestCancel}
              >
                Cancelar
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <ConfirmDialog
        open={confirmCancelOpen}
        onOpenChange={setConfirmCancelOpen}
        title="Descartar cambios"
        description="Tienes datos sin guardar — si sales ahora se perderá lo que ingresaste."
        confirmLabel="Descartar cambios"
        cancelLabel="Seguir editando"
        variant="destructive"
        onConfirm={() => {
          setConfirmCancelOpen(false);
          router.push("/ipr");
        }}
      />
    </div>
  );
}
