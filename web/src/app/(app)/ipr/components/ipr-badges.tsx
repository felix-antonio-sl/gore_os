import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { mechanismColors, mcdPhaseColors, MCD_PHASES } from "./ipr-constants";

const phaseFallbackLabel: Record<string, string> = Object.fromEntries(
  MCD_PHASES.map((p) => [p.code, p.label]),
);

interface BadgeProps {
  code?: string | null;
  label?: string | null;
  size?: "sm" | "default";
  className?: string;
}

const sizeClass = (size?: "sm" | "default") => (size === "sm" ? "text-[10px] px-1.5 py-0" : "text-xs");

/** Financing-mechanism badge (SNI, FRIL, C33…) — dark-mode aware, shared across IPR views. */
export function MechanismBadge({ code, label, size, className }: BadgeProps) {
  if (!code) return null;
  return (
    <Badge variant="outline" className={cn(sizeClass(size), mechanismColors[code] ?? "", className)}>
      {label ?? code}
    </Badge>
  );
}

/** MCD phase badge (F0…F5) — dark-mode aware, shared across IPR views. */
export function PhaseBadge({ code, label, size, className }: BadgeProps) {
  if (!code) return null;
  return (
    <Badge variant="outline" className={cn(sizeClass(size), mcdPhaseColors[code] ?? "", className)}>
      {label ?? phaseFallbackLabel[code] ?? code}
    </Badge>
  );
}
