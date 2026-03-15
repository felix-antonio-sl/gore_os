"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, ChevronRight, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ActionItem } from "@/types";

interface IprGroup {
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
  items: ActionItem[];
  hasUrgent: boolean;
}

interface ModuleMyWorkProps {
  items: ActionItem[];
}

export function ModuleMyWork({ items }: ModuleMyWorkProps) {
  const router = useRouter();

  // Group by ipr_id
  const groupMap = new Map<string, IprGroup>();
  for (const item of items) {
    const key = item.ipr_id ?? "__general__";
    if (!groupMap.has(key)) {
      groupMap.set(key, {
        ipr_id: item.ipr_id ?? null,
        ipr_codigo_bip: item.ipr_codigo_bip ?? null,
        items: [],
        hasUrgent: false,
      });
    }
    const g = groupMap.get(key)!;
    g.items.push(item);
    if (item.temporal === "VENCIDO" || item.temporal === "HOY") {
      g.hasUrgent = true;
    }
  }
  const groups = Array.from(groupMap.values()).sort((a, b) => {
    if (a.hasUrgent && !b.hasUrgent) return -1;
    if (!a.hasUrgent && b.hasUrgent) return 1;
    return 0;
  });

  const [collapsed, setCollapsed] = useState<Set<string>>(() => {
    const set = new Set<string>();
    for (const g of groups) {
      if (!g.hasUrgent) set.add(g.ipr_id ?? "__general__");
    }
    return set;
  });

  const toggle = (key: string) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  if (items.length === 0) return null;

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Mi Trabajo</h3>
        <span className="text-xs text-muted-foreground tabular-nums">{items.length} pendientes</span>
      </div>

      <div className="space-y-2">
        {groups.map((group) => {
          const key = group.ipr_id ?? "__general__";
          const isCollapsed = collapsed.has(key);
          return (
            <div key={key}>
              <button
                onClick={() => toggle(key)}
                className="w-full flex items-center gap-2 text-xs py-1 hover:bg-muted/50 rounded px-1 -mx-1"
              >
                {isCollapsed ? (
                  <ChevronRight className="size-3.5 text-muted-foreground shrink-0" />
                ) : (
                  <ChevronDown className="size-3.5 text-muted-foreground shrink-0" />
                )}
                <span className="font-mono text-muted-foreground">
                  {group.ipr_codigo_bip ?? "General"}
                </span>
                {group.hasUrgent && (
                  <span className="size-1.5 rounded-full bg-red-500 shrink-0" />
                )}
                <span className="text-muted-foreground ml-auto tabular-nums">
                  {group.items.length}
                </span>
              </button>

              {!isCollapsed && (
                <div className="ml-5 space-y-0.5 mt-0.5">
                  {group.items.map((item) => {
                    const dr = item.days_remaining;
                    const isOverdue = dr != null && dr < 0;
                    const isToday = dr === 0;
                    const isUrgent = dr != null && dr > 0 && dr <= 7;

                    return (
                      <div
                        key={`${item.category}-${item.id}`}
                        onClick={() => router.push(item.action_route)}
                        className={cn(
                          "flex items-center gap-2 px-2 py-1.5 rounded text-xs cursor-pointer transition-colors",
                          isOverdue && "bg-red-50 hover:bg-red-100 dark:bg-red-950/30",
                          isToday && "bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/30",
                          !isOverdue && !isToday && "hover:bg-muted/50"
                        )}
                      >
                        <span className={cn(
                          "size-1.5 rounded-full shrink-0",
                          isOverdue ? "bg-red-500" : isToday ? "bg-amber-500" : isUrgent ? "bg-blue-400" : "bg-gray-300"
                        )} />
                        <span className={cn(
                          "flex-1 truncate",
                          isOverdue ? "font-medium" : "text-muted-foreground"
                        )}>
                          {item.title}
                        </span>
                        {dr != null && (
                          <span className={cn(
                            "tabular-nums shrink-0 text-[11px]",
                            isOverdue ? "text-red-600 font-medium" : isToday ? "text-amber-600" : "text-muted-foreground"
                          )}>
                            {isOverdue ? `${dr}d` : isToday ? "hoy" : `${dr}d`}
                          </span>
                        )}
                        <ArrowRight className="size-3 text-muted-foreground/50 shrink-0" />
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
