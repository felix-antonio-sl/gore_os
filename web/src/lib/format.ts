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
