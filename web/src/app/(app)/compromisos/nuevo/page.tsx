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

interface CommitmentType {
  id: string;
  code: string;
  name: string;
  description: string | null;
  default_days: number | null;
}

interface UserOption {
  id: string;
  nombre: string;
  apellido_paterno: string;
  division_name: string | null;
}

interface IprOption {
  id: string;
  codigo_bip: string;
  name: string;
}

export default function NuevoCompromisoPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const [commitmentTypes, setCommitmentTypes] = useState<CommitmentType[]>([]);
  const [users, setUsers] = useState<UserOption[]>([]);

  const [description, setDescription] = useState("");
  const [commitmentTypeId, setCommitmentTypeId] = useState("");
  const [responsibleId, setResponsibleId] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [iprId, setIprId] = useState("");
  const [observations, setObservations] = useState("");

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
    api.get<CommitmentType[]>("/api/catalogs/commitment-types").then(setCommitmentTypes).catch(() => {});
    api.get<UserOption[]>("/api/catalogs/users").then(setUsers).catch(() => {});
  }, []);

  // Auto-set due date based on commitment type default_days
  useEffect(() => {
    if (commitmentTypeId && !dueDate) {
      const ct = commitmentTypes.find((t) => t.id === commitmentTypeId);
      if (ct?.default_days) {
        const d = new Date();
        d.setDate(d.getDate() + ct.default_days);
        setDueDate(d.toISOString().split("T")[0]);
      }
    }
  }, [commitmentTypeId, commitmentTypes, dueDate]);

  const canCreate =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);

  if (!canCreate) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">No tiene permisos para crear compromisos.</p>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description || !commitmentTypeId || !responsibleId || !dueDate) {
      setError("Complete todos los campos requeridos.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/compromisos", {
        description,
        commitment_type_id: commitmentTypeId,
        responsible_id: responsibleId,
        due_date: dueDate,
        ipr_id: iprId || null,
        observations: observations || null,
      });
      router.push("/compromisos");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear compromiso");
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
        onClick={() => router.push("/compromisos")}
      >
        <ArrowLeft className="size-4 mr-1" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nuevo Compromiso</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo de compromiso *</label>
              <Select value={commitmentTypeId} onValueChange={setCommitmentTypeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione tipo" />
                </SelectTrigger>
                <SelectContent>
                  {commitmentTypes.map((ct) => (
                    <SelectItem key={ct.id} value={ct.id}>
                      {ct.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Descripción *</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describa el compromiso..."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Responsable *</label>
              <Select value={responsibleId} onValueChange={setResponsibleId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione responsable" />
                </SelectTrigger>
                <SelectContent>
                  {users.map((u) => (
                    <SelectItem key={u.id} value={u.id}>
                      {u.nombre} {u.apellido_paterno}
                      {u.division_name ? ` (${u.division_name})` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fecha limite *</label>
              <Input
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">IPR asociada</label>
              <ComboboxAsync
                value={iprId}
                onChange={setIprId}
                searchFn={searchIprs}
                placeholder="Buscar IPR por código o nombre..."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Observaciones</label>
              <textarea
                className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={observations}
                onChange={(e) => setObservations(e.target.value)}
                placeholder="Observaciones opcionales..."
              />
            </div>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear Compromiso"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/compromisos")}
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
