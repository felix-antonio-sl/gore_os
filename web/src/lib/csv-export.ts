import type { Column } from "@/app/(app)/datos/domains/types";

/**
 * Escapa un valor de celda para CSV:
 * - Convierte null/undefined en string vacío
 * - Envuelve en comillas si contiene coma, comilla o salto de línea
 * - Duplica comillas internas
 */
function escapeCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  const str = String(value);
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

/**
 * Genera y descarga un archivo CSV desde un array de datos.
 * Incluye BOM UTF-8 para compatibilidad con Excel en Windows.
 *
 * @param columns  Columnas del dominio (Column[]) — usa key/label
 * @param data     Filas de datos (unknown[])
 * @param filename Nombre del archivo sin extensión
 */
export function exportCSV(
  columns: Column[],
  data: unknown[],
  filename: string
): void {
  const headers = columns.map((c) => escapeCell(c.label)).join(",");

  const rows = data.map((row) => {
    const record = row as Record<string, unknown>;
    return columns.map((c) => escapeCell(record[c.key])).join(",");
  });

  const csvContent = [headers, ...rows].join("\n");

  // BOM UTF-8 para Excel en Windows
  const bom = "\uFEFF";
  const blob = new Blob([bom + csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${filename}.csv`;
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}
