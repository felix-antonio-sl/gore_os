interface ProgressCellProps {
  value: number;
  label?: string;
}

export function ProgressCell({ value, label }: ProgressCellProps) {
  const pct = Math.max(0, Math.min(100, value));
  const color = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="flex items-center gap-2 min-w-[80px]">
      <div className="flex-1 h-2 rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${color} transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs tabular-nums text-muted-foreground w-9 text-right">
        {label ?? `${Math.round(pct)}%`}
      </span>
    </div>
  );
}
