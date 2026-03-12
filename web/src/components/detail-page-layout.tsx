import { ReactNode } from "react";
import { CheckCircle2 } from "lucide-react";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";

interface DetailPageLayoutProps {
  pathname: string;
  breadcrumbLabel?: string;
  heroContent: ReactNode;
  stepper?: {
    phases: { code: string; label: string }[];
    currentPhase: string;
    phaseColors?: Record<string, string>;
  };
  transitionPanel?: ReactNode;
  children: ReactNode;
}

const DEFAULT_PHASE_COLORS: Record<string, string> = {
  past: "bg-green-500",
  active: "bg-blue-600",
  future: "bg-muted",
};

export function DetailPageLayout({
  pathname,
  breadcrumbLabel,
  heroContent,
  stepper,
  transitionPanel,
  children,
}: DetailPageLayoutProps) {
  const breadcrumbs = buildBreadcrumbs(pathname, breadcrumbLabel);

  return (
    <div className="p-6 space-y-4">
      <Breadcrumb items={breadcrumbs} />
      {heroContent}
      {stepper && (
        <div className="flex items-center gap-1 overflow-x-auto py-2">
          {stepper.phases.map((phase, idx) => {
            const currentIdx = stepper.phases.findIndex(p => p.code === stepper.currentPhase);
            const isPast = idx < currentIdx;
            const isActive = idx === currentIdx;
            const colors = stepper.phaseColors ?? {};
            const dotColor = isPast
              ? (colors[phase.code] ?? DEFAULT_PHASE_COLORS.past)
              : isActive
                ? (colors[phase.code] ?? DEFAULT_PHASE_COLORS.active)
                : DEFAULT_PHASE_COLORS.future;

            return (
              <div key={phase.code} className="flex items-center gap-1">
                {idx > 0 && <div className={`h-0.5 w-4 ${isPast ? "bg-green-500" : "bg-muted"}`} />}
                <div className="flex items-center gap-1.5 shrink-0">
                  {isPast ? (
                    <CheckCircle2 className="size-4 text-green-600" />
                  ) : (
                    <div className={`size-3 rounded-full ${dotColor} ${isActive ? "ring-2 ring-offset-2 ring-blue-300" : ""}`} />
                  )}
                  <span className={`text-xs whitespace-nowrap ${isActive ? "font-semibold" : "text-muted-foreground"}`}>
                    {phase.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
      {transitionPanel}
      {children}
    </div>
  );
}
