"use client";

import { ReactNode } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/empty-state";
import { AlertTriangle, RotateCw } from "lucide-react";

interface Column {
  key: string;
  label: string;
  className?: string;
  render?: (value: unknown, row: unknown) => ReactNode;
}

interface DataTableProps {
  columns: Column[];
  data: unknown[];
  page: number;
  totalPages: number;
  total: number;
  onPageChange: (page: number) => void;
  onRowClick?: (row: unknown) => void;
  isLoading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  /** When set (and not loading), render a load-error state distinct from "empty". */
  error?: string | null;
  /** Retry handler — shows a "Reintentar" button in the error state. */
  onRetry?: () => void;
  /** True when filters/search are active — switches the empty copy + offers "Limpiar filtros". */
  hasActiveFilters?: boolean;
  /** Clears filters from the empty state (shown only when hasActiveFilters). */
  onClearFilters?: () => void;
}

export function DataTable({
  columns,
  data,
  page,
  totalPages,
  total,
  onPageChange,
  onRowClick,
  isLoading = false,
  emptyTitle,
  emptyDescription,
  error,
  onRetry,
  hasActiveFilters = false,
  onClearFilters,
}: DataTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-2" aria-busy="true">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-10 rounded bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  const pageSize = data.length;
  const startItem = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, total);

  const renderEmptyOrError = () => {
    if (error) {
      return (
        <EmptyState
          icon={<AlertTriangle className="size-10 stroke-1 text-amber-500" />}
          title="No se pudieron cargar los datos"
          description={error || "Revisa tu conexión y reintenta."}
          action={
            onRetry ? (
              <Button variant="outline" size="sm" onClick={onRetry}>
                <RotateCw className="size-4 mr-1.5" />
                Reintentar
              </Button>
            ) : undefined
          }
        />
      );
    }
    if (hasActiveFilters) {
      return (
        <EmptyState
          title="Sin coincidencias"
          description="Ningún registro coincide con los filtros aplicados."
          action={
            onClearFilters ? (
              <Button variant="outline" size="sm" onClick={onClearFilters}>
                Limpiar filtros
              </Button>
            ) : undefined
          }
        />
      );
    }
    return (
      <EmptyState
        title={emptyTitle ?? "Aún no hay registros"}
        description={emptyDescription ?? "Cuando se creen, aparecerán aquí."}
      />
    );
  };

  return (
    <div className="space-y-2 animate-in fade-in duration-200">
      <div className="rounded-md border">
        <Table aria-label="Tabla de datos">
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={col.key} className={col.className}>{col.label}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="py-12">
                  {renderEmptyOrError()}
                </TableCell>
              </TableRow>
            ) : (
              data.map((row, rowIndex) => (
                <TableRow
                  key={rowIndex}
                  className={cn(onRowClick && "cursor-pointer")}
                  onClick={() => onRowClick && onRowClick(row)}
                  {...(onRowClick ? {
                    tabIndex: 0,
                    onKeyDown: (e: React.KeyboardEvent) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onRowClick(row); } },
                  } : {})}
                >
                  {columns.map((col) => (
                    <TableCell key={col.key} className={col.className}>
                      {col.render
                        ? col.render((row as Record<string, unknown>)[col.key], row)
                        : String((row as Record<string, unknown>)[col.key] ?? "")}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      {/* Hide pager in error/empty states to avoid a "Página 1 de 1" under an error. */}
      {!error && data.length > 0 && (
        <div className="flex items-center justify-between px-1 text-sm text-muted-foreground" aria-live="polite">
          <span>
            Mostrando {startItem === 0 ? 0 : startItem}–{endItem} de {total}
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
              aria-label="Página anterior"
            >
              &lt;
            </Button>
            <span>
              Página {page} de {Math.max(totalPages, 1)}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
              aria-label="Página siguiente"
            >
              &gt;
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
