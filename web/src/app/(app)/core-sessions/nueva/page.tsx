"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
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

const MANAGER_ROLES = ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "SECRETARIO_EJECUTIVO"];

export default function NuevaSesionCorePage() {
  const router = useRouter();
  const { user } = useAuth();

  const [scheduledAt, setScheduledAt] = useState("");
  const [sessionType, setSessionType] = useState("ORDINARIA");
  const [location, setLocation] = useState("");
  const [summary, setSummary] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canCreate = user && MANAGER_ROLES.includes(user.role_code);

  if (!canCreate) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">No tiene permisos para crear sesiones CORE.</p>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scheduledAt) {
      setError("Debe indicar la fecha y hora de la sesion.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const result = await api.post<{ id: string; session_number: number }>("/api/core-sessions", {
        scheduled_at: new Date(scheduledAt).toISOString(),
        session_type: sessionType,
        location: location || null,
        summary: summary || null,
      });
      router.push(`/core-sessions/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear sesion");
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
        onClick={() => router.push("/core-sessions")}
      >
        <ArrowLeft className="size-4 mr-1" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nueva Sesion del Consejo Regional</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Tipo de Sesion *</label>
              <Select value={sessionType} onValueChange={setSessionType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ORDINARIA">Sesion Ordinaria</SelectItem>
                  <SelectItem value="EXTRAORDINARIA">Sesion Extraordinaria</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Fecha y hora *</label>
              <Input
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Ubicacion</label>
              <Input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Sala del Consejo, oficina, etc."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Resumen / Tabla</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                placeholder="Describa brevemente los temas principales de la sesion..."
              />
            </div>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear Sesion"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/core-sessions")}
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
