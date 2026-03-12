import { ReactNode } from "react";
import { Breadcrumb } from "@/components/breadcrumb";
import type { BreadcrumbItem } from "@/lib/breadcrumbs";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  breadcrumbs?: BreadcrumbItem[];
}

export function PageHeader({ title, description, actions, breadcrumbs }: PageHeaderProps) {
  return (
    <div className="animate-in fade-in duration-300">
      {breadcrumbs && <Breadcrumb items={breadcrumbs} />}
      <div className="flex items-center justify-between">
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
