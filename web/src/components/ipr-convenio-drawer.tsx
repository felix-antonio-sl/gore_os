"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { DrawerPanel } from "@/components/drawer-panel";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DateField } from "@/components/date-field";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Link2, AlertCircle } from "lucide-react";
import { formatCLP } from "@/lib/format";
import type { CategoryRef, ConvenioListItem, PaginatedResponse } from "@/types";

interface Props {
  open: boolean;
  onClose: () => void;
  iprId: string;
  onCreated: () => void;
}

export function IprConvenioDrawer({ open, onClose, iprId, onCreated }: Props) {
  // ── Shared state ──
  const [activeTab, setActiveTab] = useState<string>("crear");

  // ── Create tab state ──
  const [agreementTypes, setAgreementTypes] = useState<CategoryRef[]>([]);
  const [agreementStates, setAgreementStates] = useState<CategoryRef[]>([]);
  const [agreementTypeId, setAgreementTypeId] = useState("");
  const [stateId, setStateId] = useState("");
  const [totalAmount, setTotalAmount] = useState("");
  const [validFrom, setValidFrom] = useState("");
  const [validTo, setValidTo] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Associate tab state ──
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<ConvenioListItem[]>([]);
  const [searching, setSearching] = useState(false);
  const [associating, setAssociating] = useState<string | null>(null);
  const [assocError, setAssocError] = useState<string | null>(null);

  // Load catalogs when drawer opens
  useEffect(() => {
    if (!open) return;
    api
      .get<CategoryRef[]>("/api/catalogs/categories/agreement_type")
      .then(setAgreementTypes)
      .catch(() => {});
    api
      .get<CategoryRef[]>("/api/catalogs/categories/agreement_state")
      .then((states) => {
        setAgreementStates(states);
        const borrador = states.find((s) => s.code === "BORRADOR");
        if (borrador) setStateId(borrador.id);
      })
      .catch(() => {});
  }, [open]);

  const resetAll = () => {
    setActiveTab("crear");
    setAgreementTypeId("");
    setStateId("");
    setTotalAmount("");
    setValidFrom("");
    setValidTo("");
    setError(null);
    setSearchTerm("");
    setSearchResults([]);
    setAssocError(null);
  };

  const handleClose = () => {
    resetAll();
    onClose();
  };

  // ── Create tab: submit ──
  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agreementTypeId || !stateId) {
      setError("Complete todos los campos requeridos.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/convenios", {
        agreement_type_id: agreementTypeId,
        state_id: stateId,
        ipr_id: iprId,
        total_amount: totalAmount ? parseFloat(totalAmount) : null,
        valid_from: validFrom || null,
        valid_to: validTo || null,
      });
      resetAll();
      onClose();
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear convenio");
    } finally {
      setSubmitting(false);
    }
  };

  // ── Associate tab: search ──
  const doSearch = useCallback(async (term: string) => {
    if (term.length < 2) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    setAssocError(null);
    try {
      const res = await api.get<PaginatedResponse<ConvenioListItem>>(
        `/api/convenios?search=${encodeURIComponent(term)}&page_size=10`
      );
      setSearchResults(res.items);
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  }, []);

  // Debounced search
  useEffect(() => {
    if (!open || activeTab !== "asociar") return;
    const timer = setTimeout(() => doSearch(searchTerm), 300);
    return () => clearTimeout(timer);
  }, [searchTerm, open, activeTab, doSearch]);

  // ── Associate tab: link convenio ──
  const handleAssociate = async (convenioId: string) => {
    setAssociating(convenioId);
    setAssocError(null);
    try {
      await api.patch(`/api/convenios/${convenioId}`, { ipr_id: iprId });
      resetAll();
      onClose();
      onCreated();
    } catch (err) {
      setAssocError(err instanceof Error ? err.message : "Error al asociar convenio");
    } finally {
      setAssociating(null);
    }
  };

  const formatAmount = (v: number | null) => v == null ? "-" : formatCLP(v);

  return (
    <DrawerPanel open={open} onClose={handleClose} title="Agregar Convenio">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full">
          <TabsTrigger value="crear" className="flex-1">
            Crear nuevo
          </TabsTrigger>
          <TabsTrigger value="asociar" className="flex-1">
            <Link2 className="size-3.5 mr-1" />
            Asociar existente
          </TabsTrigger>
        </TabsList>

        {/* ── Tab: Crear nuevo ── */}
        <TabsContent value="crear" className="mt-4">
          <form onSubmit={handleCreateSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo de convenio *</label>
              <Select value={agreementTypeId} onValueChange={setAgreementTypeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione tipo" />
                </SelectTrigger>
                <SelectContent>
                  {agreementTypes.map((at) => (
                    <SelectItem key={at.id} value={at.id}>
                      {at.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Estado *</label>
              <Select value={stateId} onValueChange={setStateId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione estado" />
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

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Monto total</label>
              <Input
                type="number"
                min="0"
                step="1"
                value={totalAmount}
                onChange={(e) => setTotalAmount(e.target.value)}
                placeholder="Monto en CLP"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Vigencia desde</label>
              <DateField
                value={validFrom}
                onChange={(v) => setValidFrom(v)}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Vigencia hasta</label>
              <DateField
                value={validTo}
                min={validFrom || undefined}
                onChange={(v) => setValidTo(v)}
              />
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear Convenio"}
              </Button>
              <Button type="button" variant="outline" onClick={handleClose}>
                Cancelar
              </Button>
            </div>
          </form>
        </TabsContent>

        {/* ── Tab: Asociar existente ── */}
        <TabsContent value="asociar" className="mt-4 space-y-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
            <Input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar por N° convenio o IPR..."
              className="pl-9"
            />
          </div>

          {searching && (
            <p className="text-xs text-muted-foreground">Buscando...</p>
          )}

          {assocError && <p className="text-sm text-red-600">{assocError}</p>}

          {searchResults.length === 0 && searchTerm.length >= 2 && !searching && (
            <p className="text-sm text-muted-foreground">Sin resultados.</p>
          )}

          {searchResults.length > 0 && (
            <div className="space-y-2">
              {searchResults.map((conv) => {
                const isLinkedToOther = conv.ipr_id !== null && conv.ipr_id !== iprId;
                const isLinkedToThis = conv.ipr_id === iprId;
                const isOrphan = conv.ipr_id === null;

                return (
                  <div
                    key={conv.id}
                    className={`rounded-lg border p-3 transition-colors ${
                      isOrphan
                        ? "hover:bg-accent cursor-pointer"
                        : "opacity-60 cursor-not-allowed"
                    }`}
                    onClick={() => {
                      if (isOrphan) handleAssociate(conv.id);
                    }}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono text-xs font-medium">
                            {conv.agreement_number ?? "Sin número"}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            {conv.agreement_type_label}
                          </Badge>
                          <StatusBadge status={conv.state} size="sm" />
                        </div>
                        {conv.total_amount != null && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {formatAmount(conv.total_amount)}
                          </p>
                        )}
                      </div>

                      <div className="shrink-0">
                        {isLinkedToOther && (
                          <div className="flex items-center gap-1 text-xs text-amber-600" title={`Vinculado a ${conv.ipr_codigo_bip}`}>
                            <AlertCircle className="size-3.5" />
                            <span>{conv.ipr_codigo_bip}</span>
                          </div>
                        )}
                        {isLinkedToThis && (
                          <span className="text-xs text-green-600">Ya vinculado</span>
                        )}
                        {isOrphan && associating === conv.id && (
                          <span className="text-xs text-muted-foreground">Vinculando...</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {searchTerm.length < 2 && (
            <p className="text-xs text-muted-foreground">
              Escriba al menos 2 caracteres para buscar convenios disponibles.
            </p>
          )}
        </TabsContent>
      </Tabs>
    </DrawerPanel>
  );
}
