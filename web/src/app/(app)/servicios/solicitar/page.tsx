"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import type { DGIService } from "@/types";

export default function SolicitarServicioPage() {
  const router = useRouter();

  const [services, setServices] = useState<DGIService[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [resultCode, setResultCode] = useState("");

  const [form, setForm] = useState({
    service_id: "",
    description: "",
    urgency: "NORMAL",
  });

  useEffect(() => {
    api
      .get<DGIService[]>("/api/dgi/services?status=ACTIVO")
      .then(setServices)
      .catch(() => toast.error("Error al cargar servicios"))
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async () => {
    if (!form.service_id) {
      toast.error("Seleccione un servicio");
      return;
    }
    if (!form.description.trim()) {
      toast.error("La descripción es obligatoria");
      return;
    }
    setSubmitting(true);
    try {
      const result = await api.post<{ id: string; code: string }>("/api/dgi/services/requests", {
        service_id: form.service_id,
        description: form.description,
        urgency: form.urgency,
      });
      setResultCode(result.code);
      setSubmitted(true);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al enviar solicitud");
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[50vh]">
        <Card className="max-w-md w-full">
          <CardContent className="pt-8 pb-8 text-center space-y-4">
            <CheckCircle2 className="size-12 text-green-500 mx-auto" />
            <h2 className="text-xl font-bold">Solicitud Enviada</h2>
            <p className="text-muted-foreground">
              Su solicitud <span className="font-mono font-semibold">{resultCode}</span> ha sido
              registrada. El equipo DGI la evaluará a la brevedad.
            </p>
            <div className="flex gap-2 justify-center">
              <Button variant="outline" onClick={() => router.push("/servicios")}>
                Ver Servicios
              </Button>
              <Button onClick={() => router.push("/dashboard")}>
                Ir al Inicio
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <Button variant="ghost" size="sm" onClick={() => router.push("/servicios")}>
        <ArrowLeft className="size-4 mr-1" /> Volver
      </Button>

      <PageHeader
        title="Solicitar Servicio DGI"
        description="Complete el formulario para solicitar un servicio del equipo DGI"
      />

      <Card className="max-w-lg">
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-2">
            <Label>Servicio *</Label>
            <Select
              value={form.service_id}
              onValueChange={(v) => setForm({ ...form, service_id: v })}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar servicio" />
              </SelectTrigger>
              <SelectContent>
                {services.map((svc) => (
                  <SelectItem key={svc.id} value={svc.id}>
                    {svc.name} ({svc.area})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Descripción *</Label>
            <Textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Describa lo que necesita"
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label>Urgencia</Label>
            <Select value={form.urgency} onValueChange={(v) => setForm({ ...form, urgency: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="BAJA">Baja</SelectItem>
                <SelectItem value="NORMAL">Normal</SelectItem>
                <SelectItem value="ALTA">Alta</SelectItem>
                <SelectItem value="CRITICA">Crítica</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button className="w-full" onClick={handleSubmit} disabled={submitting}>
            {submitting ? "Enviando..." : "Enviar Solicitud"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
