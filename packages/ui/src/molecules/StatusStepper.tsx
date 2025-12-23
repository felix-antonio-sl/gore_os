import * as React from "react";
import { cn } from "../lib/utils";
import { GoreIcon, Icons } from "../atoms/GoreIcon";

interface Step {
  id: string;
  label: string;
  status: "pending" | "current" | "completed" | "error";
}

export interface StatusStepperProps extends React.HTMLAttributes<HTMLDivElement> {
  steps: Step[];
}

export function StatusStepper({ className, steps, ...props }: StatusStepperProps) {
  return (
    <div className={cn("flex w-full items-center", className)} {...props}>
      {steps.map((step, index) => {
        const isLast = index === steps.length - 1;
        return (
          <React.Fragment key={step.id}>
            <div className="relative flex flex-col items-center group">
              <div
                className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-full border-2 text-xs font-semibold",
                  step.status === "completed"
                    ? "border-gore-success bg-gore-success text-white"
                    : step.status === "current"
                    ? "border-gore-brand bg-white text-gore-brand"
                    : step.status === "error"
                    ? "border-gore-error bg-gore-error text-white"
                    : "border-gray-300 bg-white text-gray-500"
                )}
              >
                {step.status === "completed" ? (
                  <Icons.CheckCircle size={16} className="text-white" />
                ) : step.status === "error" ? (
                  <Icons.AlertTriangle size={16} className="text-white" />
                ) : (
                  index + 1
                )}
              </div>
              <span
                className={cn(
                  "absolute -bottom-6 w-32 text-center text-xs font-medium",
                  step.status === "current" ? "text-gore-brand" : "text-gray-500"
                )}
              >
                {step.label}
              </span>
            </div>
            {!isLast && (
              <div
                className={cn(
                  "flex-1 h-0.5 mx-2",
                  step.status === "completed" ? "bg-gore-success" : "bg-gray-300"
                )}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
