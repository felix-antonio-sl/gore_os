import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface TrendIndicatorProps {
  direction: "up" | "down" | "flat";
  label?: string;
}

export function TrendIndicator({ direction, label }: TrendIndicatorProps) {
  const config = {
    up: { icon: TrendingUp, color: "text-green-600 dark:text-green-400" },
    down: { icon: TrendingDown, color: "text-red-600 dark:text-red-400" },
    flat: { icon: Minus, color: "text-muted-foreground" },
  }[direction];

  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1 ${config.color}`}>
      <Icon className="size-3.5" />
      {label && <span className="text-xs">{label}</span>}
    </span>
  );
}
