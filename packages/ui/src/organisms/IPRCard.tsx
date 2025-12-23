import * as React from "react";
import { cn } from "../lib/utils";
import { GoreBadge } from "../atoms/GoreBadge";
import { Icons } from "../atoms/GoreIcon";
import { formatCurrency } from "../lib/formatters";

export interface IPRCardProps {
  className?: string;
  code: string;
  name: string;
  amount: number;
  stage: string;
  location?: string;
  status: "active" | "alert" | "finished";
  onClick?: () => void;
}

export function IPRCard({
  className,
  code,
  name,
  amount,
  stage,
  location,
  status,
  onClick,
}: IPRCardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "group cursor-pointer rounded-lg border bg-card text-card-foreground shadow-sm transition-all hover:shadow-md",
        status === "alert" && "border-l-4 border-l-gore-warning",
        className
      )}
    >
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-xs font-medium text-muted-foreground">
              BIP {code}
            </span>
            <h3 className="font-semibold leading-none tracking-tight text-gore-brand group-hover:underline">
              {name}
            </h3>
          </div>
          <GoreBadge
            variant={
              status === "alert"
                ? "destructive"
                : status === "finished"
                ? "success"
                : "secondary"
            }
          >
            {stage}
          </GoreBadge>
        </div>
        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center text-sm text-muted-foreground">
            {location && (
              <>
                <Icons.Home size={14} className="mr-1 text-gray-400" />
                {location}
              </>
            )}
          </div>
          <div className="text-lg font-bold text-gore-text">
            {formatCurrency(amount)}
          </div>
        </div>
      </div>
    </div>
  );
}
