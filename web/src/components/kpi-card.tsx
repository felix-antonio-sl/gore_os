"use client";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { KPI_CARD_BG, KPI_CARD_VALUE } from "@/lib/status-colors";

interface KpiCardProps {
  label: string;
  value: number;
  sublabel: string;
  color: "red" | "orange" | "amber" | "green" | "blue" | "gray";
  onClick?: () => void;
}

export function KpiCard({ label, value, sublabel, color, onClick }: KpiCardProps) {
  return (
    <Card
      className={cn(
        "border-l-4 rounded-lg py-4",
        KPI_CARD_BG[color],
        onClick && "cursor-pointer hover:shadow-md transition-shadow"
      )}
      onClick={onClick}
      {...(onClick ? {
        role: "button",
        tabIndex: 0,
        onKeyDown: (e: React.KeyboardEvent) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onClick(); } },
      } : {})}
    >
      <CardContent className="px-5 py-0">
        <p className="text-sm font-medium text-muted-foreground mb-1">{label}</p>
        <p className={cn("text-3xl font-bold", KPI_CARD_VALUE[color])}>{value}</p>
        <p className="text-xs text-muted-foreground mt-1">{sublabel}</p>
      </CardContent>
    </Card>
  );
}
