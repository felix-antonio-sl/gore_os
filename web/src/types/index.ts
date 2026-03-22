export interface SearchResult {
  id: string;
  code: string | null;
  name: string;
  entity_type: string;
}

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
  | "GOBERNADOR"
  | "CONSEJERO_REGIONAL"
  | "SECRETARIO_EJECUTIVO"
  | "JEFE_DEPARTAMENTO"
  | "JEFE_UNIDAD"
  | "ANALISTA"
  | "RTF"
  | "ASESOR_JURIDICO"
  | "JEFE_DGI"
  | "ESP_CONTROL_GESTION"
  | "ESP_PROCESOS"
  | "ESP_TD";

export const OPERATIONAL_ROLES: RoleCode[] = [
  "ADMIN_SISTEMA",
  "ADMIN_REGIONAL",
  "JEFE_DIVISION",

  "GOBERNADOR",
  "CONSEJERO_REGIONAL",
  "SECRETARIO_EJECUTIVO",
  "JEFE_DEPARTAMENTO",
  "JEFE_UNIDAD",
  "ANALISTA",
  "RTF",
  "ASESOR_JURIDICO",
];

export const WRITE_OPERATIONAL_ROLES: RoleCode[] = [
  "ADMIN_SISTEMA",
  "ADMIN_REGIONAL",
  "JEFE_DIVISION",

  "GOBERNADOR",
  "SECRETARIO_EJECUTIVO",
  "JEFE_DEPARTAMENTO",
  "ANALISTA",
  "RTF",
  "ASESOR_JURIDICO",
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

export interface CurrentActor {
  role: string | null;
  role_label: string;
  action: string;
}

export interface IPRListItem {
  id: string;
  codigo_bip: string;
  name: string;
  ipr_type: string | null;
  status: string | null;
  investment_sector: string | null;
  funding_source: string | null;
  mechanism: string | null;
  mcd_phase: string | null;
  alert_level: string | null;
  has_open_problems: boolean;
  executor_name: string | null;
  total_budget: number | null;
  actor_role: string | null;
  actor_action: string | null;
  phase_entered_at: string | null;
}

export interface CompromisoListItem {
  id: string;
  code: string | null;
  description: string;
  ipr_id: string | null;
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
// Presupuesto Types
// ---------------------------------------------------------------------------
export interface PresupuestoListItem {
  id: string;
  code: string;
  name: string;
  fiscal_year: number;
  division_id: string | null;
  division_name: string | null;
  subtitle_label: string | null;
  program_type_label: string | null;
  item_label: string | null;
  allocation_label: string | null;
  program_code_label: string | null;
  initial_amount: number;
  current_amount: number | null;
  committed_amount: number;
  accrued_amount: number;
  paid_amount: number;
  execution_pct: number;
}

export interface CarryoverItem {
  id: string;
  fiscal_year: number;
  amount: number;
}

export interface BudgetCommitmentItem {
  id: string;
  commitment_number: string;
  amount: number;
  issued_at: string;
  expires_at: string | null;
  status_label: string | null;
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
}

export interface PresupuestoDetail extends PresupuestoListItem {
  subtitle_id: string | null;
  item_id: string | null;
  allocation_id: string | null;
  item_label: string | null;
  allocation_label: string | null;
  fndr_amount: number | null;
  sectorial_amount: number | null;
  created_at: string;
  carryovers: CarryoverItem[];
  budget_commitments: BudgetCommitmentItem[];
}

export interface PresupuestoResumen {
  group_key: string;
  group_label: string;
  initial_amount: number;
  current_amount: number;
  paid_amount: number;
  execution_pct: number;
  program_count: number;
}

// ---------------------------------------------------------------------------
// Convenios Types
// ---------------------------------------------------------------------------
export interface InstallmentItem {
  id: string;
  installment_number: number;
  amount: number;
  due_date: string;
  payment_status: string;
  payment_status_label: string;
  paid_at: string | null;
  paid_amount: number | null;
  payment_reference: string | null;
}

export interface ConvenioListItem {
  id: string;
  agreement_number: string | null;
  agreement_type: string;
  agreement_type_label: string;
  state: string;
  state_label: string;
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
  ipr_name: string | null;
  giver_name: string | null;
  receiver_name: string | null;
  total_amount: number | null;
  signed_at: string | null;
  valid_from: string | null;
  valid_to: string | null;
  days_to_expiry: number | null;
  installment_count: number;
  paid_installments: number;
}

export interface RenditionSummaryItem {
  id: string;
  short_id: string;
  amount: number | null;
  state: string;
  state_label: string;
  phase_entered_at: string | null;
  created_at: string;
}

export interface ConvenioDetail extends ConvenioListItem {
  technical_referent_name: string | null;
  cgr_outcome: string | null;
  cgr_outcome_label: string | null;
  created_at: string;
  installments: InstallmentItem[];
  history?: { id: string; previous_state: string | null; new_state: string; changed_by_name: string | null; comment: string | null; changed_at: string }[];
  pending_renditions?: number;
  blocked_renditions?: number;
  renditions?: RenditionSummaryItem[];
}

export interface ConvenioResumen {
  total: number;
  by_state: { code: string; label: string; count: number }[];
  expiring_30d: number;
  expiring_90d: number;
  total_amount: number | null;
  with_cgr: number;
  without_ipr: number;
}

export interface DataQualityMetrics {
  persons: { total: number; with_email: number; pct_email: number; with_rut: number; pct_rut: number; with_phone: number; pct_phone: number };
  iprs: { total: number; with_executor: number; pct_executor: number; with_mechanism: number; pct_mechanism: number; with_nature: number; pct_nature: number; with_parties: number; pct_parties: number; with_territory: number; pct_territory: number };
  agreements: { total: number; with_cgr: number; pct_cgr: number; with_ipr: number; pct_ipr: number; with_referent: number; pct_referent: number };
  documents: { total: number; with_type: number; pct_type: number; with_url: number; pct_url: number };
  organizations: { total: number; with_type: number; pct_type: number; with_parent: number; pct_parent: number };
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
  formula: string | null;
  frequency: string | null;
  source_type: "AUTO" | "MANUAL" | "EXTERNAL" | null;
  lifecycle_status: "BORRADOR" | "APROBADO" | "VIGENTE" | "DEPRECADO" | null;
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
  responsible_id: string | null;
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
  sort_order: number;
  started_at: string | null;
  completed_at: string | null;
  days_in_column: number | null;
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

export interface RenditionStateSummary {
  code: string;
  label: string;
  count: number;
}

export interface RenditionSummary {
  total: number;
  by_state: RenditionStateSummary[];
  amount_at_risk: number | null;
}

export interface DecisionItem {
  source: string;
  id: string;
  title: string;
  severity: string;
}

export interface CockpitJefeDGI {
  semaforo: DGIDimensionSummary[];
  decisions_pending: number;
  decision_items: DecisionItem[];
  team_status: { role: string; name: string; activity: string }[];
  critical_alerts: { id: string; message: string; severity: string }[];
  report_status: { title: string; status: string; due: string } | null;
  rendition_summary: RenditionSummary | null;
}

export interface CockpitControlGestion {
  data_sources: DGIDataSource[];
  indicators_alert: DGIIndicator[];
  trends: DGIIndicator[];
  work_queue: { priority: string; task: string; status: string; deadline: string }[];
}

export interface AgendaItem {
  time: string;
  activity: string;
  process: string;
}

export interface PortfolioStats {
  active: number;
  completed: number;
  target: number;
}

export interface CockpitProcesos {
  initiatives: DGIInitiative[];
  bpmn_models: DGIBPMNModel[];
  today_agenda: AgendaItem[];
  portfolio_stats: PortfolioStats;
}

export interface DecreeItem {
  id: string;
  code: string;
  name: string;
  description: string | null;
  status: string;
  deadline: string | null;
  days_until: number | null;
}

export interface NormativeAlertItem {
  message: string;
  days_until: number;
  decree_code: string | null;
}

export interface VelocityStats {
  current: number;
  required: number;
  months_remaining: number;
}

export interface KBStats {
  module_status: string;
  message: string;
}

export interface CockpitTD {
  compliance_bars: DGIIndicator[];
  velocity: VelocityStats;
  decrees: DecreeItem[];
  kb_stats: KBStats;
  committee: DGICommitteeSession | null;
  normative_alerts: NormativeAlertItem[];
}

// ---------------------------------------------------------------------------
// IPR Children Types (Partes, Territorio, Hitos)
// ---------------------------------------------------------------------------
export interface IprPartyItem {
  id: string;
  organization_name: string;
  organization_code: string | null;
  role_code: string;
  role_label: string;
  is_primary: boolean;
  valid_from: string | null;
  valid_to: string | null;
  contact_person: string | null;
  contact_email: string | null;
  responsibility_description: string | null;
  agreement_number: string | null;
}

export interface IprTerritoryItem {
  id: string;
  territory_name: string;
  territory_code: string | null;
  impact_type_code: string;
  impact_type_label: string;
  is_primary: boolean;
  notes: string | null;
}

export interface IprMilestoneItem {
  id: string;
  milestone_type_code: string;
  milestone_type_label: string;
  description: string | null;
  planned_date: string;
  actual_date: string | null;
  deviation_days: number | null;
  completed_by_name: string | null;
  verification_notes: string | null;
  created_at: string;
}

export interface TerritoryOption {
  id: string;
  code: string;
  name: string;
  territory_type: string;
}

export interface OrganizationOption {
  id: string;
  code: string;
  name: string;
  short_name: string;
  org_type: string;
  rut: string | null;
}

// ---------------------------------------------------------------------------
// Reuniones de Crisis Types
// ---------------------------------------------------------------------------
export interface ReunionListItem {
  id: string;
  session_id: string;
  session_number: number;
  scheduled_at: string;
  started_at: string | null;
  finished_at: string | null;
  summary: string | null;
  organizer_name: string | null;
  status: "PROGRAMADA" | "EN_CURSO" | "FINALIZADA";
  topic_count: number;
}

export interface TopicItem {
  id: string;
  agreement_number: number;
  subject: string;
  decision: string | null;
  responsible_name: string | null;
  due_date: string | null;
  status: string | null;
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
  context_type: string | null;
}

export interface ReunionDetail extends ReunionListItem {
  location: string | null;
  topics: TopicItem[];
}

export interface AutoSuggestion {
  type: "alerta_critica" | "compromiso_vencido" | "problema_abierto";
  subject: string;
  detail: string;
  target_id: string;
  ipr_codigo_bip: string | null;
}

// ---------------------------------------------------------------------------
// IPR Lifecycle / Transitions
// ---------------------------------------------------------------------------
export interface GateStatus {
  name: string;
  met: boolean;
  detail: string;
}

export interface IprTransition {
  id: string;
  code: string;
  label: string;
  target_phase: string | null;
  phase_change: boolean;
  gates: GateStatus[];
  blocked: boolean;
  allowed: boolean;
  effects?: string[];
}

// Roles with IPR transition authority (matches backend _ASSIGN_ROLES)
export const TRANSITION_ROLES: RoleCode[] = [
  "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION",
  "GOBERNADOR", "JEFE_DEPARTAMENTO", "ANALISTA",
];

// ---------------------------------------------------------------------------
// Actos Administrativos Types
// ---------------------------------------------------------------------------
export interface ActoListItem {
  id: string;
  act_number: string;
  act_type: string;
  act_type_label: string;
  subject: string;
  state: string;
  state_label: string;
  issuer_name: string | null;
  signer_name: string | null;
  issued_at: string;
  requires_cgr: boolean;
  cgr_outcome: string | null;
  cgr_outcome_label: string | null;
  resolution_type: string | null;
  resolution_type_label: string | null;
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
  agreement_id: string | null;
  agreement_number: string | null;
  budget_amount: number | null;
}

export interface ActoDetail extends ActoListItem {
  effective_from: string | null;
  effective_to: string | null;
  cgr_submitted_at: string | null;
  cgr_resolved_at: string | null;
  resolution_subtype: string | null;
  resolution_subtype_label: string | null;
  created_at: string;
  history: HistoryEntry[];
}

export interface ActoTransition {
  id: string;
  code: string;
  label: string;
}

// ---------------------------------------------------------------------------
// CORE Sessions (Consejo Regional)
// ---------------------------------------------------------------------------
export interface CoreSessionListItem {
  id: string;
  session_number: number;
  session_type: string;
  scheduled_at: string;
  started_at: string | null;
  ended_at: string | null;
  summary: string | null;
  status: "PROGRAMADA" | "EN_CURSO" | "FINALIZADA";
  topic_count: number;
  quorum_reached: boolean | null;
}

export interface TopicWithVotes {
  id: string;
  agreement_number: number;
  subject: string;
  decision: string | null;
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
  quorum_type: string;
  votes_favor: number;
  votes_contra: number;
  votes_abstencion: number;
  votes_total: number;
  required_votes: number;
  result: "APROBADO" | "RECHAZADO" | "PENDIENTE";
}

export interface MemberAttendance {
  member_id: string;
  person_name: string;
  role_in_committee: string | null;
  has_voted_in_session: boolean;
}

export interface CoreSessionDetail extends CoreSessionListItem {
  location: string | null;
  minute_id: string | null;
  topics: TopicWithVotes[];
  members_present: number;
  members_total: number;
}

// ---------------------------------------------------------------------------
// Poly-Switch (Track Info + Evaluation Assignment)
// ---------------------------------------------------------------------------
export interface TrackInfo {
  mechanism: string | null;
  mechanism_label: string | null;
  evaluator: string | null;
  evaluator_label: string | null;
  favorable_products: string[];
  unfavorable_products: string[];
  terminal_negative: string[];
  thresholds: Record<string, number>;
  sla_days: Record<string, number>;
  required_attrs: string[];
  mechanism_attrs: Record<string, string | number | boolean | null>;
  evaluations: EvaluationAssignment[];
}

// ---------------------------------------------------------------------------
// DGI Cartera IPR Types
// ---------------------------------------------------------------------------
export type HealthSignal = "VERDE" | "AMARILLO" | "ROJO";

export interface CarteraIPRItem {
  id: string;
  codigo_bip: string;
  name: string;
  mechanism: string | null;
  mcd_phase: string | null;
  division_name: string | null;
  division_id: string | null;
  monto_total: number | null;
  health_signal: HealthSignal;
  health_reasons: string[];
  days_since_update: number;
  physical_progress: number | null;
  financial_progress: number | null;
  cdp_total: number;
  cdp_paid: number;
  budget_execution_pct: number | null;
  agreement_count: number;
  agreement_latest_state: string | null;
  overdue_installments: number;
  resolution_count: number;
  pending_cgr: number;
  open_problems: number;
  active_alerts: number;
  critical_alerts: number;
  overdue_commitments: number;
}

export interface CarteraSummary {
  total: number;
  verde: number;
  amarillo: number;
  rojo: number;
  overdue_installments_total: number;
  pending_cgr_total: number;
  monto_total: number;
  total_paid: number;
}

export interface CuotaVencidaItem {
  id: string;
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
  agreement_id: string;
  agreement_number: string | null;
  counterpart_name: string | null;
  installment_number: number;
  amount: number;
  due_date: string;
  days_overdue: number;
}

export interface EvaluationAssignment {
  id: string;
  ipr_id?: string;
  evaluator_type: string;
  evaluator_type_label: string | null;
  evaluator_org_name: string | null;
  evaluator_name: string | null;
  assigned_at: string;
  deadline_at: string | null;
  completed_at: string | null;
  result_code: string | null;
  result_label: string | null;
  observations: string | null;
  numeric_score: number | null;
  rank_position: number | null;
  rank_total: number | null;
  convocatoria_code: string | null;
}

export interface KinshipDeclaration {
  id: string;
  ipr_id: string;
  person_id: string;
  person_name: string;
  person_rut: string | null;
  declaration_type: string;
  declares_no_conflict: boolean;
  related_authority_id: string | null;
  related_authority_name: string | null;
  relationship_type: string | null;
  relationship_degree: number | null;
  declared_at: string;
  validated_by_id: string | null;
  validated_at: string | null;
}

export interface PersonRef {
  id: string;
  rut: string | null;
  names: string;
  paternal_surname: string;
  maternal_surname: string | null;
  organization_name: string | null;
}

// ---------------------------------------------------------------------------
// Process Catalog Types (DGI Wave A)
// ---------------------------------------------------------------------------
export interface ProcessListItem {
  id: string;
  code: string | null;
  name: string;
  description: string | null;
  scope: string | null;
  division_id: string | null;
  division_name: string | null;
  owner_id: string | null;
  owner_name: string | null;
  status: string;
  criticality: string;
  bpmn_count: number;
}

export interface ProcessDetail extends ProcessListItem {
  created_at: string;
  updated_at: string;
  bpmn_models: Array<{
    id: string;
    code: string | null;
    process_name: string;
    version: string;
    status: string;
    description: string | null;
  }>;
}

export interface ProcessActor {
  id: string;
  actor_type: string;
  actor_name: string;
  lane_label: string | null;
  description: string | null;
  created_at: string;
}

export interface ProcessRule {
  id: string;
  code: string;
  description: string;
  rule_type: string;
  created_at: string;
}

export interface ProcessMetric {
  id: string;
  name: string;
  value: number | null;
  unit: string | null;
  measured_at: string;
  measurement_type: string;
  source: string | null;
  created_at: string;
}

export interface ProcessPainPoint {
  id: string;
  description: string;
  impact: string;
  bpmn_stage: string | null;
  reported_by_name: string | null;
  created_at: string;
}

export interface ImprovementOpportunity {
  id: string;
  dimension: string;
  description: string;
  impact: string | null;
  effort: string | null;
  status: string;
  initiative_id: string | null;
  initiative_code: string | null;
  created_at: string;
}

export interface ProcessProgressItem {
  division_name: string;
  total: number;
  identificado: number;
  en_levantamiento: number;
  modelado: number;
  validado: number;
  publicado: number;
  suspendido: number;
}

// ---------------------------------------------------------------------------
// Bottleneck Detection Types (DGI Wave A)
// ---------------------------------------------------------------------------
export interface BottleneckFinding {
  finding_type: "ACUMULACION" | "CICLO_TIEMPO" | "PRESUPUESTO";
  division_id: string | null;
  division_name: string | null;
  description: string;
  detection_value: number;
  detection_threshold: number;
  severity: "ALTO" | "MEDIO";
  pending_commitments?: number;
  open_problems?: number;
  current_avg_days?: number;
  historical_avg_days?: number;
  delta_pct?: number;
  execution_pct?: number;
  program_name?: string;
}

export interface BottleneckInvestigation {
  id: string;
  code: string | null;
  status: string;
  status_label: string | null;
  division_id: string | null;
  division_name: string | null;
  detection_type: string;
  detection_value: number | null;
  detection_threshold: number | null;
  problem: string | null;
  detected_at: string;
  closed_at: string | null;
  created_by_name: string | null;
  updated_at: string;
}

export interface BottleneckDetail extends BottleneckInvestigation {
  indicator_id: string | null;
  process_id: string | null;
  verification: string | null;
  root_cause_analysis: string | null;
  proposal: string | null;
  communication: string | null;
  follow_up: string | null;
}

export interface BottleneckSummary {
  total_active: number;
  by_status: { code: string; label: string; count: number }[];
  by_division: { division_name: string; count: number }[];
  critical_count: number;
}

// ---------------------------------------------------------------------------
// DMAIC Types (Wave C)
// ---------------------------------------------------------------------------
export interface DMAICGateResult {
  phase: string;
  met: boolean;
  detail: string;
}

export interface DMAICDetail {
  initiative_id: string;
  current_phase: string | null;
  phases: Record<string, Record<string, string>>;
  gates: DMAICGateResult[];
}

export interface LeanMetrics {
  throughput_30d: number;
  throughput_60d: number;
  throughput_90d: number;
  lead_time_avg: number | null;
  cycle_time_avg: number | null;
  wip_count: number;
  aging: { id: string; name: string; days: number; column: string }[];
}

export interface MetricComparison {
  name: string;
  baseline_value: number | null;
  post_mejora_value: number | null;
  unit: string | null;
  delta: number | null;
  improved: boolean;
}

export interface ImpactEffortCell {
  impact: string;
  effort: string;
  count: number;
  opportunities: { id: string; description: string }[];
}

// ---------------------------------------------------------------------------
// Wave B: Coordinación Institucional
// ---------------------------------------------------------------------------
export interface ARDecision {
  id: string;
  description: string;
  decision_type: string;
  decision_type_label: string;
  status: string;
  status_label: string;
  due_date: string | null;
  context: string | null;
  responsible_name: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface Escalation {
  id: string;
  code: string;
  level: string;
  level_label: string;
  status: string;
  status_label: string;
  situation: string;
  impact: string;
  options: { option: string; pros: string; cons: string }[];
  recommendation: string | null;
  deadline: string | null;
  subject_type: string | null;
  subject_id: string | null;
  escalated_to: string | null;
  resolved_description: string | null;
  resolved_at: string | null;
  alert_id: string | null;
  created_at: string;
  created_by_name: string | null;
}

export interface EscalationStats {
  total_active: number;
  by_level: { level: string; label: string; count: number }[];
  avg_resolution_hours: number | null;
  resolved_count: number;
}

export interface DGIService {
  id: string;
  code: string;
  name: string;
  description: string | null;
  area: string;
  status: string;
  status_label: string;
  sla_days: number | null;
  how_to_request: string | null;
  deliverables: string | null;
}

export interface ServiceRequest {
  id: string;
  code: string;
  service_id: string;
  service_name: string;
  status: string;
  status_label: string;
  requester_name: string;
  division_name: string | null;
  description: string;
  urgency: string;
  assigned_to_name: string | null;
  started_at: string | null;
  completed_at: string | null;
  satisfaction_score: number | null;
  days_elapsed: number | null;
  sla_days: number | null;
  is_overdue: boolean;
  created_at: string;
}

export interface SLADefinition {
  id: string;
  service_id: string;
  product_type: string;
  product_type_label: string;
  description: string | null;
  target_days: number;
  target_hour: string | null;
  priority: number;
}

export interface SLADashboardItem {
  service_id: string;
  service_name: string;
  area: string;
  total_requests: number;
  completed: number;
  completion_rate: number;
  avg_days: number | null;
  breaches: number;
}

export interface SLADashboardSummary {
  global_completion_rate: number;
  active_requests: number;
  avg_resolution_days: number | null;
  avg_satisfaction: number | null;
  by_service: SLADashboardItem[];
}

export interface DivisionInteraction {
  id: string;
  division_id: string;
  division_name: string;
  interaction_type: string;
  interaction_type_label: string;
  interaction_date: string;
  participants: { name: string; role: string }[];
  topics: string[];
  agreements: { description: string; responsible: string; due_date: string; status: string }[];
  next_date: string | null;
  notes: string | null;
  created_at: string;
}

export interface InteractionMatrixRow {
  division_id: string;
  division_name: string;
  last_interaction: string | null;
  next_planned: string | null;
  interaction_count: number;
  pending_agreements: number;
  dominant_type: string | null;
}

// ---------------------------------------------------------------------------
// TD Committee Sessions (Wave D — CI-016)
// ---------------------------------------------------------------------------
export interface TDSessionListItem {
  id: string;
  session_number: number;
  scheduled_at: string;
  started_at: string | null;
  ended_at: string | null;
  description: string | null;
  status: "PROGRAMADA" | "EN_CURSO" | "FINALIZADA";
  topic_count: number;
  pending_agreements: number;
}

export interface TDTopicItem {
  id: string;
  topic_number: number;
  subject: string;
  agreement: string | null;
  created_at: string;
}

export interface TDSessionDetail extends TDSessionListItem {
  location: string | null;
  topics: TDTopicItem[];
}

// ---------------------------------------------------------------------------
// Consolidated Calendar (Wave D — CI-019)
// ---------------------------------------------------------------------------
export interface CalendarEvent {
  event_date: string;
  event_type: "SESSION" | "INTERACTION" | "DECISION" | "ESCALATION" | "SLA";
  title: string;
  description: string | null;
  entity_id: string | null;
  severity: "rojo" | "amber" | "verde" | null;
}

// ---------------------------------------------------------------------------
// Risk Management (Wave E)
// ---------------------------------------------------------------------------
export interface RiskListItem {
  id: string;
  code: string;
  name: string;
  risk_type: string | null;
  risk_type_label: string | null;
  probability: string | null;
  probability_label: string | null;
  impact: string | null;
  impact_label: string | null;
  status: string | null;
  status_label: string | null;
  subject_type: string;
  subject_id: string;
  subject_label: string | null;
  identified_at: string | null;
  created_at: string;
}

export interface RiskDetail extends RiskListItem {
  mitigation_plan: string | null;
  metadata: Record<string, unknown> | null;
  created_by_name: string | null;
  updated_at: string;
}

export interface RiskSummary {
  total: number;
  by_status: { code: string; label: string; count: number }[];
  by_type: { code: string; label: string; count: number }[];
  by_probability: { code: string; label: string; count: number }[];
  high_risk_count: number;
}

export interface RiskMatrixCell {
  probability: string;
  probability_label: string;
  impact: string;
  impact_label: string;
  count: number;
}

// ---------------------------------------------------------------------------
// Command Center (Wave E)
// ---------------------------------------------------------------------------
export interface CommandCenterSummary {
  escalations: {
    active: number;
    by_level: { level: string; label: string; count: number }[];
    top: { id: string; code: string; situation: string; deadline: string | null; level: string; level_label: string }[];
  };
  alerts: {
    critical: number;
    high: number;
    top: { id: string; message: string; severity: string; severity_label: string; triggered_at: string }[];
  };
  risks: {
    high_count: number;
    total_active: number;
    top: { id: string; code: string; name: string; probability: string; status: string }[];
  };
  decisions: {
    pending: number;
    top: { id: string; description: string; due_date: string | null; decision_type: string; status: string }[];
  };
  meetings: {
    upcoming: number;
    next: { id: string; scheduled_at: string; summary: string | null; organizer_name: string | null }[];
  };
  sla_breaches: {
    count: number;
  };
}

export interface TimelineEvent {
  category: "ESCALATION" | "ALERT" | "RISK" | "DECISION" | "MEETING";
  ref_code: string;
  description: string;
  event_time: string;
  detail: string | null;
  entity_id: string | null;
}

// --- Dashboard Response Types (existing endpoints) ---

export interface TeamMemberLoad {
  user_id: string;
  name: string;
  pendientes: number;
  en_progreso: number;
  completados: number;
  vencidos: number;
  total: number;
}

export interface MiDivisionResponse {
  kpis: KPICardData[];
  team: TeamMemberLoad[];
  commitments: CompromisoListItem[];
}

export interface MisCompromisosResponse {
  kpis: KPICardData[];
  groups: Array<{ label: string; count: number; items: CompromisoListItem[] }>;
}

export interface DivisionBreakdown {
  division_name: string;
  vencidos: number;
  total_compromisos: number;
  problemas_abiertos: number;
  ejecucion_pct: number;
}

export interface SemaforoItem {
  dimension: string;
  label: string;
  signal: string;
  indicator_count: number;
}

export interface DashboardExecutivoResponse extends DashboardData {
  divisions: DivisionBreakdown[];
  semaforo: SemaforoItem[];
}

// --- Action Items (Centro de Comando Personal) ---

export interface ActionItem {
  id: string;
  category: "COMPROMISO" | "ALERTA" | "DECISION" | "ESCALAMIENTO" | "SLA" | "RIESGO" | "FIRMA" | "RENDICION" | "IPR";
  title: string;
  subtitle: string | null;
  deadline: string | null;
  days_remaining: number | null;
  temporal: "VENCIDO" | "HOY" | "ESTA_SEMANA" | "FUTURO" | null;
  severity: "CRITICO" | "ALTO" | "MEDIO" | "BAJO";
  priority: number;
  action_label: string;
  action_route: string;
  ipr_id?: string | null;
  ipr_codigo_bip?: string | null;
}

// ---------------------------------------------------------------------------
// ANALISTA Formulation Pipeline
// ---------------------------------------------------------------------------
export interface FormulacionIPR {
  id: string;
  codigo_bip: string;
  name: string;
  phase: string;
  days_in_phase: number;
  has_mechanism: boolean;
  partes_count: number;
  territorio_count: number;
  hitos_count: number;
  evaluaciones_count: number;
  admisibilidad_total: number;
  admisibilidad_verified: number;
  eval_assigned: boolean;
  eval_result: string | null;
  suggested_action: string;
  suggested_tab: string;
}

export interface MisFormulacionesResponse {
  total: number;
  by_phase: Record<string, FormulacionIPR[]>;
}

export interface ActionItemsResponse {
  greeting_name: string;
  today: string;
  summary: string;
  items: ActionItem[];
  counts: Record<string, number>;
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------
export interface NotificationItem {
  id: string;
  title: string;
  body: string | null;
  category: "alerta" | "sla" | "escalamiento" | "compromiso" | "rendicion" | "firma" | "sistema";
  entity_type: string | null;
  entity_id: string | null;
  link: string | null;
  read_at: string | null;
  created_at: string;
}

export interface NotificationUnreadCount {
  count: number;
}

// ---------------------------------------------------------------------------
// IPR Readiness (H3)
// ---------------------------------------------------------------------------
export interface SatelliteStatus {
  name: string;
  label: string;
  count: number;
  detail?: Record<string, unknown>;
}

export interface TransitionReadiness {
  code: string;
  label: string;
  target_phase?: string;
  gates_met: number;
  gates_total: number;
  blocking_gates: string[];
}

export interface IprReadiness {
  satellites: SatelliteStatus[];
  next_transitions: TransitionReadiness[];
}

// ---------------------------------------------------------------------------
// IPR Cartera por Division (H14)
// ---------------------------------------------------------------------------
export interface DivisionCarteraItem {
  division_id: string;
  division_name: string;
  abbreviation: string | null;
  total_iprs: number;
  by_phase: Record<string, number>;
  critical_alerts: number;
  open_problems: number;
  overdue_commitments: number;
  health_signal: "VERDE" | "AMARILLO" | "ROJO";
  health_reasons: string[];
}
