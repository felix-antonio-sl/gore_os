import * as React from "react";
import { cn } from "../lib/utils";
import { GoreBadge } from "../atoms/GoreBadge";
import { formatRut } from "../lib/formatters";

export interface ProveedorCardProps {
  className?: string;
  rut: string;
  razonSocial: string;
  giro: string;
  estadoMercadoPublico: string;
}

export function ProveedorCard({
  className,
  rut,
  razonSocial,
  giro,
  estadoMercadoPublico,
}: ProveedorCardProps) {
    const isHabil = estadoMercadoPublico.toLowerCase() === "hábil" || estadoMercadoPublico.toLowerCase() === "habil";
    
  return (
    <div
      className={cn(
        "rounded-lg border bg-card p-4 text-card-foreground shadow-sm",
        className
      )}
    >
      <div className="flex flex-col space-y-1.5">
        <div className="flex items-start justify-between">
            <div className="space-y-1">
                <span className="text-xs font-mono text-muted-foreground">
                    {formatRut(rut)}
                </span>
                <h3 className="font-semibold leading-none tracking-tight text-gore-text">
                    {razonSocial}
                </h3>
            </div>
            <GoreBadge variant={isHabil ? "success" : "destructive"}>
                {estadoMercadoPublico}
            </GoreBadge>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">
            {giro}
        </p>
      </div>
    </div>
  );
}
