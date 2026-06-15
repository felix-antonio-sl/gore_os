"use client";

import * as React from "react";
import { Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

interface DateFieldProps {
  /** ISO value `yyyy-mm-dd` (or "" when empty) — same contract as <input type="date">. */
  value: string;
  /** Emits ISO `yyyy-mm-dd` when a complete valid date is entered, "" when cleared. */
  onChange: (value: string) => void;
  id?: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  /** Optional lower bound (ISO) for validation styling. */
  min?: string;
  "aria-invalid"?: boolean;
}

/** "yyyy-mm-dd" → "dd/mm/aaaa" (Chilean display). Empty/invalid → "". */
function isoToDisplay(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso ?? "");
  if (!m) return "";
  return `${m[3]}/${m[2]}/${m[1]}`;
}

/** "dd/mm/aaaa" → "yyyy-mm-dd" if it is a real calendar date, else "". */
function displayToIso(display: string): string {
  const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(display);
  if (!m) return "";
  const day = Number(m[1]);
  const month = Number(m[2]);
  const year = Number(m[3]);
  if (month < 1 || month > 12 || day < 1 || day > 31 || year < 1900 || year > 2100) return "";
  const d = new Date(year, month - 1, day);
  // Reject overflow dates like 31/02/2026.
  if (d.getFullYear() !== year || d.getMonth() !== month - 1 || d.getDate() !== day) return "";
  return `${m[3]}-${m[2]}-${m[1]}`;
}

/** Mask raw input into "dd/mm/aaaa" as the user types (digits only, auto slashes). */
function mask(input: string): string {
  const digits = input.replace(/\D/g, "").slice(0, 8);
  const parts = [digits.slice(0, 2), digits.slice(2, 4), digits.slice(4, 8)].filter(Boolean);
  return parts.join("/");
}

/**
 * Chilean date input. Always shows and parses `dd/mm/aaaa`, never the browser's
 * locale-dependent `mm/dd/yyyy`. Inherits the standard input tokens (dark mode included).
 * Drop-in replacement for `<input type="date" value onChange>`.
 */
export function DateField({
  value,
  onChange,
  id,
  placeholder = "dd/mm/aaaa",
  disabled,
  className,
  min,
  "aria-invalid": ariaInvalid,
}: DateFieldProps) {
  const [display, setDisplay] = React.useState(() => isoToDisplay(value));

  // Re-sync from the controlled value only when it represents a different date,
  // so we never clobber what the user is mid-typing.
  React.useEffect(() => {
    if (displayToIso(display) !== value) {
      setDisplay(isoToDisplay(value));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const masked = mask(e.target.value);
    setDisplay(masked);
    if (masked === "") {
      onChange("");
      return;
    }
    const iso = displayToIso(masked);
    if (iso) onChange(iso);
  };

  // Invalid = fully typed but not a real date, or before `min`.
  const iso = displayToIso(display);
  const invalid =
    ariaInvalid ||
    (display.length === 10 && !iso) ||
    (!!iso && !!min && iso < min);

  return (
    <div className={cn("relative", className)}>
      <input
        id={id}
        type="text"
        inputMode="numeric"
        autoComplete="off"
        value={display}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        aria-invalid={invalid || undefined}
        className={cn(
          "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 pr-9 text-sm shadow-xs transition-colors",
          "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
          "disabled:cursor-not-allowed disabled:opacity-50",
          invalid && "border-red-400 focus-visible:ring-red-400 dark:border-red-700",
        )}
      />
      <Calendar className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
    </div>
  );
}
