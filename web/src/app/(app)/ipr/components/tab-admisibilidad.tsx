"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Circle, Shield } from "lucide-react";
import { formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";

interface ChecklistItem {
  item_id: string;
  code: string;
  label: string;
  description: string | null;
  responsible_role: string;
  is_required: boolean;
  verified: boolean;
  verified_by: string | null;
  verified_at: string | null;
  notes: string | null;
}

interface ChecklistResponse {
  track_code: string | null;
  total_items: number;
  verified_count: number;
  pending_count: number;
  items: ChecklistItem[];
}

interface Props {
  iprId: string;
  canManage: boolean;
}

export function TabAdmisibilidad({ iprId, canManage }: Props) {
  const { user } = useAuth();
  const [data, setData] = useState<ChecklistResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const res = await api.get<ChecklistResponse>(`/api/ipr/${iprId}/admisibilidad`);
      setData(res);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [iprId]);

  const handleVerify = async (itemId: string) => {
    try {
      await api.post(`/api/ipr/${iprId}/admisibilidad/${itemId}/verificar`, {});
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al verificar");
    }
  };

  const handleUnverify = async (itemId: string) => {
    try {
      await api.delete(`/api/ipr/${iprId}/admisibilidad/${itemId}/verificar`);
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al desmarcar");
    }
  };

  if (loading) return <div className="text-sm text-muted-foreground">Cargando checklist...</div>;
  if (!data || data.total_items === 0) {
    return <div className="text-sm text-muted-foreground">No hay items de admisibilidad configurados para este track.</div>;
  }

  const pct = data.total_items > 0 ? Math.round((data.verified_count / data.total_items) * 100) : 0;
  const userRole = user?.role_code || "";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Checklist de Admisibilidad
          </CardTitle>
          <Badge variant="outline">{data.track_code}</Badge>
        </div>
        <div className="space-y-2 pt-2">
          <div className="flex justify-between text-sm">
            <span>{data.verified_count}/{data.total_items} verificados</span>
            <span>{pct}%</span>
          </div>
          <Progress value={pct} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.items.map((item) => {
            const canVerify = canManage && (userRole === "ADMIN_SISTEMA" || userRole === item.responsible_role);
            return (
              <div key={item.item_id} className="flex items-start gap-3 rounded-lg border p-3">
                {item.verified ? (
                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-green-600 shrink-0" />
                ) : (
                  <Circle className="mt-0.5 h-5 w-5 text-muted-foreground shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{item.label}</span>
                    {item.is_required && <Badge variant="destructive" className="text-[10px]">Requerido</Badge>}
                  </div>
                  {item.description && (
                    <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
                  )}
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="secondary" className="text-[10px]">{item.responsible_role}</Badge>
                    {item.verified && item.verified_by && (
                      <span className="text-xs text-muted-foreground">
                        {item.verified_by} — {formatDateTime(item.verified_at!)}
                      </span>
                    )}
                  </div>
                </div>
                {canVerify && !item.verified && (
                  <Button size="sm" variant="outline" onClick={() => handleVerify(item.item_id)}>
                    Verificar
                  </Button>
                )}
                {canVerify && item.verified && (
                  <Button size="sm" variant="ghost" className="text-muted-foreground" onClick={() => handleUnverify(item.item_id)}>
                    Desmarcar
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
