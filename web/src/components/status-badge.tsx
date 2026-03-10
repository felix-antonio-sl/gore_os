"use client";

import { CheckIcon, XIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "default";
}

export function StatusBadge({ status, size = "default" }: StatusBadgeProps) {
  const sizeClass = size === "sm" ? "text-[10px] px-1.5 py-0" : "";

  switch (status) {
    case "PENDIENTE":
      return (
        <Badge variant="outline" className={cn("border-gray-400 text-gray-800", sizeClass)}>
          Pendiente
        </Badge>
      );
    case "EN_PROGRESO":
      return (
        <Badge variant="default" className={cn("bg-blue-600", sizeClass)}>
          En Progreso
        </Badge>
      );
    case "COMPLETADO":
      return (
        <Badge variant="default" className={cn("bg-amber-500", sizeClass)}>
          Completado
        </Badge>
      );
    case "VERIFICADO":
      return (
        <Badge variant="default" className={cn("bg-green-600", sizeClass)}>
          <CheckIcon className="size-3" />
          Verificado
        </Badge>
      );
    case "VENCIDO":
      return (
        <Badge variant="destructive" className={sizeClass}>
          Vencido
        </Badge>
      );
    case "CANCELADO":
      return (
        <Badge variant="secondary" className={cn("line-through", sizeClass)}>
          Cancelado
        </Badge>
      );
    case "ABIERTO":
      return (
        <Badge variant="outline" className={cn("border-red-500 text-red-600", sizeClass)}>
          Abierto
        </Badge>
      );
    case "EN_GESTION":
      return (
        <Badge variant="default" className={cn("bg-blue-600", sizeClass)}>
          En Gestión
        </Badge>
      );
    case "RESUELTO":
      return (
        <Badge variant="default" className={cn("bg-green-600", sizeClass)}>
          <CheckIcon className="size-3" />
          Resuelto
        </Badge>
      );
    case "CERRADO_SIN_RESOLVER":
      return (
        <Badge variant="secondary" className={sizeClass}>
          <XIcon className="size-3" />
          Cerrado sin Resolver
        </Badge>
      );
    case "EN_REVISION_RTF":
      return (
        <Badge variant="outline" className={cn("border-amber-400 text-amber-700 bg-amber-50", sizeClass)}>
          En Revisión RTF
        </Badge>
      );
    case "VISADA_RTF":
      return (
        <Badge variant="outline" className={cn("border-blue-400 text-blue-700 bg-blue-50", sizeClass)}>
          Visada RTF
        </Badge>
      );
    case "EN_REVISION_UCR":
      return (
        <Badge variant="outline" className={cn("border-indigo-400 text-indigo-700 bg-indigo-50", sizeClass)}>
          En Revisión UCR
        </Badge>
      );
    case "OBSERVADA":
      return (
        <Badge variant="outline" className={cn("border-orange-400 text-orange-700 bg-orange-50", sizeClass)}>
          Observada
        </Badge>
      );
    case "APROBADA":
      return (
        <Badge variant="default" className={cn("bg-green-600", sizeClass)}>
          <CheckIcon className="size-3" />
          Aprobada
        </Badge>
      );
    case "RECHAZADA":
      return (
        <Badge variant="destructive" className={sizeClass}>
          <XIcon className="size-3" />
          Rechazada
        </Badge>
      );
    default:
      return (
        <Badge variant="secondary" className={sizeClass}>
          {status}
        </Badge>
      );
  }
}
