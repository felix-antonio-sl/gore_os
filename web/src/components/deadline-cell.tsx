import { formatDate } from "@/lib/format";

interface DeadlineCellProps {
  date: string | null;
  daysRemaining?: number | null;
}

export function DeadlineCell({ date: dateStr, daysRemaining }: DeadlineCellProps) {
  if (!dateStr) return <span className="text-muted-foreground text-xs">—</span>;

  const dr = daysRemaining ?? Math.round(
    (new Date(dateStr).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );

  const color =
    dr < 0 ? "text-red-600 dark:text-red-400" :
    dr <= 7 ? "text-amber-600 dark:text-amber-400" :
    "text-muted-foreground";

  const badge =
    dr < 0 ? `${Math.abs(dr)}d vencido` :
    dr === 0 ? "Hoy" :
    dr <= 7 ? `${dr}d` :
    null;

  return (
    <div className="flex items-center gap-1.5">
      <span className={`text-sm ${color}`}>{formatDate(dateStr)}</span>
      {badge && (
        <span className={`text-[10px] font-medium ${color}`}>({badge})</span>
      )}
    </div>
  );
}
