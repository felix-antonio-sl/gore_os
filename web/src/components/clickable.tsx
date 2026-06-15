"use client";

import { ReactNode, KeyboardEvent } from "react";
import { cn } from "@/lib/utils";

interface ClickableProps {
  onClick: () => void;
  children: ReactNode;
  className?: string;
  disabled?: boolean;
  ariaLabel?: string;
}

/**
 * Accessible wrapper for clickable non-button elements.
 * Adds role="button", keyboard activation (Enter/Space) and focus ring,
 * so visual cards/rows behave like real buttons for keyboard + screen readers.
 * Replaces the ~111 bare `<div onClick>` patterns across the app.
 */
export function Clickable({ onClick, children, className, disabled, ariaLabel }: ClickableProps) {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (disabled) return;
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onClick();
    }
  };

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-disabled={disabled || undefined}
      aria-label={ariaLabel}
      onClick={() => !disabled && onClick()}
      onKeyDown={handleKeyDown}
      className={cn(
        "cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 rounded-md",
        disabled && "cursor-not-allowed opacity-60",
        className,
      )}
    >
      {children}
    </div>
  );
}
