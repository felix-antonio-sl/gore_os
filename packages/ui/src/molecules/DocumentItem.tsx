import * as React from "react";
import { cn } from "../lib/utils";
import { Icons, GoreIcon } from "../atoms/GoreIcon";
import { GoreBadge } from "../atoms/GoreBadge";

export interface DocumentItemProps {
  className?: string;
  tipo: string;
  numero: string;
  fecha: string;
  materia?: string;
  estado?: string;
  isPdf?: boolean;
}

export function DocumentItem({
  className,
  tipo,
  numero,
  fecha,
  materia,
  estado,
  isPdf = true,
}: DocumentItemProps) {
  return (
    <div
      className={cn(
        "flex items-start gap-4 rounded-md border p-3 transition-colors hover:bg-gray-50",
        className
      )}
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded bg-red-50 text-red-600">
        <Icons.FileText size={20} />
      </div>
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-gore-text">
            {tipo} N° {numero}
          </p>
          {estado && <GoreBadge variant="outline" className="text-[10px] h-5">{estado}</GoreBadge>}
        </div>
        <div className="flex items-center text-xs text-muted-foreground">
            <span>{fecha}</span>
        </div>
        {materia && (
            <p className="text-xs text-gray-500 line-clamp-2 mt-1">
                {materia}
            </p>
        )}
      </div>
    </div>
  );
}
