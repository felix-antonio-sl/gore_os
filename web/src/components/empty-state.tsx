import { ReactNode } from "react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  compact?: boolean;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  compact = false,
}: EmptyStateProps) {
  if (compact) {
    return <p className="text-sm text-muted-foreground">{title}</p>;
  }

  return (
    <div className="flex flex-col items-center gap-2 py-12 text-muted-foreground">
      {icon ?? <Inbox className="size-10 stroke-1" />}
      <p className="text-sm font-medium">{title}</p>
      {description && <p className="text-xs">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
