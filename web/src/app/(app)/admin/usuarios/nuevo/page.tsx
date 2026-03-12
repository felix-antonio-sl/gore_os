"use client";

import { useEffect, useState } from "react";
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
import { ArrowLeft } from "lucide-react";

interface CategoryOption {
  id: string;
  code: string;
  label: string;
}

interface DivisionOption {
  id: string;
  code: string;
  name: string;
}

export default function NuevoUsuarioPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const [roles, setRoles] = useState<CategoryOption[]>([]);
  const [divisions, setDivisions] = useState<DivisionOption[]>([]);

  const [names, setNames] = useState("");
  const [paternalSurname, setPaternalSurname] = useState("");
  const [maternalSurname, setMaternalSurname] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [roleId, setRoleId] = useState("");
  const [divisionId, setDivisionId] = useState("");
  const [rut, setRut] = useState("");
  const [phone, setPhone] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<CategoryOption[]>("/api/catalogs/categories/system_role").then(setRoles).catch(() => {});
    api.get<DivisionOption[]>("/api/catalogs/divisions").then(setDivisions).catch(() => {});
  }, []);

  const canCreate = user && user.role_code === "ADMIN_SISTEMA";

  if (!canCreate) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">No tiene permisos para crear usuarios.</p>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!names || !paternalSurname || !email || !password || !roleId) {
      setError("Nombres, apellido paterno, email, contraseña y rol son requeridos.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await api.post("/api/admin/usuarios", {
        names,
        paternal_surname: paternalSurname,
        maternal_surname: maternalSurname || null,
        email,
        password,
        system_role_id: roleId,
        division_id: divisionId || null,
        rut: rut || null,
        phone: phone || null,
      });
      router.push("/admin/usuarios");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear usuario");
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
        onClick={() => router.push("/admin/usuarios")}
      >
        <ArrowLeft className="size-4 mr-1" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Nuevo Usuario</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Nombres *</label>
              <Input
                value={names}
                onChange={(e) => setNames(e.target.value)}
                placeholder="Nombres del usuario"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Apellido paterno *</label>
              <Input
                value={paternalSurname}
                onChange={(e) => setPaternalSurname(e.target.value)}
                placeholder="Apellido paterno"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Apellido materno</label>
              <Input
                value={maternalSurname}
                onChange={(e) => setMaternalSurname(e.target.value)}
                placeholder="Apellido materno (opcional)"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Email *</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="email@goreos.cl"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Contraseña *</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Contraseña"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Rol *</label>
              <Select value={roleId} onValueChange={setRoleId}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione rol" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((r) => (
                    <SelectItem key={r.id} value={r.id}>
                      {r.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">División</label>
              <Select value={divisionId} onValueChange={setDivisionId}>
                <SelectTrigger>
                  <SelectValue placeholder="Sin división (opcional)" />
                </SelectTrigger>
                <SelectContent>
                  {divisions.map((d) => (
                    <SelectItem key={d.id} value={d.id}>
                      {d.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">RUT</label>
              <Input
                value={rut}
                onChange={(e) => setRut(e.target.value)}
                placeholder="12.345.678-9 (opcional)"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Teléfono</label>
              <Input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+56 9 1234 5678 (opcional)"
              />
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Creando..." : "Crear Usuario"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/admin/usuarios")}
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
