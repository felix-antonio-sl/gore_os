import * as React from "react";
import { cn } from "../lib/utils";
import { Icons } from "../atoms/GoreIcon";

interface TimelineEvent {
  id: string;
  date: string;
  title: string;
  actor: string;
  description?: string;
  type: "info" | "success" | "warning";
}

export interface ProcessTimelineProps
  extends React.HTMLAttributes<HTMLDivElement> {
  events: TimelineEvent[];
}

export function ProcessTimeline({
  className,
  events,
  ...props
}: ProcessTimelineProps) {
  return (
    <div className={cn("space-y-8 pl-2", className)} {...props}>
      {events.map((event, index) => {
        const isLast = index === events.length - 1;
        return (
          <div key={event.id} className="relative flex gap-4">
            {!isLast && (
              <div className="absolute left-[9px] top-8 h-full w-px bg-gray-200" />
            )}
            <div
              className={cn(
                "relative z-10 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border bg-white",
                event.type === "success"
                  ? "border-gore-success"
                  : event.type === "warning"
                  ? "border-gore-warning"
                  : "border-gray-300"
              )}
            >
              <div
                className={cn(
                  "h-2 w-2 rounded-full",
                  event.type === "success"
                    ? "bg-gore-success"
                    : event.type === "warning"
                    ? "bg-gore-warning"
                    : "bg-gray-300"
                )}
              />
            </div>
            <div className="flex flex-col gap-1 -mt-1">
              <span className="text-xs text-muted-foreground">{event.date}</span>
              <p className="text-sm font-medium text-gore-text leading-none">
                {event.title}
              </p>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Icons.Home size={12} />
                {event.actor}
              </div>
              {event.description && (
                <p className="mt-1 text-sm text-gray-600">
                  {event.description}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
