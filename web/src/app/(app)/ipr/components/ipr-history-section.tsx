"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, ArrowRight } from "lucide-react";
import { StatusBadge } from "@/components/status-badge";
import { formatDateTimeShort } from "@/lib/format";
import type { HistoryEntry } from "@/types";

interface IprHistorySectionProps {
  history: HistoryEntry[];
}

export function IprHistorySection({ history }: IprHistorySectionProps) {
  const [expanded, setExpanded] = useState(false);

  if (history.length === 0) return null;

  return (
    <div className="rounded-xl border bg-card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 text-left"
      >
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium">Historial de Transiciones</h3>
          <span className="text-xs text-muted-foreground">{history.length}</span>
        </div>
        {expanded ? (
          <ChevronDown className="size-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="size-4 text-muted-foreground" />
        )}
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-2">
          {history.map((h) => (
            <div key={h.id} className="flex items-center gap-2 text-xs py-1.5 border-b last:border-0">
              <span className="text-muted-foreground shrink-0 w-28 tabular-nums">
                {formatDateTimeShort(h.changed_at)}
              </span>
              {h.previous_state && (
                <>
                  <StatusBadge status={h.previous_state} size="sm" />
                  <ArrowRight className="size-3 text-muted-foreground shrink-0" />
                </>
              )}
              <StatusBadge status={h.new_state} size="sm" />
              <span className="text-muted-foreground ml-auto truncate max-w-32">
                {h.changed_by_name}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
