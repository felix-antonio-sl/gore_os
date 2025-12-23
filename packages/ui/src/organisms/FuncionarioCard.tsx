import * as React from "react";
import { cn } from "../lib/utils";
import { GoreBadge } from "../atoms/GoreBadge";
import { Icons } from "../atoms/GoreIcon";

export interface FuncionarioCardProps {
  className?: string;
  nombres: string;
  apellidos: string;
  email: string;
  cargo: string;
  division: string;
  estamento?: string;
  estado: string;
}

export function FuncionarioCard({
  className,
  nombres,
  apellidos,
  email,
  cargo,
  division,
  estamento,
  estado,
}: FuncionarioCardProps) {
  return (
    <div
      className={cn(
        "flex items-center space-x-4 rounded-lg border bg-card p-4 text-card-foreground shadow-sm",
        className
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gore-brand/10">
        <span className="text-lg font-semibold text-gore-brand">
          {nombres.charAt(0)}
          {apellidos.charAt(0)}
        </span>
      </div>
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-gore-text">
            {nombres} {apellidos}
          </h4>
          <GoreBadge variant={estado === "Activo" ? "success" : "secondary"}>
            {estado}
          </GoreBadge>
        </div>
        <p className="text-xs text-muted-foreground">{email}</p>
        <div className="flex items-center gap-2 pt-1">
          <span className="inline-flex items-center text-xs font-medium text-gore-brand">
             <Icons.Home size={12} className="mr-1" />
            {division}
          </span>
          <span className="text-xs text-gray-400">•</span>
          <span className="text-xs text-gray-500">{cargo}</span>
        </div>
        {estamento && (
             <span className="inline-block rounded bg-gray-100 px-2 py-0.5 text-[10px] font-medium text-gray-600">
                {estamento}
             </span>
        )}
      </div>
    </div>
  );
}
