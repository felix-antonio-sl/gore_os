"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { AlertCircle, Clock, CheckCircle2, AlertTriangle } from "lucide-react";
import type { ActionItem } from "@/types";

const SEVERITY_DOT: Record<string, string> = {
  CRITICO: "bg-red-500",
  ALTO: "bg-orange-500",
  MEDIO: "bg-amber-500",
  BAJO: "bg-green-500",
};

const TEMPORAL_LABEL: Record<string, { text: string; className: string }> = {
  VENCIDO: { text: "Vencido", className: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300" },
  HOY: { text: "Hoy", className: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300" },
  ESTA_SEMANA: { text: "Esta semana", className: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300" },
  FUTURO: { text: "Próximo", className: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300" },
};

const CATEGORY_ICON: Record<string, React.ReactNode> = {
  COMPROMISO: <CheckCircle2 className="size-4" />,
  ALERTA: <AlertCircle className="size-4" />,
  DECISION: <AlertTriangle className="size-4" />,
  ESCALAMIENTO: <AlertTriangle className="size-4" />,
  SLA: <Clock className="size-4" />,
  RIESGO: <AlertCircle className="size-4" />,
};

interface AttentionStripProps {
  items: ActionItem[];
  maxItems?: number;
}

export function AttentionStrip({ items, maxItems = 5 }: AttentionStripProps) {
  const router = useRouter();
  if (items.length === 0) {
    return (
      <div className="flex items-center gap-3 p-4 rounded-lg bg-green-50 border border-green-200 dark:bg-green-950/30 dark:border-green-800 animate-in fade-in duration-200">
        <div className="size-10 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center shrink-0">
          <CheckCircle2 className="size-5 text-green-600" />
        </div>
        <div>
          <p className="text-sm font-medium text-green-800 dark:text-green-200">Al día</p>
          <p className="text-xs text-green-600 dark:text-green-400">No tienes tareas pendientes.</p>
        </div>
      </div>
    );
  }
  const visible = items.slice(0, maxItems);

  return (
    <div className="space-y-2">
      <h2 className="text-sm font-semibold text-muted-foreground">Requiere atención</h2>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {visible.map((item) => {
          const temporal = item.temporal ? TEMPORAL_LABEL[item.temporal] : null;
          return (
            <div
              key={`${item.category}-${item.id}`}
              className="rounded-lg border bg-card p-3 shadow-sm animate-in fade-in duration-200"
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className={`size-2 rounded-full ${SEVERITY_DOT[item.severity]}`} />
                {temporal && (
                  <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${temporal.className}`}>
                    {temporal.text}
                  </span>
                )}
                <span className="text-muted-foreground">{CATEGORY_ICON[item.category]}</span>
              </div>
              <p className="text-sm font-medium leading-tight line-clamp-2">{item.title}</p>
              {item.subtitle && (
                <p className="text-xs text-muted-foreground mt-0.5">{item.subtitle}</p>
              )}
              <div className="mt-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7 text-xs"
                  onClick={() => router.push(item.action_route)}
                >
                  {item.action_label}
                </Button>
              </div>
            </div>
          );
        })}
      </div>
      {items.length > maxItems && (
        <p className="text-xs text-muted-foreground">+{items.length - maxItems} más</p>
      )}
    </div>
  );
}
