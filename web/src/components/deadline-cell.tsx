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

  const relativeText =
    dr < 0 ? `hace ${Math.abs(dr)}d` :
    dr === 0 ? "hoy" :
    dr <= 7 ? `en ${dr}d` :
    null;

  return (
    <div>
      {relativeText ? (
        <>
          <span className={`text-sm font-medium ${color}`}>{relativeText}</span>
          <div className="text-[10px] text-muted-foreground">{formatDate(dateStr)}</div>
        </>
      ) : (
        <span className="text-sm text-muted-foreground">{formatDate(dateStr)}</span>
      )}
    </div>
  );
}
