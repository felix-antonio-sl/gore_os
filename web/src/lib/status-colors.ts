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

/* ── KPI card colors ─────────────────────────────────────── */

export const KPI_CARD_BG: Record<string, string> = {
  red: "border-l-red-600 bg-red-50",
  orange: "border-l-orange-600 bg-orange-50",
  amber: "border-l-amber-500 bg-amber-50",
  green: "border-l-green-600 bg-green-50",
  blue: "border-l-blue-600 bg-blue-50",
  gray: "border-l-gray-400 bg-gray-50",
};

export const KPI_CARD_VALUE: Record<string, string> = {
  red: "text-red-700",
  orange: "text-orange-700",
  amber: "text-amber-700",
  green: "text-green-700",
  blue: "text-blue-700",
  gray: "text-gray-700",
};

/* ── Alert severity colors ───────────────────────────────── */

export const ALERT_SEVERITY_BORDER: Record<string, string> = {
  CRITICO: "border-l-red-600",
  ALTO: "border-l-orange-600",
  ATENCION: "border-l-amber-500",
  INFO: "border-l-blue-600",
};

export const ALERT_SEVERITY_ICON_COLOR: Record<string, string> = {
  CRITICO: "text-red-600",
  ALTO: "text-orange-600",
  ATENCION: "text-amber-500",
  INFO: "text-blue-600",
};

/* ── Temporal / deadline states ───────────────────────────── */

export interface TemporalState {
  label: string | ((days: number) => string);
  className: string;
  hidden?: boolean;
}

export const TEMPORAL_STATES: {
  terminal: TemporalState;
  completed: TemporalState;
  overdue_old: TemporalState;
  overdue_new: TemporalState;
  urgent: TemporalState;
  soon: TemporalState;
  normal: TemporalState;
} = {
  terminal: { label: "", className: "", hidden: true },
  completed: {
    label: "Por verificar",
    className: "bg-amber-500 text-white border-transparent",
  },
  overdue_old: {
    label: (d: number) => `Vencido ${Math.abs(d)}d`,
    className: "bg-red-100 text-red-700 border-red-300",
  },
  overdue_new: {
    label: (d: number) => `Vencido ${Math.abs(d)}d`,
    className: "bg-orange-100 text-orange-700 border-orange-300",
  },
  urgent: {
    label: "Vence mañana",
    className: "bg-orange-100 text-orange-700 border-orange-300",
  },
  soon: {
    label: (d: number) => `Vence en ${d}d`,
    className: "bg-amber-100 text-amber-700 border-amber-300",
  },
  normal: {
    label: (d: number) => `en ${d}d`,
    className: "text-muted-foreground",
  },
};

/* ── DGI service area colors ──────────────────────────────── */

export const DGI_AREA_COLORS: Record<string, string> = {
  CG: "bg-blue-50 text-blue-700 border-blue-200",
  MP: "bg-green-50 text-green-700 border-green-200",
  TD: "bg-purple-50 text-purple-700 border-purple-200",
  KC: "bg-amber-50 text-amber-700 border-amber-200",
};

/* ── Risk status & probability colors ────────────────────── */

export const RISK_STATUS_COLORS: Record<string, string> = {
  IDENTIFICADO: "bg-slate-50 text-slate-700 border-slate-200",
  EN_EVALUACION: "bg-blue-50 text-blue-700 border-blue-200",
  EN_MITIGACION: "bg-amber-50 text-amber-700 border-amber-200",
  MITIGADO: "bg-green-50 text-green-700 border-green-200",
  ACEPTADO: "bg-cyan-50 text-cyan-700 border-cyan-200",
  CERRADO: "bg-gray-50 text-gray-500 border-gray-200",
};

export const RISK_PROBABILITY_COLORS: Record<string, string> = {
  MUY_BAJA: "bg-green-50 text-green-700 border-green-200",
  BAJA: "bg-emerald-50 text-emerald-700 border-emerald-200",
  MEDIA: "bg-amber-50 text-amber-700 border-amber-200",
  ALTA: "bg-orange-50 text-orange-700 border-orange-200",
  MUY_ALTA: "bg-red-50 text-red-700 border-red-200",
};

/* ── Escalation level & status colors ────────────────────── */

export const ESCALATION_LEVEL_COLORS: Record<string, string> = {
  NIVEL_1: "bg-blue-50 text-blue-700 border-blue-200",
  NIVEL_2: "bg-amber-50 text-amber-700 border-amber-200",
  NIVEL_3: "bg-orange-50 text-orange-700 border-orange-200",
  NIVEL_4: "bg-red-50 text-red-700 border-red-200",
};

export const ESCALATION_STATUS_COLORS: Record<string, string> = {
  ABIERTO: "bg-slate-50 text-slate-700 border-slate-200",
  EN_GESTION: "bg-blue-50 text-blue-700 border-blue-200",
  RESUELTO: "bg-green-50 text-green-700 border-green-200",
  CERRADO: "bg-gray-50 text-gray-500 border-gray-200",
};

/**
 * Resolve which temporal state applies for the given days + status.
 */
export function resolveTemporalState(
  daysRemaining: number,
  state: string
): keyof typeof TEMPORAL_STATES {
  if (state === "VERIFICADO" || state === "CANCELADO") return "terminal";
  if (state === "COMPLETADO") return "completed";
  if (daysRemaining <= -5) return "overdue_old";
  if (daysRemaining < 0) return "overdue_new";
  if (daysRemaining <= 1) return "urgent";
  if (daysRemaining <= 3) return "soon";
  return "normal";
}
