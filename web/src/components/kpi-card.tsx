"use client";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: number;
  sublabel: string;
  color: "red" | "orange" | "amber" | "green" | "blue" | "gray";
  onClick?: () => void;
}

const colorMap: Record<string, string> = {
  red: "border-l-red-600 bg-red-50",
  orange: "border-l-orange-600 bg-orange-50",
  amber: "border-l-amber-500 bg-amber-50",
  green: "border-l-green-600 bg-green-50",
  blue: "border-l-blue-600 bg-blue-50",
  gray: "border-l-gray-400 bg-gray-50",
};

const valueColorMap: Record<string, string> = {
  red: "text-red-700",
  orange: "text-orange-700",
  amber: "text-amber-700",
  green: "text-green-700",
  blue: "text-blue-700",
  gray: "text-gray-700",
};

export function KpiCard({ label, value, sublabel, color, onClick }: KpiCardProps) {
  return (
    <Card
      className={cn(
        "border-l-4 rounded-lg py-4",
        colorMap[color],
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
        <p className={cn("text-3xl font-bold", valueColorMap[color])}>{value}</p>
        <p className="text-xs text-muted-foreground mt-1">{sublabel}</p>
      </CardContent>
    </Card>
  );
}
