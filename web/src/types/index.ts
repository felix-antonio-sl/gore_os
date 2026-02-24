export interface User {
  id: string;
  email: string;
  nombre: string;
  apellido_paterno: string;
  role_code: RoleCode;
  role_label: string;
  division_id: string | null;
  population: "operativa" | "dgi";
}

export type RoleCode =
  | "ADMIN_SISTEMA"
  | "ADMIN_REGIONAL"
  | "JEFE_DIVISION"
  | "ENCARGADO"
  | "JEFE_DGI"
  | "ESP_CONTROL_GESTION"
  | "ESP_PROCESOS"
  | "ESP_TD";

export const OPERATIONAL_ROLES: RoleCode[] = [
  "ADMIN_SISTEMA",
  "ADMIN_REGIONAL",
  "JEFE_DIVISION",
  "ENCARGADO",
];

export const DGI_ROLES: RoleCode[] = [
  "JEFE_DGI",
  "ESP_CONTROL_GESTION",
  "ESP_PROCESOS",
  "ESP_TD",
];

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CategoryRef {
  id: string;
  code: string;
  label: string;
  description?: string;
}

export interface IPRListItem {
  id: string;
  codigo_bip: string;
  name: string;
  ipr_type: string | null;
  status: string | null;
  investment_sector: string | null;
  funding_source: string | null;
  alert_level: string | null;
  has_open_problems: boolean;
  executor_name: string | null;
  total_budget: number | null;
}

export interface CompromisoListItem {
  id: string;
  code: string | null;
  description: string;
  ipr_codigo_bip: string | null;
  ipr_name: string | null;
  commitment_type: string | null;
  responsible_name: string | null;
  responsible_id: string;
  division_name: string | null;
  due_date: string;
  state: string;
  state_label: string;
  days_remaining: number;
  completed_at: string | null;
  verified_at: string | null;
}

export interface ProblemaListItem {
  id: string;
  code: string | null;
  ipr_id: string;
  ipr_codigo_bip: string | null;
  ipr_name: string | null;
  problem_type: string;
  problem_type_label: string;
  impact: string | null;
  impact_label: string | null;
  description: string;
  state: string;
  state_label: string;
  days_open: number;
  detected_at: string;
}

export interface AlertaListItem {
  id: string;
  alert_type: string;
  alert_type_label: string;
  severity: string | null;
  severity_label: string | null;
  subject_type: string;
  subject_id: string;
  subject_label: string | null;
  message: string;
  triggered_at: string;
  acknowledged_at: string | null;
  attended_at: string | null;
  resolved_at: string | null;
}

export interface KPICardData {
  label: string;
  value: number;
  sublabel: string;
  color: "red" | "orange" | "amber" | "green" | "blue" | "gray";
}

export interface DashboardData {
  kpis: KPICardData[];
  commitments: CompromisoListItem[];
  alerts: AlertaListItem[];
  problems: ProblemaListItem[];
}

export interface HistoryEntry {
  id: string;
  previous_state: string | null;
  new_state: string;
  changed_by_name: string | null;
  comment: string | null;
  changed_at: string;
}

// ---------------------------------------------------------------------------
// DGI Types
// ---------------------------------------------------------------------------
export interface DGIIndicator {
  id: string;
  code: string;
  name: string;
  dimension: string;
  current_value: number | null;
  target_value: number | null;
  unit: string;
  signal: "VERDE" | "AMARILLO" | "ROJO" | null;
  trend: "up" | "down" | "flat" | null;
  description: string | null;
  last_updated_at: string | null;
}

export interface DGIDimensionSummary {
  dimension: string;
  label: string;
  signal: "VERDE" | "AMARILLO" | "ROJO";
  indicator_count: number;
}

export interface DGIInitiative {
  id: string;
  code: string | null;
  name: string;
  description: string | null;
  responsible_name: string | null;
  status: string;
  dmaic_phase: string | null;
  division_name: string | null;
  start_date: string | null;
  target_date: string | null;
  current_day: number;
  total_days: number | null;
  progress: number;
  wip_column: string | null;
}

export interface DGIReport {
  id: string;
  code: string | null;
  report_type: string;
  status: string;
  title: string;
  period_start: string | null;
  period_end: string | null;
  recipient: string | null;
  generated_by_name: string | null;
  sent_at: string | null;
  created_at: string;
}

export interface DGIBPMNModel {
  id: string;
  code: string | null;
  process_name: string;
  version: string;
  status: string;
  description: string | null;
}

export interface DGIDataSource {
  id: string;
  division_name: string | null;
  source_name: string;
  status: "OK" | "ATRASADO" | "SIN_DATOS";
  last_data_at: string | null;
  days_behind: number;
}

export interface DGICommitteeSession {
  id: string;
  session_date: string;
  status: string;
  agenda: { item: string }[];
  agreements: { item: string }[];
  notes: string | null;
}

export interface CockpitJefeDGI {
  semaforo: DGIDimensionSummary[];
  decisions_pending: number;
  team_status: { role: string; name: string; activity: string }[];
  critical_alerts: { id: string; message: string; severity: string }[];
  report_status: { title: string; status: string; due: string } | null;
}

export interface CockpitControlGestion {
  data_sources: DGIDataSource[];
  indicators_alert: DGIIndicator[];
  trends: DGIIndicator[];
  work_queue: { priority: string; task: string; status: string; deadline: string }[];
}

export interface CockpitProcesos {
  initiatives: DGIInitiative[];
  bpmn_models: DGIBPMNModel[];
  today_agenda: { time: string; activity: string; process: string }[];
  portfolio_stats: { active: number; completed: number; target: number };
}

export interface CockpitTD {
  compliance_bars: DGIIndicator[];
  velocity: { current: number; required: number; months_remaining: number };
  decrees: { code: string; name: string; status: string }[];
  kb_stats: { pending_publication: number; recently_updated: number; total: number };
  committee: DGICommitteeSession | null;
  normative_alerts: { message: string; days_until: number }[];
}
