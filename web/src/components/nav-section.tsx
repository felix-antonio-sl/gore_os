"use client";

import { useEffect, useState, ReactNode } from "react";
import { ChevronRight } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

interface NavSectionProps {
  id: string;
  label: string;
  defaultOpen?: boolean;
  children: ReactNode;
}

export function NavSection({
  id,
  label,
  defaultOpen = true,
  children,
}: NavSectionProps) {
  const storageKey = `goreos_nav_${id}`;

  const [isOpen, setIsOpen] = useState(() => {
    if (typeof window === "undefined") return defaultOpen;
    const saved = localStorage.getItem(storageKey);
    return saved !== null ? saved === "true" : defaultOpen;
  });

  useEffect(() => {
    localStorage.setItem(storageKey, String(isOpen));
  }, [storageKey, isOpen]);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger className="flex w-full items-center gap-1.5 rounded-md px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-sidebar-foreground/40 hover:text-sidebar-foreground/60 transition-colors">
        <ChevronRight
          className={cn(
            "size-3 shrink-0 transition-transform duration-200",
            isOpen && "rotate-90"
          )}
        />
        {label}
      </CollapsibleTrigger>
      <CollapsibleContent className="flex flex-col gap-0.5">
        {children}
      </CollapsibleContent>
    </Collapsible>
  );
}
