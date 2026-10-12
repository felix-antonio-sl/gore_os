import { api } from "./api";
import type { ComboboxOption } from "@/components/combobox-async";

export async function searchUsers(query: string): Promise<ComboboxOption[]> {
  const users = await api.get<{
    id: string;
    nombre: string;
    apellido_paterno: string;
    division_name: string | null;
  }[]>(`/api/catalogs/users?search=${encodeURIComponent(query)}`);
  return users.map((user) => ({
    value: user.id,
    label: `${user.nombre} ${user.apellido_paterno}${user.division_name ? ` (${user.division_name})` : ""}`,
  }));
}

export async function searchIprs(query: string): Promise<ComboboxOption[]> {
  const iprs = await api.get<{ id: string; codigo_bip: string; name: string }[]>(
    `/api/catalogs/iprs?search=${encodeURIComponent(query)}`,
  );
  return iprs.map((ipr) => ({ value: ipr.id, label: `${ipr.codigo_bip} — ${ipr.name}` }));
}
