"use client";

import { useRouter } from "next/navigation";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ArrowLeft, MoreVertical, Pencil, UserPlus } from "lucide-react";
import { MechanismBadge, PhaseBadge } from "./ipr-badges";
import type { IprDetail } from "./ipr-constants";

interface IprStickyHeaderProps {
  ipr: IprDetail;
  canEdit: boolean;
  canAssign: boolean;
  onEdit: () => void;
  onAssign: () => void;
}

const TERMINAL_STATES = ["CERRADO", "ANULADO", "TERMINADO_ANTICIPADAMENTE", "INADMISIBLE"];

export function IprStickyHeader({ ipr, canEdit, canAssign, onEdit, onAssign }: IprStickyHeaderProps) {
  const router = useRouter();
  const isTerminal = TERMINAL_STATES.includes(ipr.status ?? "");
  const hasActions = !isTerminal && (canEdit || canAssign);

  return (
    <header className="sticky top-0 z-30 bg-background/95 backdrop-blur border-b px-4 py-2">
      <div className="flex items-center gap-2 min-w-0">
        <Button variant="ghost" size="sm" className="h-8 px-2 shrink-0" onClick={() => router.back()}>
          <ArrowLeft className="size-4 mr-1" />
          Volver
        </Button>

        <span className="font-mono text-xs text-muted-foreground shrink-0">{ipr.codigo_bip}</span>
        <span className="text-muted-foreground shrink-0">·</span>
        <span className="text-sm font-medium truncate min-w-0 flex-1">{ipr.name}</span>

        <div className="flex items-center gap-1.5 shrink-0">
          <MechanismBadge
            code={ipr.mechanism}
            label={ipr.mechanism_label ?? ipr.mechanism}
            size="sm"
            className="hidden sm:inline-flex"
          />
          {ipr.status && <StatusBadge status={ipr.status} size="sm" />}
          <PhaseBadge code={ipr.mcd_phase} label={ipr.mcd_phase} size="sm" />
          {hasActions && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="size-7">
                  <MoreVertical className="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {canEdit && (
                  <DropdownMenuItem onClick={onEdit}>
                    <Pencil className="size-3.5 mr-2" /> Editar
                  </DropdownMenuItem>
                )}
                {canAssign && (
                  <DropdownMenuItem onClick={onAssign}>
                    <UserPlus className="size-3.5 mr-2" /> Asignar Responsable
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4 ml-11 text-xs text-muted-foreground mt-0.5 flex-wrap">
        {ipr.current_actor && (
          <span className="flex items-center gap-1.5">
            <span>Le toca a:</span>
            <Badge variant="outline" className="font-normal text-[10px] px-1.5 py-0">
              {ipr.current_actor.role_label}
            </Badge>
            <span className="text-muted-foreground">— {ipr.current_actor.action}</span>
          </span>
        )}
        {ipr.executor_name && <span className="hidden sm:inline">Ejecutor: <span className="text-foreground">{ipr.executor_name}</span></span>}
        {ipr.formulator_name && <span className="hidden sm:inline">Responsable: <span className="text-foreground">{ipr.formulator_name}</span></span>}
      </div>
    </header>
  );
}
