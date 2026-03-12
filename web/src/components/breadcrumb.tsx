import Link from "next/link";
import { ChevronRight } from "lucide-react";
import type { BreadcrumbItem } from "@/lib/breadcrumbs";

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  if (items.length <= 1) return null;

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm text-muted-foreground mb-2 min-w-0">
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-1 min-w-0">
          {i > 0 && <ChevronRight className="size-3 shrink-0" />}
          {item.href ? (
            <Link
              href={item.href}
              className="hover:text-foreground transition-colors truncate max-w-[160px]"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground font-medium truncate max-w-[200px]">
              {item.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
}
