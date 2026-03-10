"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { FilterBar } from "@/components/filter-bar";
import { DrawerPanel } from "@/components/drawer-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Plus, KeyRound } from "lucide-react";
import { formatDate } from "@/lib/format";
import { PageHeader } from "@/components/page-header";
import type { PaginatedResponse, CategoryRef } from "@/types";

interface UserListItem {
  id: string;
  email: string;
  names: string;
  paternal_surname: string;
  maternal_surname: string | null;
  role_code: string;
  role_label: string;
  division_name: string | null;
  is_active: boolean;
  created_at: string;
}

interface UserDetail extends UserListItem {
  division_id: string | null;
  system_role_id: string;
  phone: string | null;
  rut: string | null;
}

interface DivisionOption {
  id: string;
  code: string;
  name: string;
}

const ROLE_OPTIONS = [
  { value: "ADMIN_SISTEMA", label: "Admin Sistema" },
  { value: "ADMIN_REGIONAL", label: "Admin Regional" },
  { value: "JEFE_DIVISION", label: "Jefe Division" },
  { value: "ENCARGADO", label: "Encargado" },
  { value: "JEFE_DGI", label: "Jefe DGI" },
  { value: "ESP_CONTROL_GESTION", label: "Esp. Control Gestion" },
  { value: "ESP_PROCESOS", label: "Esp. Procesos" },
  { value: "ESP_TD", label: "Esp. Transformacion Digital" },
];

const ACTIVE_OPTIONS = [
  { value: "true", label: "Activo" },
  { value: "false", label: "Inactivo" },
];

