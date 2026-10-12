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
  phase_entered_at?: string;
  alert_level?: string;
  executor_name?: string;
  formulator_name?: string;
  total_budget?: number;
  start_date?: string;
  end_date?: string;
  ipr_type_label?: string | null;
  status_label?: string | null;
  assignee_name?: string | null;
  sponsor_division_name?: string | null;
  intended_outcome?: string | null;
  commitment_count: number;
  problem_count: number;
  alert_count: number;
  agreement_count: number;
}

export const alertBorderMap: Record<string, string> = {
  CRITICO: "border-l-red-600",
  ALTO: "border-l-orange-500",
  ATENCION: "border-l-amber-400",
  INFO: "border-l-blue-500",
};

export const mechanismColors: Record<string, string> = {
  SNI: "bg-indigo-100 text-indigo-800 border-indigo-200 dark:bg-indigo-950 dark:text-indigo-300 dark:border-indigo-800",
  C33: "bg-violet-100 text-violet-800 border-violet-200 dark:bg-violet-950 dark:text-violet-300 dark:border-violet-800",
  FRIL: "bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800",
  GLOSA06: "bg-sky-100 text-sky-800 border-sky-200 dark:bg-sky-950 dark:text-sky-300 dark:border-sky-800",
  TRANSFER: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800",
  SUBV8: "bg-rose-100 text-rose-800 border-rose-200 dark:bg-rose-950 dark:text-rose-300 dark:border-rose-800",
  FRPD: "bg-teal-100 text-teal-800 border-teal-200 dark:bg-teal-950 dark:text-teal-300 dark:border-teal-800",
};

export const mcdPhaseColors: Record<string, string> = {
  F0: "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-700",
  F1: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800",
  F2: "bg-cyan-100 text-cyan-700 border-cyan-200 dark:bg-cyan-950 dark:text-cyan-300 dark:border-cyan-800",
  F3: "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800",
  F4: "bg-green-100 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800",
  F5: "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-900 dark:text-gray-300 dark:border-gray-700",
};

export const MCD_PHASES = [
  { code: "F0", label: "Formulación" },
  { code: "F1", label: "Admisibilidad" },
  { code: "F2", label: "Evaluación" },
  { code: "F3", label: "Priorización" },
  { code: "F4", label: "Ejecución" },
  { code: "F5", label: "Cierre" },
];

export const SECTOR_OPTIONS = [
  { value: "SPORTS", label: "Deporte" },
  { value: "CULTURE", label: "Cultura y Patrimonio" },
  { value: "EDUCATION", label: "Educación" },
  { value: "HEALTH", label: "Salud" },
  { value: "INFRASTRUCTURE", label: "Infraestructura" },
  { value: "ENVIRONMENT", label: "Medio Ambiente" },
  { value: "TRANSPORT", label: "Transporte y Vialidad" },
  { value: "SECURITY", label: "Seguridad" },
  { value: "TOURISM", label: "Turismo" },
  { value: "SCIENCE", label: "Ciencia e Innovación" },
  { value: "ECONOMIC_DEV", label: "Desarrollo Económico" },
];

export const sectorLabel: Record<string, string> = Object.fromEntries(
  SECTOR_OPTIONS.map(o => [o.value, o.label])
);
