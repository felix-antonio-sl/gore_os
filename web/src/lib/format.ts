/**
 * Shared formatting utilities for GORE_OS.
 * All formatters use "es-CL" locale for Chilean Spanish.
 */

const LOCALE = "es-CL";

/** Short date: "27 feb. 2026" */
export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    return new Intl.DateTimeFormat(LOCALE, {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

/** Date + time: "27 feb. 2026, 14:30" */
export function formatDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    return new Intl.DateTimeFormat(LOCALE, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

/** Short date+time without year: "27 feb., 14:30" (for alert cards, timelines) */
export function formatDateTimeShort(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    return new Intl.DateTimeFormat(LOCALE, {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

/** Long formal date: "jueves, 27 de febrero de 2026, 14:30" (for reuniones detail) */
export function formatDateLong(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    return new Intl.DateTimeFormat(LOCALE, {
      weekday: "long",
      day: "2-digit",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

/** Compact CLP currency: "$1,2 MM" */
export function formatCLP(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat(LOCALE, {
    style: "currency",
    currency: "CLP",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

/** Alias for formatCLP */
export const formatCurrency = formatCLP;

/**
 * Exact CLP currency, no compact notation: "$67.294".
 * Use for parameters, thresholds, UTM values and any figure where the exact
 * amount matters — never the compact `formatCLP` (which rounds to "$67,3 mil").
 */
export function formatCLPExact(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat(LOCALE, {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(value);
}

/** Alias: a UTM-denominated peso amount is always shown exact. */
export const formatUTM = formatCLPExact;

/**
 * Human-framed large amounts: ">= 1.000 millones" → "$5.000 millones",
 * smaller amounts fall back to exact pesos ("$67.294"). Avoids "$5000 M".
 */
export function formatMillones(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  if (Math.abs(value) < 1_000_000_000) return formatCLPExact(value);
  const millones = value / 1_000_000;
  const formatted = new Intl.NumberFormat(LOCALE, {
    maximumFractionDigits: millones % 1 === 0 ? 0 : 1,
  }).format(millones);
  return `$${formatted} millones`;
}

/** Relative time: "hace 2h", "hace 3d", "hace 1 min" */
export function formatRelativeTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    const now = Date.now();
    const then = new Date(dateStr).getTime();
    const diffMs = now - then;
    if (diffMs < 0) return "ahora";

    const minutes = Math.floor(diffMs / 60_000);
    if (minutes < 1) return "ahora";
    if (minutes < 60) return `hace ${minutes} min`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `hace ${hours}h`;

    const days = Math.floor(hours / 24);
    if (days < 30) return `hace ${days}d`;

    const months = Math.floor(days / 30);
    if (months < 12) return `hace ${months} mes${months > 1 ? "es" : ""}`;

    const years = Math.floor(days / 365);
    return `hace ${years} a${years > 1 ? "nos" : "no"}`;
  } catch {
    return dateStr;
  }
}
