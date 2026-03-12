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

export default function NuevoConvenioPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const [agreementTypes, setAgreementTypes] = useState<CategoryRef[]>([]);
  const [agreementStates, setAgreementStates] = useState<CategoryRef[]>([]);

  const [agreementTypeId, setAgreementTypeId] = useState("");
  const [stateId, setStateId] = useState("");
  const [iprId, setIprId] = useState("");
  const [totalAmount, setTotalAmount] = useState("");
  const [validFrom, setValidFrom] = useState("");
  const [validTo, setValidTo] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canCreate = user && ["ADMIN_SISTEMA", "ADMIN_REGIONAL"].includes(user.role_code);

  useEffect(() => {
    api.get<CategoryRef[]>("/api/catalogs/categories/agreement_type").then(setAgreementTypes).catch(() => {});
    api.get<CategoryRef[]>("/api/catalogs/categories/agreement_state").then((states) => {
      setAgreementStates(states);
      const borrador = states.find((s) => s.code === "BORRADOR");
      if (borrador) setStateId(borrador.id);
    }).catch(() => {});
  }, []);

  const searchIpr = useCallback(async (query: string): Promise<ComboboxOption[]> => {
    const results = await api.get<{ id: string; codigo_bip: string; name: string }[]>(
      `/api/catalogs/iprs?search=${encodeURIComponent(query)}`
    );
    return results.map((r) => ({ value: r.id, label: `${r.codigo_bip} — ${r.name}` }));
  }, []);

  const handleSubmit = async () => {
    if (!agreementTypeId || !stateId) {
      setError("Tipo y estado son requeridos.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/convenios", {
        agreement_type_id: agreementTypeId,
        state_id: stateId,
        ipr_id: iprId || null,
        total_amount: totalAmount ? Number(totalAmount) : null,
        valid_from: validFrom || null,
        valid_to: validTo || null,
      });
      router.push("/convenios");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear convenio");
    } finally {
      setSubmitting(false);
    }
  };

  if (!canCreate) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">No tiene permisos para crear convenios.</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-4">
      <Breadcrumb items={buildBreadcrumbs(pathname)} />
      <Button variant="ghost" size="sm" onClick={() => router.push("/convenios")}>
        <ArrowLeft className="size-4 mr-1" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nuevo Convenio</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm p-3 rounded border border-red-200">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium">Tipo de Convenio *</label>
            <Select value={agreementTypeId} onValueChange={setAgreementTypeId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione tipo..." />
              </SelectTrigger>
              <SelectContent>
                {agreementTypes.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Estado Inicial *</label>
            <Select value={stateId} onValueChange={setStateId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione estado..." />
              </SelectTrigger>
              <SelectContent>
                {agreementStates.map((s) => (
                  <SelectItem key={s.id} value={s.id}>
                    {s.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">IPR Asociada</label>
            <ComboboxAsync
              value={iprId}
              onChange={setIprId}
              searchFn={searchIpr}
              placeholder="Buscar IPR por BIP..."
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Monto Total</label>
            <Input
              type="number"
              placeholder="0"
              value={totalAmount}
              onChange={(e) => setTotalAmount(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Vigencia Desde</label>
              <Input
                type="date"
                value={validFrom}
                onChange={(e) => setValidFrom(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Vigencia Hasta</label>
              <Input
                type="date"
                value={validTo}
                onChange={(e) => setValidTo(e.target.value)}
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => router.push("/convenios")}>
              Cancelar
            </Button>
            <Button onClick={handleSubmit} disabled={submitting}>
              {submitting ? "Creando..." : "Crear Convenio"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
