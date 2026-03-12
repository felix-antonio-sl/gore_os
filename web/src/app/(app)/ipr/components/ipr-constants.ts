/** Shared constants and types for IPR detail components */

export interface IprDetail {
  id: string;
  codigo_bip: string;
  name: string;
  description?: string;
  ipr_type?: string;
  status?: string;
  investment_sector?: string;
  funding_source?: string;
  fund_category?: string;
  fund_category_label?: string;
  mechanism?: string;
  mechanism_label?: string;
  mcd_phase?: string;
  mcd_phase_label?: string;
  alert_level?: string;
  executor_name?: string;
  formulator_name?: string;
  total_budget?: number;
  start_date?: string;
  end_date?: string;
}

export const alertBorderMap: Record<string, string> = {
  CRITICO: "border-l-red-600",
  ALTO: "border-l-orange-500",
  ATENCION: "border-l-amber-400",
  INFO: "border-l-blue-500",
};

export const mechanismColors: Record<string, string> = {
  SNI: "bg-indigo-100 text-indigo-800 border-indigo-200",
  C33: "bg-violet-100 text-violet-800 border-violet-200",
  FRIL: "bg-emerald-100 text-emerald-800 border-emerald-200",
  GLOSA06: "bg-sky-100 text-sky-800 border-sky-200",
  TRANSFER: "bg-amber-100 text-amber-800 border-amber-200",
  SUBV8: "bg-rose-100 text-rose-800 border-rose-200",
  FRPD: "bg-teal-100 text-teal-800 border-teal-200",
};

export const mcdPhaseColors: Record<string, string> = {
  F0: "bg-slate-100 text-slate-700 border-slate-200",
  F1: "bg-blue-100 text-blue-700 border-blue-200",
  F2: "bg-cyan-100 text-cyan-700 border-cyan-200",
  F3: "bg-amber-100 text-amber-700 border-amber-200",
  F4: "bg-green-100 text-green-700 border-green-200",
  F5: "bg-gray-100 text-gray-700 border-gray-200",
};

export const MCD_PHASES = [
  { code: "F0", label: "Formulación" },
  { code: "F1", label: "Admisibilidad" },
  { code: "F2", label: "Evaluación" },
  { code: "F3", label: "Priorización" },
  { code: "F4", label: "Ejecución" },
  { code: "F5", label: "Cierre" },
];
