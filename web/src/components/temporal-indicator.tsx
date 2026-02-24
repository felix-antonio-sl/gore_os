"use client";

import { Badge } from "@/components/ui/badge";

interface TemporalIndicatorProps {
  daysRemaining: number;
  state: string;
}

export function TemporalIndicator({ daysRemaining, state }: TemporalIndicatorProps) {
  if (state === "VERIFICADO" || state === "CANCELADO") {
    return null;
  }

  if (state === "COMPLETADO") {
    return (
      <Badge variant="default" className="bg-amber-500">
        Por verificar
      </Badge>
    );
  }

  if (daysRemaining <= -5) {
    return (
      <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
        Vencido {Math.abs(daysRemaining)}d
      </span>
    );
  }

  if (daysRemaining < 0) {
    return (
      <span className="inline-flex items-center rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700">
        Vencido {Math.abs(daysRemaining)}d
      </span>
    );
  }

  if (daysRemaining <= 1) {
    return (
      <span className="inline-flex items-center rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700">
        Vence mañana
      </span>
    );
  }

  if (daysRemaining <= 3) {
    return (
      <span className="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
        Vence en {daysRemaining}d
      </span>
    );
  }

  return (
    <span className="text-xs text-muted-foreground">
      en {daysRemaining}d
    </span>
  );
}
