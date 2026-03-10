/**
 * Centralized signal and status color definitions.
 * All components rendering VERDE/AMARILLO/ROJO signals MUST import from here.
 */

/** Semáforo signal — Tailwind classes for Badge/Card backgrounds */
export const SIGNAL_BG: Record<string, string> = {
  VERDE: "bg-green-100 border-green-500",
  AMARILLO: "bg-amber-100 border-amber-500",
  ROJO: "bg-red-100 border-red-500",
};

export const SIGNAL_DOT: Record<string, string> = {
  VERDE: "bg-green-500",
  AMARILLO: "bg-amber-500",
  ROJO: "bg-red-500",
};

export const SIGNAL_TEXT: Record<string, string> = {
  VERDE: "text-green-700",
  AMARILLO: "text-amber-700",
  ROJO: "text-red-700",
};

export const SIGNAL_LABEL: Record<string, string> = {
  VERDE: "OK",
  AMARILLO: "Atención",
  ROJO: "Crítico",
};

/** Semáforo signal — Badge outline classes (for inline badges) */
export const SIGNAL_BADGE: Record<string, string> = {
  VERDE: "bg-green-100 text-green-700 border-green-300",
  AMARILLO: "bg-amber-100 text-amber-700 border-amber-300",
  ROJO: "bg-red-100 text-red-700 border-red-300",
};

/** Semáforo signal — hex colors for chart strokes (recharts) */
export const SIGNAL_HEX: Record<string, string> = {
  VERDE: "#22c55e",
  AMARILLO: "#f59e0b",
  ROJO: "#ef4444",
};
