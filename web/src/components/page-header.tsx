import { ReactNode } from "react";
import { Breadcrumb } from "@/components/breadcrumb";
import type { BreadcrumbItem } from "@/lib/breadcrumbs";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  breadcrumbs?: BreadcrumbItem[];
  accentColor?: string;  // Tailwind color name: "indigo", "amber", "emerald", etc.
}

const ACCENT_BORDER: Record<string, string> = {
  indigo: "border-l-indigo-500",
  amber: "border-l-amber-500",
  emerald: "border-l-emerald-500",
  violet: "border-l-violet-500",
  rose: "border-l-rose-500",
  cyan: "border-l-cyan-500",
  teal: "border-l-teal-500",
};

export function PageHeader({ title, description, actions, breadcrumbs, accentColor }: PageHeaderProps) {
  const borderClass = accentColor
    ? `border-l-4 ${ACCENT_BORDER[accentColor] ?? ""} pl-3`
    : "";

  return (
    <div className="animate-in fade-in duration-300">
      {breadcrumbs && <Breadcrumb items={breadcrumbs} />}
      <div className={`flex items-center justify-between ${borderClass}`}>
        <div>
          <h1 className="text-2xl font-bold">{title}</h1>
          {description && (
            <p className="text-muted-foreground text-sm mt-1">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}
