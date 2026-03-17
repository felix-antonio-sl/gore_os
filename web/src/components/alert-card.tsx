"use client";

import { AlertTriangle, AlertCircle, Info } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { formatDateTimeShort } from "@/lib/format";
import { ALERT_SEVERITY_BORDER, ALERT_SEVERITY_ICON_COLOR } from "@/lib/status-colors";
import type { AlertaListItem } from "@/types";

interface AlertCardProps {
  alert: AlertaListItem;
  onAttend?: (id: string) => void;
  onViewSubject?: (type: string, id: string) => void;
}

const SEVERITY_ICON_COMPONENT: Record<string, typeof AlertTriangle> = {
  CRITICO: AlertTriangle,
  ALTO: AlertTriangle,
  ATENCION: AlertCircle,
  INFO: Info,
};

export function AlertCard({ alert, onAttend, onViewSubject }: AlertCardProps) {
  const severity = alert.severity ?? "INFO";
  const borderClass = ALERT_SEVERITY_BORDER[severity] ?? ALERT_SEVERITY_BORDER.INFO;
  const IconComp = SEVERITY_ICON_COMPONENT[severity] ?? Info;
  const iconColor = ALERT_SEVERITY_ICON_COLOR[severity] ?? ALERT_SEVERITY_ICON_COLOR.INFO;

  return (
    <Card className={cn("border-l-4 rounded-lg py-4", borderClass)}>
      <CardContent className="px-5 py-0">
        <div className="flex items-start gap-3">
          <div className="mt-0.5">
            <IconComp className={cn("size-4 shrink-0", iconColor)} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <p className="font-semibold text-sm">{alert.alert_type_label}</p>
              <span className="text-xs text-muted-foreground shrink-0">
                {formatDateTimeShort(alert.triggered_at)}
              </span>
            </div>
            <p className="text-sm text-muted-foreground mt-1">{alert.message}</p>
            {alert.subject_label && (
              <p className="text-xs text-muted-foreground mt-1 italic">{alert.subject_label}</p>
            )}
            {(onAttend || onViewSubject) && (
              <div className="flex gap-2 mt-3">
                {onAttend && !alert.attended_at && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onAttend(alert.id)}
                  >
                    Atender
                  </Button>
                )}
                {onViewSubject && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onViewSubject(alert.subject_type, alert.subject_id)}
                  >
                    Ver
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
