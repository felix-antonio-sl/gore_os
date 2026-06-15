"use client";

import { cn } from "@/lib/utils";
import { TAB_GROUPS, TAB_LABELS, PHASE_RELEVANT_TABS } from "./ipr-constants";

interface IprSidebarNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  currentPhase?: string;
}

export function IprSidebarNav({ activeTab, onTabChange, currentPhase }: IprSidebarNavProps) {
  const relevantTabs = currentPhase ? PHASE_RELEVANT_TABS[currentPhase] ?? [] : [];

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
          {group.tabs.map((tab) => {
            const isRelevant = relevantTabs.includes(tab);
            return (
              <button
                key={tab}
                onClick={() => onTabChange(tab)}
                className={cn(
                  "w-full text-left text-sm px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5",
                  activeTab === tab
                    ? "bg-accent font-medium text-foreground"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
              >
                <span className="flex-1 min-w-0 truncate">{TAB_LABELS[tab] ?? tab}</span>
                {isRelevant && (
                  <span
                    className="inline-block size-1.5 rounded-full bg-primary shrink-0"
                    aria-label="Relevante en esta etapa"
                    title="Relevante en esta etapa"
                  />
                )}
              </button>
            );
          })}
        </div>
      ))}
    </nav>
  );
}
