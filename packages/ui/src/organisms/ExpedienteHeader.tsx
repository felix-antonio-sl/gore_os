import * as React from "react";
import { cn } from "../lib/utils";
import { GoreBadge } from "../atoms/GoreBadge";
import { Icons } from "../atoms/GoreIcon";

export interface ExpedienteHeaderProps {
  className?: string;
  type: string;
  id: string;
  title: string;
  status: string;
  metadata: {
    label: string;
    value: string;
  }[];
}

export function ExpedienteHeader({
  className,
  type,
  id,
  title,
  status,
  metadata,
}: ExpedienteHeaderProps) {
  return (
    <div className={cn("border-b bg-white pb-6 pt-4", className)}>
      <div className="mb-4 flex items-center gap-2 text-sm text-muted-foreground">
        <span className="font-semibold uppercase tracking-wider text-gore-brand">
          {type}
        </span>
        <span>•</span>
        <span>{id}</span>
      </div>
      <div className="mb-6 flex items-start justify-between gap-4">
        <h1 className="text-3xl font-bold tracking-tight text-gore-brand">
          {title}
        </h1>
        <GoreBadge variant="secondary" className="px-3 py-1 text-sm">
          {status}
        </GoreBadge>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {metadata.map((item) => (
          <div key={item.label} className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">
              {item.label}
            </p>
            <p className="text-sm font-medium text-gore-text">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
