"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { searchIprs, searchUsers } from "@/lib/catalog-search";
import { DrawerPanel } from "@/components/drawer-panel";
import { DateField } from "@/components/date-field";
import { ComboboxAsync } from "@/components/combobox-async";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface CommitmentType {
  id: string;
  code: string;
  name: string;
  description: string | null;
  default_days: number | null;
}

interface Props {
  open: boolean;
  onClose: () => void;
  iprId?: string;
  onCreated: () => void;
}

export function CompromisoCreateDrawer({ open, onClose, iprId, onCreated }: Props) {
  const [commitmentTypes, setCommitmentTypes] = useState<CommitmentType[]>([]);

  const [commitmentTypeId, setCommitmentTypeId] = useState("");
  const [description, setDescription] = useState("");
  const [responsibleId, setResponsibleId] = useState("");
  const [selectedIprId, setSelectedIprId] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [observations, setObservations] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!open) return;
    api
      .get<CommitmentType[]>("/api/catalogs/commitment-types")
      .then(setCommitmentTypes)
      .catch(() => {});
  }, [open]);

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

  const isDirty =
    !!description || !!commitmentTypeId || !!responsibleId || !!observations || !!selectedIprId || !!dueDate;

  const resetForm = () => {
    setCommitmentTypeId("");
    setDescription("");
    setResponsibleId("");
    setSelectedIprId("");
    setDueDate("");
    setObservations("");
    setFieldErrors({});
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const validate = () => {
    const errors: Record<string, string> = {};
    if (!commitmentTypeId) errors.commitmentTypeId = "Seleccione el tipo de compromiso.";
    if (!description.trim()) errors.description = "Ingrese una descripción.";
    if (!responsibleId) errors.responsibleId = "Seleccione un responsable.";
    if (!dueDate) errors.dueDate = "Ingrese la fecha límite.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    try {
      await api.post("/api/compromisos", {
        description,
        commitment_type_id: commitmentTypeId,
        responsible_id: responsibleId,
        due_date: dueDate,
        ipr_id: iprId || selectedIprId || null,
        observations: observations || null,
      });
      toast.success("Compromiso creado");
      resetForm();
      onClose();
      onCreated();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear compromiso");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <DrawerPanel open={open} onClose={handleClose} title="Nuevo Compromiso" wide={!iprId} isDirty={isDirty}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-sm font-medium">Tipo de compromiso *</label>
          <Select
            value={commitmentTypeId}
            onValueChange={(v) => {
              setCommitmentTypeId(v);
              setFieldErrors((p) => ({ ...p, commitmentTypeId: "" }));
            }}
          >
            <SelectTrigger aria-invalid={!!fieldErrors.commitmentTypeId || undefined}>
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
          {fieldErrors.commitmentTypeId && (
            <p className="text-xs text-red-600">{fieldErrors.commitmentTypeId}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Descripción *</label>
          <textarea
            className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={description}
            onChange={(e) => {
              setDescription(e.target.value);
              setFieldErrors((p) => ({ ...p, description: "" }));
            }}
            placeholder="Describa el compromiso..."
            aria-invalid={!!fieldErrors.description || undefined}
          />
          {fieldErrors.description && (
            <p className="text-xs text-red-600">{fieldErrors.description}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Responsable *</label>
          <ComboboxAsync
            value={responsibleId}
            onChange={(v) => {
              setResponsibleId(v);
              setFieldErrors((p) => ({ ...p, responsibleId: "" }));
            }}
            searchFn={searchUsers}
            placeholder="Buscar responsable por nombre…"
          />
          {fieldErrors.responsibleId && (
            <p className="text-xs text-red-600">{fieldErrors.responsibleId}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Fecha límite *</label>
          <DateField
            value={dueDate}
            onChange={(v) => {
              setDueDate(v);
              setFieldErrors((p) => ({ ...p, dueDate: "" }));
            }}
            aria-invalid={!!fieldErrors.dueDate || undefined}
          />
          {fieldErrors.dueDate && (
            <p className="text-xs text-red-600">{fieldErrors.dueDate}</p>
          )}
        </div>

        {!iprId && (
          <div className="space-y-1.5">
            <label className="text-sm font-medium">IPR asociada</label>
            <ComboboxAsync value={selectedIprId} onChange={setSelectedIprId} searchFn={searchIprs}
              placeholder="Buscar IPR por código o nombre..." />
          </div>
        )}

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Observaciones</label>
          <textarea
            className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={observations}
            onChange={(e) => setObservations(e.target.value)}
            placeholder="Observaciones opcionales..."
          />
        </div>

        <div className="flex gap-2 pt-2">
          <Button type="submit" disabled={submitting}>
            {submitting ? "Creando..." : "Crear Compromiso"}
          </Button>
          <Button type="button" variant="outline" onClick={handleClose}>
            Cancelar
          </Button>
        </div>
      </form>
    </DrawerPanel>
  );
}
