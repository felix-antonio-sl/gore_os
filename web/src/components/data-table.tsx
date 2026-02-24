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
      <div className="space-y-2">
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
        <Table>
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
                  className="text-center text-muted-foreground py-8"
                >
                  Sin resultados
                </TableCell>
              </TableRow>
            ) : (
              data.map((row, rowIndex) => (
                <TableRow
                  key={rowIndex}
                  className={cn(onRowClick && "cursor-pointer")}
                  onClick={() => onRowClick && onRowClick(row)}
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
      <div className="flex items-center justify-between px-1 text-sm text-muted-foreground">
        <span>
          Mostrando {startItem === 0 ? 0 : startItem}–{endItem} de {total}
        </span>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
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
          >
            &gt;
          </Button>
        </div>
      </div>
    </div>
  );
}
