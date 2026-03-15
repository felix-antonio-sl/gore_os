"use client";

import { cn } from "@/lib/utils";
import { TAB_GROUPS, TAB_LABELS } from "./ipr-constants";

interface IprSidebarNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function IprSidebarNav({ activeTab, onTabChange }: IprSidebarNavProps) {
  return (
    <nav className="py-3 px-2 space-y-1">
      <button
        onClick={() => onTabChange("resumen")}
        className={cn(
          "w-full text-left text-sm px-3 py-1.5 rounded-md transition-colors",
          activeTab === "resumen"
            ? "bg-accent font-medium text-foreground"
            : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
        )}
      >
        Resumen
      </button>

      {TAB_GROUPS.map((group) => (
        <div key={group.label} className="pt-2">
          <p className="px-3 text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wider mb-1">
            {group.label}
          </p>
          {group.tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => onTabChange(tab)}
              className={cn(
                "w-full text-left text-sm px-3 py-1.5 rounded-md transition-colors",
                activeTab === tab
                  ? "bg-accent font-medium text-foreground"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
              )}
            >
              {TAB_LABELS[tab] ?? tab}
            </button>
          ))}
        </div>
      ))}
    </nav>
  );
}
