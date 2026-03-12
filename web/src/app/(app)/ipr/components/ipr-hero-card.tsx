import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Pencil, UserPlus } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate, formatCurrency } from "@/lib/format";
import { alertBorderMap, mechanismColors, mcdPhaseColors } from "./ipr-constants";
import type { IprDetail } from "./ipr-constants";

interface IprHeroCardProps {
  ipr: IprDetail;
  canEdit: boolean;
  canAssign: boolean;
  onEdit: () => void;
  onAssign: () => void;
}

export function IprHeroCard({ ipr, canEdit, canAssign, onEdit, onAssign }: IprHeroCardProps) {
  const borderClass = ipr.alert_level ? alertBorderMap[ipr.alert_level] : "";

  return (
    <div
      className={cn(
        "rounded-xl border bg-card p-5 border-l-4",
        borderClass || "border-l-border"
      )}
    >
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-mono text-xs text-muted-foreground">{ipr.codigo_bip}</span>
            {ipr.ipr_type && (
              <Badge variant="outline" className="text-xs">{ipr.ipr_type}</Badge>
            )}
            {ipr.status && <StatusBadge status={ipr.status} size="sm" />}
          </div>
          <h1 className="text-xl font-bold">{ipr.name}</h1>
          {ipr.description && (
            <p className="text-sm text-muted-foreground mt-1">{ipr.description}</p>
          )}
        </div>
        <div className="flex flex-col items-end gap-2 shrink-0">
          <div className="text-right">
            <p className="text-2xl font-bold">{formatCurrency(ipr.total_budget)}</p>
            <p className="text-xs text-muted-foreground">Presupuesto total</p>
          </div>
          <div className="flex gap-2">
            {canEdit && (
              <Button size="sm" variant="outline" onClick={onEdit}>
                <Pencil className="size-4 mr-1" />
                Editar
              </Button>
            )}
            {canAssign && (
              <Button size="sm" variant="outline" onClick={onAssign}>
                <UserPlus className="size-4 mr-1" />
                Asignar Responsable
              </Button>
            )}
          </div>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm">
        {ipr.mechanism && (
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">Mecanismo:</span>
            <Badge variant="outline" className={cn("text-xs", mechanismColors[ipr.mechanism])}>
              {ipr.mechanism}
            </Badge>
            {ipr.mechanism_label && (
              <span className="text-xs text-muted-foreground">{ipr.mechanism_label}</span>
            )}
          </div>
        )}
        {ipr.funding_source && (
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">Fuente:</span>
            <span className="font-medium">{ipr.fund_category_label || ipr.funding_source}</span>
          </div>
        )}
        {ipr.mcd_phase && (
          <div className="flex items-center gap-1.5">
            <span className="text-muted-foreground">Fase MCD:</span>
            <Badge variant="outline" className={cn("text-xs", mcdPhaseColors[ipr.mcd_phase])}>
              {ipr.mcd_phase}
            </Badge>
            {ipr.mcd_phase_label && (
              <span className="text-xs text-muted-foreground">{ipr.mcd_phase_label}</span>
            )}
          </div>
        )}
        {ipr.executor_name && (
          <div>
            <span className="text-muted-foreground">Ejecutor: </span>
            <span className="font-medium">{ipr.executor_name}</span>
          </div>
        )}
        {ipr.investment_sector && (
          <div>
            <span className="text-muted-foreground">Sector: </span>
            <span className="font-medium">{ipr.investment_sector}</span>
          </div>
        )}
        {ipr.start_date && (
          <div>
            <span className="text-muted-foreground">Inicio: </span>
            <span className="font-medium">{formatDate(ipr.start_date)}</span>
          </div>
        )}
        {ipr.end_date && (
          <div>
            <span className="text-muted-foreground">Termino: </span>
            <span className="font-medium">{formatDate(ipr.end_date)}</span>
          </div>
        )}
      </div>
    </div>
  );
}