export default function UsuariosPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user: currentUser } = useAuth();

  const [data, setData] = useState<PaginatedResponse<UserListItem> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<UserDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Edit mode state
  const [editing, setEditing] = useState(false);
  const [editNames, setEditNames] = useState("");
  const [editPaternal, setEditPaternal] = useState("");
  const [editMaternal, setEditMaternal] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editRoleId, setEditRoleId] = useState("");
  const [editDivisionId, setEditDivisionId] = useState("");
  const [editPhone, setEditPhone] = useState("");
  const [editSaving, setEditSaving] = useState(false);
  const [editErrors, setEditErrors] = useState<Record<string, string>>({});

  // Reset password state
  const [showResetPw, setShowResetPw] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const [resetMsg, setResetMsg] = useState<string | null>(null);

  // Catalogs for edit form
  const [roles, setRoles] = useState<CategoryRef[]>([]);
  const [divisions, setDivisions] = useState<DivisionOption[]>([]);

  const page = Number(searchParams.get("page") ?? "1");
  const search = searchParams.get("search") ?? "";
  const role_code = searchParams.get("role_code") ?? "";
  const is_active = searchParams.get("is_active") ?? "";

  const filterValues: Record<string, string> = { role_code, is_active };

  useEffect(() => {
    api.get<CategoryRef[]>("/api/catalogs/categories/system_role").then(setRoles).catch(() => {});
    api.get<DivisionOption[]>("/api/catalogs/divisions").then(setDivisions).catch(() => {});
  }, []);

  const buildUrl = useCallback(
    (overrides: Record<string, string | number>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(overrides).forEach(([k, v]) => {
        if (v === "" || v === undefined) params.delete(k);
        else params.set(k, String(v));
      });
      return `${pathname}?${params.toString()}`;
    },
    [pathname, searchParams]
  );

  const handleFilterChange = (key: string, value: string) => {
    router.push(buildUrl({ [key]: value, page: 1 }));
  };

  const handleClear = () => router.push(pathname);
  const handlePageChange = (newPage: number) => router.push(buildUrl({ page: newPage }));

  const [searchInput, setSearchInput] = useState(search);

  useEffect(() => {
    setSearchInput(search);
  }, [search]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (searchInput !== search) {
        router.push(buildUrl({ search: searchInput, page: 1 }));
      }
    }, 400);
    return () => clearTimeout(timeout);
  }, [searchInput, search, router, buildUrl]);

  // Fetch list
  useEffect(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (search) params.set("search", search);
    if (role_code) params.set("role_code", role_code);
    if (is_active) params.set("is_active", is_active);

    setIsLoading(true);
    api
      .get<PaginatedResponse<UserListItem>>(`/api/admin/usuarios?${params.toString()}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [page, search, role_code, is_active]);

  const loadDetail = (userId: string) => {
    setSelectedId(userId);
    setDetail(null);
    setDetailLoading(true);
    setEditing(false);
    setShowResetPw(false);
    setResetMsg(null);
    api
      .get<UserDetail>(`/api/admin/usuarios/${userId}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false));
  };

  const openDetail = (row: unknown) => {
    const item = row as UserListItem;
    loadDetail(item.id);
  };

  const startEdit = () => {
    if (!detail) return;
    setEditNames(detail.names);
    setEditPaternal(detail.paternal_surname);
    setEditMaternal(detail.maternal_surname ?? "");
    setEditEmail(detail.email);
    setEditRoleId(detail.system_role_id);
    setEditDivisionId(detail.division_id ?? "");
    setEditPhone(detail.phone ?? "");
    setEditing(true);
    setEditErrors({});
  };

  const validateEditForm = (): Record<string, string> => {
    const errors: Record<string, string> = {};
    if (!editNames.trim()) errors.names = "Nombres es requerido";
    if (!editPaternal.trim()) errors.paternal = "Apellido paterno es requerido";
    if (!editEmail.trim()) {
      errors.email = "Email es requerido";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editEmail)) {
      errors.email = "Formato de email inválido";
    }
    return errors;
  };

  const handleSaveEdit = async () => {
    if (!detail) return;
    const errors = validateEditForm();
    if (Object.keys(errors).length > 0) {
      setEditErrors(errors);
      return;
    }
    setEditErrors({});
    setEditSaving(true);
    try {
      const body: Record<string, string | null> = {};
      if (editNames !== detail.names) body.names = editNames;
      if (editPaternal !== detail.paternal_surname) body.paternal_surname = editPaternal;
      if (editMaternal !== (detail.maternal_surname ?? "")) body.maternal_surname = editMaternal || null;
      if (editEmail !== detail.email) body.email = editEmail;
      if (editRoleId !== detail.system_role_id) body.system_role_id = editRoleId;
      if (editDivisionId !== (detail.division_id ?? "")) body.division_id = editDivisionId || null;
      if (editPhone !== (detail.phone ?? "")) body.phone = editPhone || null;

      if (Object.keys(body).length > 0) {
        await api.patch(`/api/admin/usuarios/${detail.id}`, body);
      }
      setEditing(false);
      loadDetail(detail.id);
      // Refresh list
      refreshList();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEditSaving(false);
    }
  };

  const handleToggle = async () => {
    if (!detail) return;
    try {
      await api.post(`/api/admin/usuarios/${detail.id}/toggle-activo`);
      loadDetail(detail.id);
      refreshList();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error");
    }
  };

  const handleResetPassword = async () => {
    if (!detail || !newPassword) return;
    try {
      const res = await api.post<{ message: string }>(`/api/admin/usuarios/${detail.id}/reset-password`, {
        new_password: newPassword,
      });
      setResetMsg(res.message);
      setNewPassword("");
    } catch (err) {
      setResetMsg(err instanceof Error ? err.message : "Error");
    }
  };

  const refreshList = () => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "20");
    if (search) params.set("search", search);
    if (role_code) params.set("role_code", role_code);
    if (is_active) params.set("is_active", is_active);

    api
      .get<PaginatedResponse<UserListItem>>(`/api/admin/usuarios?${params.toString()}`)
      .then(setData)
      .catch(() => {});
  };

  if (currentUser?.role_code !== "ADMIN_SISTEMA") {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">No tiene permisos para acceder a esta sección.</p>
      </div>
    );
  }

  const columns = [
    {
      key: "names",
      label: "Nombre",
      render: (_v: unknown, row: unknown) => {
        const u = row as UserListItem;
        return (
          <span className="font-medium">
            {u.names} {u.paternal_surname}
          </span>
        );
      },
    },
    { key: "email", label: "Email" },
    {
      key: "role_label",
      label: "Rol",
      render: (v: unknown) => (
        <Badge variant="outline" className="text-xs">
          {String(v ?? "")}
        </Badge>
      ),
    },
    {
      key: "division_name",
      label: "División",
      render: (v: unknown) => <span className="text-sm">{String(v ?? "-")}</span>,
    },
    {
      key: "is_active",
      label: "Estado",
      render: (v: unknown) =>
        v ? (
          <Badge variant="default" className="bg-green-600 text-xs">
            Activo
          </Badge>
        ) : (
          <Badge variant="secondary" className="text-xs">
            Inactivo
          </Badge>
        ),
    },
    {
      key: "created_at",
      label: "Creado",
      render: (v: unknown) => (
        <span className="text-xs text-muted-foreground">{formatDate(String(v ?? ""))}</span>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <PageHeader
        title="Usuarios"
        description="Administración de usuarios del sistema"
        actions={
          <Button onClick={() => router.push("/admin/usuarios/nuevo")}>
            <Plus className="size-4 mr-1" />
            Nuevo Usuario
          </Button>
        }
      />

      <FilterBar
        filters={[
          { key: "role_code", label: "Rol", options: ROLE_OPTIONS },
          { key: "is_active", label: "Estado", options: ACTIVE_OPTIONS },
        ]}
        values={filterValues}
        onChange={handleFilterChange}
        onClear={handleClear}
        searchPlaceholder="Buscar por nombre o email..."
        searchValue={searchInput}
        onSearchChange={setSearchInput}
      />

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        page={page}
        totalPages={data?.total_pages ?? 1}
        total={data?.total ?? 0}
        onPageChange={handlePageChange}
        onRowClick={openDetail}
        isLoading={isLoading}
      />

      <DrawerPanel
        open={!!selectedId}
        onClose={() => {
          setSelectedId(null);
          setEditing(false);
          setShowResetPw(false);
        }}
        title="Detalle de Usuario"
      >
        {detailLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-8 rounded bg-muted animate-pulse" />
            ))}
          </div>
        ) : detail ? (
          <div className="space-y-5">
            {!editing ? (
              <>
                {/* View mode */}
                <div>
                  <p className="font-semibold text-base">
                    {detail.names} {detail.paternal_surname}
                    {detail.maternal_surname ? ` ${detail.maternal_surname}` : ""}
                  </p>
                  <p className="text-sm text-muted-foreground mt-0.5">{detail.email}</p>
                </div>

                <div className="rounded-lg border divide-y text-sm">
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Rol</span>
                    <Badge variant="outline">{detail.role_label}</Badge>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">División</span>
                    <span>{detail.division_name ?? "-"}</span>
                  </div>
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Estado</span>
                    {detail.is_active ? (
                      <Badge variant="default" className="bg-green-600 text-xs">
                        Activo
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="text-xs">
                        Inactivo
                      </Badge>
                    )}
                  </div>
                  {detail.rut && (
                    <div className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">RUT</span>
                      <span>{detail.rut}</span>
                    </div>
                  )}
                  {detail.phone && (
                    <div className="flex justify-between px-3 py-2">
                      <span className="text-muted-foreground">Teléfono</span>
                      <span>{detail.phone}</span>
                    </div>
                  )}
                  <div className="flex justify-between px-3 py-2">
                    <span className="text-muted-foreground">Creado</span>
                    <span className="text-xs">{formatDate(detail.created_at)}</span>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <Button size="sm" onClick={startEdit}>
                    Editar
                  </Button>
                  <Button
                    size="sm"
                    variant={detail.is_active ? "destructive" : "default"}
                    onClick={handleToggle}
                  >
                    {detail.is_active ? "Desactivar" : "Activar"}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setShowResetPw(!showResetPw);
                      setResetMsg(null);
                      setNewPassword("");
                    }}
                  >
                    <KeyRound className="size-4 mr-1" />
                    Reset Contraseña
                  </Button>
                </div>

                {showResetPw && (
                  <div className="space-y-2 rounded-lg border p-3">
                    <label className="text-sm font-medium">Nueva contraseña</label>
                    <Input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Nueva contraseña"
                    />
                    <p className="text-xs text-muted-foreground">Mínimo 8 caracteres</p>
                    <Button size="sm" onClick={handleResetPassword} disabled={!newPassword || newPassword.length < 8}>
                      Cambiar
                    </Button>
                    {resetMsg && (
                      <p className="text-sm text-green-600">{resetMsg}</p>
                    )}
                  </div>
                )}
              </>
            ) : (
              <>
                {/* Edit mode */}
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Nombres</label>
                    <Input value={editNames} onChange={(e) => setEditNames(e.target.value)} className={editErrors.names ? "border-red-400" : ""} />
                    {editErrors.names && <p className="text-xs text-red-600">{editErrors.names}</p>}
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Apellido paterno</label>
                    <Input value={editPaternal} onChange={(e) => setEditPaternal(e.target.value)} className={editErrors.paternal ? "border-red-400" : ""} />
                    {editErrors.paternal && <p className="text-xs text-red-600">{editErrors.paternal}</p>}
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Apellido materno</label>
                    <Input value={editMaternal} onChange={(e) => setEditMaternal(e.target.value)} />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Email</label>
                    <Input value={editEmail} onChange={(e) => setEditEmail(e.target.value)} className={editErrors.email ? "border-red-400" : ""} />
                    {editErrors.email && <p className="text-xs text-red-600">{editErrors.email}</p>}
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Rol</label>
                    <Select value={editRoleId} onValueChange={setEditRoleId}>
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
                    <Select
                      value={editDivisionId || "__none__"}
                      onValueChange={(v) => setEditDivisionId(v === "__none__" ? "" : v)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sin división" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__none__">Sin división</SelectItem>
                        {divisions.map((d) => (
                          <SelectItem key={d.id} value={d.id}>
                            {d.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Teléfono</label>
                    <Input value={editPhone} onChange={(e) => setEditPhone(e.target.value)} />
                  </div>
                  <div className="flex gap-2 pt-2">
                    <Button size="sm" onClick={handleSaveEdit} disabled={editSaving}>
                      {editSaving ? "Guardando..." : "Guardar"}
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setEditing(false)}>
                      Cancelar
                    </Button>
                  </div>
                </div>
              </>
            )}
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">No se pudo cargar el detalle.</p>
        )}
      </DrawerPanel>
    </div>
  );
}
