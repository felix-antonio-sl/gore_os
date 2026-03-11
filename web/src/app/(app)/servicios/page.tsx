"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { toast } from "sonner";
import { Plus, Clock } from "lucide-react";
import { useAuth } from "@/lib/auth";
import type { DGIService } from "@/types";

const AREA_LABELS: Record<string, string> = {
  CG: "Control de Gestión",
  MP: "Mejora de Procesos",
  TD: "Transformación Digital",
  KC: "Gestión del Conocimiento",
};

const AREA_COLORS: Record<string, string> = {
  CG: "bg-blue-50 text-blue-700 border-blue-200",
  MP: "bg-green-50 text-green-700 border-green-200",
  TD: "bg-purple-50 text-purple-700 border-purple-200",
  KC: "bg-amber-50 text-amber-700 border-amber-200",
};

const AREAS = ["TODOS", "CG", "MP", "TD", "KC"];

export default function ServiciosPage() {
  const router = useRouter();
  const { user } = useAuth();
  const isJefeDGI = user?.role_code === "JEFE_DGI";

  const [services, setServices] = useState<DGIService[]>([]);
  const [loading, setLoading] = useState(true);
  const [areaFilter, setAreaFilter] = useState("TODOS");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  const [form, setForm] = useState({
    name: "",
    description: "",
    area: "CG",
    sla_days: "",
    how_to_request: "",
    deliverables: "",
  });

  const fetchServices = () => {
    setLoading(true);
    const areaParam = areaFilter !== "TODOS" ? `?area=${areaFilter}` : "";
    api
      .get<DGIService[]>(`/api/dgi/services${areaParam}`)
      .then(setServices)
      .catch(() => toast.error("Error al cargar servicios"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchServices();
  }, [areaFilter]);

  const handleCreate = async () => {
    if (!form.name.trim()) {
      toast.error("El nombre es obligatorio");
      return;
    }
    setCreating(true);
    try {
      const result = await api.post<DGIService>("/api/dgi/services", {
        name: form.name,
        description: form.description || undefined,
        area: form.area,
        sla_days: form.sla_days ? parseInt(form.sla_days) : undefined,
        how_to_request: form.how_to_request || undefined,
        deliverables: form.deliverables || undefined,
      });
      toast.success(`Servicio ${result.code} creado`);
      setDrawerOpen(false);
      setForm({ name: "", description: "", area: "CG", sla_days: "", how_to_request: "", deliverables: "" });
      fetchServices();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al crear servicio");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Catálogo de Servicios DGI"
        description="Servicios disponibles para todas las divisiones del GORE"
        actions={
          isJefeDGI ? (
            <Button size="sm" onClick={() => setDrawerOpen(true)}>
              <Plus className="size-4 mr-1" />
              Nuevo Servicio
            </Button>
          ) : undefined
        }
      />

      {/* Area filter */}
      <div className="flex gap-1 flex-wrap">
        {AREAS.map((area) => (
          <Button
            key={area}
            variant={areaFilter === area ? "default" : "outline"}
            size="sm"
            onClick={() => setAreaFilter(area)}
          >
            {area === "TODOS" ? "Todos" : AREA_LABELS[area] ?? area}
          </Button>
        ))}
      </div>

      {/* Services grid */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-44 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : services.length === 0 ? (
        <EmptyState title="Sin servicios" description="No hay servicios registrados" />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((svc) => (
            <Card
              key={svc.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push(`/servicios/${svc.id}`)}
            >
              <CardContent className="pt-5 space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className={`text-xs ${AREA_COLORS[svc.area] ?? ""}`}>
                    {AREA_LABELS[svc.area] ?? svc.area}
                  </Badge>
                  <span className="font-mono text-xs text-muted-foreground">{svc.code}</span>
                </div>
                <h3 className="font-semibold text-sm">{svc.name}</h3>
                {svc.description && (
                  <p className="text-xs text-muted-foreground line-clamp-2">{svc.description}</p>
                )}
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  {svc.sla_days && (
                    <span className="flex items-center gap-1">
                      <Clock className="size-3" />
                      SLA: {svc.sla_days}d
                    </span>
                  )}
                  <Badge variant="outline" className="text-xs">
                    {svc.status_label}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create drawer */}
      <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
        <SheetContent className="sm:max-w-lg overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Nuevo Servicio</SheetTitle>
          </SheetHeader>
          <div className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label>Nombre *</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Nombre del servicio"
              />
            </div>
            <div className="space-y-2">
              <Label>Área</Label>
              <Select value={form.area} onValueChange={(v) => setForm({ ...form, area: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="CG">Control de Gestión</SelectItem>
                  <SelectItem value="MP">Mejora de Procesos</SelectItem>
                  <SelectItem value="TD">Transformación Digital</SelectItem>
                  <SelectItem value="KC">Gestión del Conocimiento</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={2}
              />
            </div>
            <div className="space-y-2">
              <Label>SLA (días)</Label>
              <Input
                type="number"
                value={form.sla_days}
                onChange={(e) => setForm({ ...form, sla_days: e.target.value })}
                placeholder="5"
              />
            </div>
            <div className="space-y-2">
              <Label>Cómo solicitar</Label>
              <Textarea
                value={form.how_to_request}
                onChange={(e) => setForm({ ...form, how_to_request: e.target.value })}
                rows={2}
              />
            </div>
            <div className="space-y-2">
              <Label>Entregables</Label>
              <Textarea
                value={form.deliverables}
                onChange={(e) => setForm({ ...form, deliverables: e.target.value })}
                rows={2}
              />
            </div>
            <Button className="w-full" onClick={handleCreate} disabled={creating}>
              {creating ? "Creando..." : "Crear Servicio"}
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
