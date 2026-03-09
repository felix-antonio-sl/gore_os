"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { toast } from "sonner";

interface CertificationStatus {
  categoria_c33: string | null;
  certifier_org: string | null;
  requested: boolean;
  requested_at: string | null;
  requested_by: string | null;
  resolved: boolean;
  informe_tecnico_favorable: boolean | null;
  resolved_at: string | null;
  resolved_by: string | null;
  document_reference: string | null;
  notes: string | null;
}

const REQUEST_ROLES = ["JEFE_DIVISION", "ADMIN_REGIONAL", "ADMIN_SISTEMA", "JEFE_DGI", "GOBERNADOR"];
const RESOLVE_ROLES = ["ADMIN_REGIONAL", "ADMIN_SISTEMA"];

export function C33CertificationSection({ iprId }: { iprId: string }) {
  const { user } = useAuth();
  const [status, setStatus] = useState<CertificationStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [showResolveForm, setShowResolveForm] = useState(false);
  const [docRef, setDocRef] = useState("");
  const [notes, setNotes] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await api.get<CertificationStatus>(`/api/ipr/${iprId}/certificacion-tecnica`);
      setStatus(data);
    } catch {
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }, [iprId]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <div className="text-sm text-muted-foreground">Cargando certificacion...</div>;
  if (!status) return null;

  const canRequest = user && REQUEST_ROLES.includes(user.role_code);
  const canResolve = user && RESOLVE_ROLES.includes(user.role_code);

  const handleSolicitar = async () => {
    try {
      await api.post(`/api/ipr/${iprId}/certificacion-tecnica/solicitar`, {});
      toast.success("Certificacion solicitada");
      load();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Error al solicitar");
    }
  };

  const handleResolver = async (favorable: boolean) => {
    try {
      await api.patch(`/api/ipr/${iprId}/certificacion-tecnica`, {
        favorable,
        document_reference: docRef,
        notes,
      });
      toast.success(favorable ? "Certificacion favorable registrada" : "Certificacion desfavorable registrada");
      setShowResolveForm(false);
      load();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Error al registrar resultado");
    }
  };

  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="font-medium">Certificacion Tecnica C33</h4>
        {status.resolved ? (
          status.informe_tecnico_favorable ? (
            <Badge variant="default" className="bg-green-600">Favorable</Badge>
          ) : (
            <Badge variant="destructive">Desfavorable</Badge>
          )
        ) : status.requested ? (
          <Badge variant="secondary">Solicitada a {status.certifier_org}</Badge>
        ) : (
          <Badge variant="outline">Sin solicitar</Badge>
        )}
      </div>

      {status.categoria_c33 && (
        <div className="text-sm text-muted-foreground">
          Categoria: <span className="font-medium">{status.categoria_c33}</span>
          {status.certifier_org && <> — Certificador: <span className="font-medium">{status.certifier_org}</span></>}
        </div>
      )}

      {status.requested && (
        <div className="text-sm">
          Solicitada por {status.requested_by} el {status.requested_at ? formatDateTime(status.requested_at) : "—"}
        </div>
      )}

      {status.resolved && (
        <div className="text-sm space-y-1">
          <div>Resuelta por {status.resolved_by} el {status.resolved_at ? formatDateTime(status.resolved_at) : "—"}</div>
          {status.document_reference && <div>Referencia: {status.document_reference}</div>}
          {status.notes && <div>Notas: {status.notes}</div>}
        </div>
      )}

      {!status.requested && !status.resolved && canRequest && status.categoria_c33 && (
        <Button size="sm" onClick={handleSolicitar}>
          Solicitar Certificacion a {status.certifier_org}
        </Button>
      )}

      {status.requested && !status.resolved && canResolve && (
        <>
          {!showResolveForm ? (
            <Button size="sm" variant="outline" onClick={() => setShowResolveForm(true)}>
              Registrar Resultado
            </Button>
          ) : (
            <div className="space-y-2 border-t pt-2">
              <Input
                placeholder="Referencia documento (ej: ORD. N° 123/2026)"
                value={docRef}
                onChange={(e) => setDocRef(e.target.value)}
              />
              <textarea
                className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Notas (opcional)"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
              />
              <div className="flex gap-2">
                <Button size="sm" onClick={() => handleResolver(true)}>Favorable</Button>
                <Button size="sm" variant="destructive" onClick={() => handleResolver(false)}>Desfavorable</Button>
                <Button size="sm" variant="ghost" onClick={() => setShowResolveForm(false)}>Cancelar</Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
