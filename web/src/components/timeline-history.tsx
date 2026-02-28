"use client";

import { StatusBadge } from "@/components/status-badge";
import { formatDateTimeShort } from "@/lib/format";
import type { HistoryEntry } from "@/types";

interface TimelineHistoryProps {
  entries: HistoryEntry[];
}

export function TimelineHistory({ entries }: TimelineHistoryProps) {
  if (!entries || entries.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">Sin historial disponible.</p>
    );
  }

  return (
    <div className="relative space-y-0">
      {entries.map((entry, index) => (
        <div key={entry.id} className="flex gap-4 relative">
          {/* Vertical line */}
          {index < entries.length - 1 && (
            <div className="absolute left-[11px] top-6 bottom-0 w-px bg-border" />
          )}
          {/* Dot */}
          <div className="mt-1 shrink-0 size-6 rounded-full border-2 border-primary bg-background flex items-center justify-center z-10">
            <div className="size-2 rounded-full bg-primary" />
          </div>
          {/* Content */}
          <div className="pb-6 flex-1 min-w-0">
            <p className="text-xs text-muted-foreground mb-1">
              {formatDateTimeShort(entry.changed_at)}
              {entry.changed_by_name && (
                <span className="ml-2 font-medium text-foreground">
                  {entry.changed_by_name}
                </span>
              )}
            </p>
            <div className="flex flex-wrap items-center gap-2">
              {entry.previous_state && (
                <>
                  <StatusBadge status={entry.previous_state} size="sm" />
                  <span className="text-muted-foreground text-xs">→</span>
                </>
              )}
              <StatusBadge status={entry.new_state} size="sm" />
            </div>
            {entry.comment && (
              <p className="text-sm italic text-muted-foreground mt-1">
                &ldquo;{entry.comment}&rdquo;
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
