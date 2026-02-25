"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";

export default function NuevaReunionPage() {
  const router = useRouter();
  const { user } = useAuth();

  const [scheduledAt, setScheduledAt] = useState("");
  const [location, setLocation] = useState("");
  const [summary, setSummary] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canCreate =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);

  if (!canCreate) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">No tiene permisos para crear reuniones.</p>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scheduledAt) {
      setError("Debe indicar la fecha y hora de la reunion.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const result = await api.post<{ id: string; session_id: string }>("/api/reuniones", {
        scheduled_at: new Date(scheduledAt).toISOString(),
        location: location || null,
        summary: summary || null,
      });
      router.push(`/reuniones/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear reunion");
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
        onClick={() => router.push("/reuniones")}
      >
        <ArrowLeft className="size-4 mr-1" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nueva Reunion de Crisis</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
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
                placeholder="Sala de reuniones, oficina, etc."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Resumen / Motivo</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                placeholder="Describa brevemente el motivo de la reunion..."
              />
            </div>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear Reunion"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/reuniones")}
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
