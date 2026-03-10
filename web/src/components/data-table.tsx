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

interface Column {
  key: string;
  label: string;
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

  return (
    <div className="space-y-2">
      <div className="rounded-md border">
        <Table aria-label="Tabla de datos">
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={col.key}>{col.label}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="py-12"
                >
                  <EmptyState title="Sin resultados" description="Intente ajustar los filtros" />
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
                    <TableCell key={col.key}>
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
    </div>
  );
}
