# GORE_OS v3.0 - Entity-Relationship Diagrams

**Modelo**: GORE_OS v3.0 - Sistema de Gestión Institucional para Gobiernos Regionales
**Fecha**: 2026-01-27
**Total Entidades**: 50 tablas en 4 schemas

---

## Resumen de Schemas

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `meta` | 5 | Átomos fundamentales - Role, Process, Entity, Story |
| `ref` | 3 | Vocabularios controlados - Category Pattern (Gist 14.0) |
| `core` | 40 | Entidades de negocio - IPR, Agreements, Budget, Work Items |
| `txn` | 2 | Event Sourcing - Eventos y Magnitudes (particionadas) |

---

## 1. ERD Completo - Vista General

```mermaid
erDiagram
    %% ========================================
    %% SCHEMA: META (Átomos Fundamentales)
    %% ========================================

    meta_role ||--o{ meta_story : "defines capability"
    meta_role ||--o{ meta_role : "human_accountable"
    meta_process ||--o{ meta_story : "context"
    meta_entity ||--o{ meta_story_entity : "participates"
    meta_story ||--o{ meta_story_entity : "involves"
    meta_story ||--o{ core_work_item : "origin"

    meta_role {
        uuid id PK
        varchar code UK
        text name
        agent_type_enum agent_type
        cognition_level_enum cognition_level
        delegation_mode_enum delegation_mode
        uuid human_accountable_id FK
    }

    meta_process {
        uuid id PK
        varchar code UK
        text name
        process_layer_enum layer
    }

    meta_entity {
        uuid id PK
        varchar code UK
        text name
        varchar domain
    }

    meta_story {
        uuid id PK
        varchar code UK
        text as_a
        text i_want
        text so_that
        uuid role_id FK
        uuid process_id FK
        story_status_enum status
    }

    meta_story_entity {
        uuid id PK
        uuid story_id FK
        uuid entity_id FK
        story_status_enum status
    }

    %% ========================================
    %% SCHEMA: REF (Vocabularios Controlados)
    %% ========================================

    ref_category ||--o{ ref_category : "parent"
    ref_category ||--o{ core_ipr : "classifies"
    ref_category ||--o{ core_agreement : "types"
    ref_category ||--o{ core_work_item : "status"

    ref_category {
        uuid id PK
        varchar scheme
        varchar code
        text label
        uuid parent_id FK
        uuid phase_id FK
        jsonb valid_transitions
    }

    ref_actor ||--o{ txn_event : "performs"
    ref_actor {
        uuid id PK
        varchar code UK
        text name
        agent_type_enum agent_type
        text agent_definition_uri
    }

    ref_operational_commitment_type ||--o{ core_operational_commitment : "types"
    ref_operational_commitment_type {
        uuid id PK
        varchar code UK
        varchar name
        integer default_days
    }

    %% ========================================
    %% SCHEMA: CORE - Organización y Personas
    %% ========================================

    core_organization ||--o{ core_organization : "parent"
    core_organization ||--o{ core_person : "employs"
    core_organization ||--o{ core_ipr : "formulates"

    core_organization {
        uuid id PK
        varchar code UK
        text name
        uuid org_type_id FK
        uuid parent_id FK
    }

    core_person ||--|| core_user : "has account"
    core_person {
        uuid id PK
        varchar rut UK
        text names
        text paternal_surname
        uuid organization_id FK
    }

    core_user ||--o{ core_work_item : "assigned"
    core_user ||--o{ core_operational_commitment : "responsible"
    core_user {
        uuid id PK
        uuid person_id FK,UK
        varchar email UK
        uuid system_role_id FK
        boolean is_active
    }

    %% ========================================
    %% SCHEMA: CORE - Territorio
    %% ========================================

    core_territory ||--o{ core_territory : "contains"
    core_territory ||--o{ core_territorial_indicator : "has"
    core_territory ||--o{ core_ipr : "benefits"

    core_territory {
        uuid id PK
        varchar code UK
        text name
        uuid territory_type_id FK
        uuid parent_id FK
        numeric area_km2
        integer population
    }

    core_territorial_indicator {
        uuid id PK
        varchar code UK
        uuid territory_id FK
        uuid indicator_type_id FK
        numeric numeric_value
        integer fiscal_year
    }

    %% ========================================
    %% SCHEMA: CORE - IPR (Iniciativas de Inversión)
    %% ========================================

    core_ipr ||--o{ core_ipr_mechanism : "evaluated by"
    core_ipr ||--o{ core_agreement : "formalized"
    core_ipr ||--o{ core_budget_commitment : "funded"
    core_ipr ||--o{ core_ipr_problem : "has issues"
    core_ipr ||--o{ core_work_item : "tracked"
    core_ipr ||--o{ core_progress_report : "reported"

    core_ipr {
        uuid id PK
        varchar codigo_bip UK
        text name
        ipr_nature_enum ipr_nature
        uuid mcd_phase_id FK
        uuid status_id FK
        uuid mechanism_id FK
        uuid formulator_id FK
        uuid territory_id FK
        boolean has_open_problems
    }

    core_ipr_mechanism {
        uuid id PK
        uuid ipr_id FK
        uuid mechanism_id FK
        varchar result_code
        date evaluation_date
        uuid evaluator_id FK
    }

    core_ipr_problem ||--o{ core_operational_commitment : "addressed by"
    core_ipr_problem {
        uuid id PK
        uuid ipr_id FK
        uuid state_id FK
        text description
        date detected_at
        date resolved_at
    }

    %% ========================================
    %% SCHEMA: CORE - Presupuesto
    %% ========================================

    core_budget_program ||--o{ core_budget_commitment : "funds"
    core_budget_program ||--o{ core_fund_program : "allocates"

    core_budget_program {
        uuid id PK
        varchar code
        text name
        integer fiscal_year
        numeric initial_amount
        numeric current_amount
        numeric committed_amount
        numeric accrued_amount
        numeric paid_amount
    }

    core_budget_commitment ||--o{ core_agreement : "backs"
    core_budget_commitment {
        uuid id PK
        varchar commitment_number UK
        uuid budget_program_id FK
        uuid ipr_id FK
        uuid agreement_id FK
        numeric amount
        uuid commitment_state_id FK
    }

    core_fund_program {
        uuid id PK
        varchar code UK
        text name
        uuid fund_type_id FK
        integer fiscal_year
        uuid budget_program_id FK
    }

    %% ========================================
    %% SCHEMA: CORE - Convenios
    %% ========================================

    core_agreement ||--o{ core_agreement_installment : "has payments"
    core_agreement ||--o{ core_rendition : "rendered"
    core_agreement ||--o{ core_work_item : "tracked"

    core_agreement {
        uuid id PK
        varchar code UK
        uuid agreement_type_id FK
        uuid giver_id FK
        uuid receiver_id FK
        uuid ipr_id FK
        numeric total_amount
        uuid state_id FK
        date valid_from
        date valid_to
    }

    core_agreement_installment {
        uuid id PK
        uuid agreement_id FK
        integer installment_number
        numeric amount
        date due_date
        uuid payment_status_id FK
        numeric paid_amount
    }

    core_rendition {
        uuid id PK
        uuid agreement_id FK
        integer rendition_number
        date rendition_date
        numeric amount_rendered
        uuid status_id FK
    }

    %% ========================================
    %% SCHEMA: CORE - Actos Administrativos
    %% ========================================

    core_administrative_act ||--o{ core_resolution : "specializes"
    core_administrative_act {
        uuid id PK
        varchar code UK
        uuid act_type_id FK
        uuid state_id FK
        date act_date
        text subject
    }

    core_resolution ||--o{ core_ipr : "approves"
    core_resolution ||--o{ core_agreement : "authorizes"
    core_resolution {
        uuid id PK
        uuid act_id FK
        uuid resolution_type_id FK
        integer resolution_number
        date resolution_date
    }

    %% ========================================
    %% SCHEMA: CORE - Gobernanza (Comités y Sesiones)
    %% ========================================

    core_committee ||--o{ core_committee_member : "has"
    core_committee ||--o{ core_session : "holds"

    core_committee {
        uuid id PK
        varchar code UK
        text name
        uuid committee_type_id FK
    }

    core_committee_member {
        uuid id PK
        uuid committee_id FK
        uuid person_id FK
        uuid member_role_id FK
        date valid_from
        date valid_to
    }

    core_session ||--o{ core_minute : "documented"
    core_session ||--o{ core_session_agreement : "produces"
    core_session ||--o{ core_crisis_meeting : "emergency"

    core_session {
        uuid id PK
        varchar code
        uuid committee_id FK
        integer session_number
        timestamptz scheduled_at
        uuid status_id FK
    }

    core_session_agreement ||--o{ core_operational_commitment : "generates"
    core_session_agreement {
        uuid id PK
        uuid session_id FK
        integer agreement_number
        text description
        uuid responsible_id FK
        uuid status_id FK
        date due_date
    }

    core_minute {
        uuid id PK
        uuid session_id FK
        text content
        uuid status_id FK
    }

    %% ========================================
    %% SCHEMA: CORE - Gestión Operativa
    %% ========================================

    core_operational_commitment ||--o{ core_commitment_history : "tracked"
    core_operational_commitment ||--o{ core_work_item : "generates"

    core_operational_commitment {
        uuid id PK
        varchar code UK
        uuid commitment_type_id FK
        uuid responsible_id FK
        uuid state_id FK
        text description
        date due_date
        timestamptz completed_at
    }

    core_commitment_history {
        uuid id PK
        uuid commitment_id FK
        uuid previous_state_id FK
        uuid new_state_id FK
        uuid changed_by_id FK
        timestamptz changed_at
    }

    core_work_item ||--o{ core_work_item : "parent"
    core_work_item ||--o{ core_work_item : "blocked_by"
    core_work_item ||--o{ core_work_item_history : "tracked"

    core_work_item {
        uuid id PK
        varchar code UK
        text title
        uuid item_type_id FK
        uuid status_id FK
        uuid assignee_id FK
        uuid division_id FK
        uuid story_id FK
        uuid commitment_id FK
        uuid ipr_id FK
        uuid agreement_id FK
        date due_date
        uuid blocked_by_item_id FK
    }

    core_work_item_history {
        uuid id PK
        uuid work_item_id FK
        uuid event_type_id FK
        uuid previous_status_id FK
        uuid new_status_id FK
        uuid performed_by_id FK
        timestamptz occurred_at
    }

    %% ========================================
    %% SCHEMA: CORE - Alertas y Riesgos
    %% ========================================

    core_alert {
        uuid id PK
        uuid alert_type_id FK
        uuid severity_id FK
        varchar subject_type
        uuid subject_id
        text message
        timestamptz triggered_at
        timestamptz attended_at
    }

    core_risk {
        uuid id PK
        varchar code UK
        uuid risk_type_id FK
        uuid probability_id FK
        uuid impact_id FK
        varchar subject_type
        uuid subject_id
        text description
        uuid status_id FK
    }

    %% ========================================
    %% SCHEMA: CORE - Otros
    %% ========================================

    core_progress_report {
        uuid id PK
        uuid ipr_id FK
        integer report_number
        date report_date
        numeric physical_progress
        numeric financial_progress
        uuid reported_by_id FK
    }

    core_planning_instrument {
        uuid id PK
        varchar code UK
        text name
        uuid instrument_type_id FK
        integer fiscal_year
    }

    core_inventory_item {
        uuid id PK
        varchar code UK
        uuid item_type_id FK
        text description
        numeric acquisition_value
        uuid location_id FK
    }

    core_digital_platform {
        uuid id PK
        varchar code UK
        text name
        uuid platform_type_id FK
        text url
    }

    %% ========================================
    %% SCHEMA: TXN (Event Sourcing)
    %% ========================================

    txn_event {
        uuid id PK
        uuid event_type_id FK
        varchar subject_type
        uuid subject_id
        uuid actor_id FK
        uuid actor_ref_id FK
        timestamptz occurred_at
        timestamptz recorded_at
        jsonb data
        uuid created_by_id FK
    }

    txn_magnitude {
        uuid id PK
        varchar subject_type
        uuid subject_id
        uuid aspect_id FK
        uuid unit_id FK
        numeric numeric_value
        date as_of_date
        timestamptz created_at
        uuid created_by_id FK
    }

    ref_category ||--o{ txn_event : "event_type"
    ref_category ||--o{ txn_magnitude : "aspect"
    core_user ||--o{ txn_event : "actor"
```

---

## 2. ERD por Dominio

### 2.1 Dominio: Meta (Átomos Fundamentales)

```mermaid
erDiagram
    ROLE ||--o{ STORY : "capability for"
    ROLE ||--o{ ROLE : "accountable to"
    PROCESS ||--o{ STORY : "context"
    ENTITY ||--o{ STORY_ENTITY : "participates"
    STORY ||--o{ STORY_ENTITY : "involves"

    ROLE {
        uuid id PK
        varchar code UK "Unique identifier"
        text name "Role name"
        agent_type_enum agent_type "HUMAN|ALGORITHMIC|..."
        cognition_level_enum cognition_level "C0|C1|C2|C3"
        delegation_mode_enum delegation_mode "M1-M6"
        uuid human_accountable_id FK "HAIC constraint"
        text ontology_uri "koda://..."
    }

    PROCESS {
        uuid id PK
        varchar code UK
        text name
        process_layer_enum layer "STRATEGIC|TACTICAL|OPERATIONAL"
    }

    ENTITY {
        uuid id PK
        varchar code UK
        text name
        varchar domain "Bounded context"
    }

    STORY {
        uuid id PK
        varchar code UK
        text name
        text as_a "Role clause"
        text i_want "Action clause"
        text so_that "Benefit clause"
        uuid role_id FK
        uuid process_id FK
        story_status_enum status "DRAFT|ENRICHED|APPROVED|RETIRED"
        text[] acceptance_criteria
    }

    STORY_ENTITY {
        uuid id PK
        uuid story_id FK,UK
        uuid entity_id FK,UK
        story_status_enum status
    }
```

### 2.2 Dominio: IPR y Presupuesto

```mermaid
erDiagram
    IPR ||--o{ IPR_MECHANISM : "evaluated"
    IPR ||--o{ BUDGET_COMMITMENT : "funded"
    IPR ||--o{ AGREEMENT : "formalized"
    IPR ||--o{ IPR_PROBLEM : "issues"
    IPR ||--o{ PROGRESS_REPORT : "tracked"

    BUDGET_PROGRAM ||--o{ BUDGET_COMMITMENT : "allocates"
    BUDGET_PROGRAM ||--o{ FUND_PROGRAM : "distributes"

    BUDGET_COMMITMENT ||--o{ AGREEMENT : "backs"

    IPR {
        uuid id PK
        varchar codigo_bip UK "SNI code"
        text name
        ipr_nature_enum ipr_nature "PROYECTO|PROGRAMA|..."
        uuid mcd_phase_id FK "F0-F5"
        uuid status_id FK "28 states"
        uuid mechanism_id FK "7 tracks"
        uuid formulator_id FK "Organization"
        uuid territory_id FK "Beneficiary territory"
        numeric cofinanciamiento_anf "% ANF"
        boolean has_open_problems
        uuid alert_level_id FK
    }

    IPR_MECHANISM {
        uuid id PK
        uuid ipr_id FK
        uuid mechanism_id FK "SNI|C33|FRIL|..."
        varchar result_code "RS|FI|FC|OT|RF|ITF|AT"
        date evaluation_date
        uuid evaluator_id FK
        numeric evaluation_score
    }

    BUDGET_PROGRAM {
        uuid id PK
        varchar code
        text name
        integer fiscal_year
        uuid program_type_id FK
        uuid subtitle_id FK "21-35"
        numeric initial_amount "(18,2)"
        numeric current_amount "Maintained by trigger"
        numeric committed_amount
        numeric accrued_amount
        numeric paid_amount
    }

    BUDGET_COMMITMENT {
        uuid id PK
        varchar commitment_number UK
        uuid budget_program_id FK
        uuid ipr_id FK
        uuid agreement_id FK
        numeric amount "(18,2)"
        uuid commitment_state_id FK
        date commitment_date
    }

    FUND_PROGRAM {
        uuid id PK
        varchar code UK
        text name
        uuid fund_type_id FK
        integer fiscal_year
        numeric total_amount
        uuid budget_program_id FK
    }

    IPR_PROBLEM {
        uuid id PK
        uuid ipr_id FK
        uuid state_id FK
        uuid problem_type_id FK
        text description
        date detected_at
        date resolved_at
        text solution_applied
    }

    PROGRESS_REPORT {
        uuid id PK
        uuid ipr_id FK
        integer report_number
        date report_date
        numeric physical_progress "(5,2) %"
        numeric financial_progress "(5,2) %"
        text description
        uuid reported_by_id FK
    }

    AGREEMENT {
        uuid id PK
        varchar code UK
        uuid agreement_type_id FK
        uuid giver_id FK
        uuid receiver_id FK
        uuid ipr_id FK
        numeric total_amount
        uuid state_id FK
        date valid_from
        date valid_to
    }
```

### 2.3 Dominio: Convenios y Rendiciones

```mermaid
erDiagram
    AGREEMENT ||--o{ AGREEMENT_INSTALLMENT : "payments"
    AGREEMENT ||--o{ RENDITION : "rendered"
    AGREEMENT ||--o| RESOLUTION : "authorized by"

    ORGANIZATION ||--o{ AGREEMENT : "giver"
    ORGANIZATION ||--o{ AGREEMENT : "receiver"

    AGREEMENT {
        uuid id PK
        varchar code UK
        uuid agreement_type_id FK "MANDATO|TRANSFERENCIA|..."
        uuid giver_id FK "GORE usually"
        uuid receiver_id FK "Executor"
        uuid ipr_id FK
        uuid budget_commitment_id FK
        numeric total_amount
        uuid state_id FK "10 states"
        date valid_from
        date valid_to
        uuid resolution_id FK
    }

    AGREEMENT_INSTALLMENT {
        uuid id PK
        uuid agreement_id FK
        integer installment_number
        numeric amount "(18,2)"
        date due_date
        uuid payment_status_id FK
        timestamptz paid_at
        numeric paid_amount
        varchar payment_reference
    }

    RENDITION {
        uuid id PK
        uuid agreement_id FK
        integer rendition_number
        date rendition_date
        date period_from
        date period_to
        numeric amount_rendered
        uuid status_id FK
        text observations
    }

    ORGANIZATION {
        uuid id PK
        varchar code UK
        text name
        uuid org_type_id FK
        uuid parent_id FK
    }

    RESOLUTION {
        uuid id PK
        uuid act_id FK
        uuid resolution_type_id FK
        integer resolution_number
        date resolution_date
        numeric budget_amount
    }
```

### 2.4 Dominio: Gobernanza

```mermaid
erDiagram
    COMMITTEE ||--o{ COMMITTEE_MEMBER : "composed of"
    COMMITTEE ||--o{ SESSION : "holds"
    SESSION ||--o{ MINUTE : "documented"
    SESSION ||--o{ SESSION_AGREEMENT : "produces"
    SESSION ||--o{ CRISIS_MEETING : "emergency"
    SESSION_AGREEMENT ||--o{ OPERATIONAL_COMMITMENT : "generates"

    COMMITTEE {
        uuid id PK
        varchar code UK
        text name
        uuid committee_type_id FK "CORE|COMISION|COMITE_TECNICO"
        text description
    }

    COMMITTEE_MEMBER {
        uuid id PK
        uuid committee_id FK
        uuid person_id FK
        uuid member_role_id FK "PRESIDENTE|SECRETARIO|MIEMBRO"
        date valid_from
        date valid_to
    }

    SESSION {
        uuid id PK
        varchar code
        uuid committee_id FK
        integer session_number
        uuid session_type_id FK "ORDINARIA|EXTRAORDINARIA"
        timestamptz scheduled_at
        timestamptz actual_start
        timestamptz actual_end
        uuid status_id FK
        text location
    }

    MINUTE {
        uuid id PK
        uuid session_id FK
        text content
        uuid status_id FK
        uuid approved_by_id FK
        timestamptz approved_at
    }

    SESSION_AGREEMENT {
        uuid id PK
        uuid session_id FK
        integer agreement_number
        text description
        uuid responsible_id FK
        uuid status_id FK
        date due_date
    }

    CRISIS_MEETING {
        uuid id PK
        uuid session_id FK
        uuid ipr_id FK
        uuid crisis_type_id FK
        text situation_description
        text actions_agreed
    }

    OPERATIONAL_COMMITMENT {
        uuid id PK
        varchar code UK
        uuid session_id FK
        uuid problem_id FK
        uuid commitment_type_id FK
        uuid responsible_id FK
        uuid state_id FK "6 states"
        text description
        date due_date
        timestamptz completed_at
    }
```

### 2.5 Dominio: Work Items (Gestión Operativa)

```mermaid
erDiagram
    STORY ||--o{ WORK_ITEM : "originates"
    OPERATIONAL_COMMITMENT ||--o{ WORK_ITEM : "generates"
    IPR ||--o{ WORK_ITEM : "tracked by"
    AGREEMENT ||--o{ WORK_ITEM : "tracked by"

    WORK_ITEM ||--o{ WORK_ITEM : "parent-child"
    WORK_ITEM ||--o{ WORK_ITEM : "blocked by"
    WORK_ITEM ||--o{ WORK_ITEM_HISTORY : "history"

    USER ||--o{ WORK_ITEM : "assigned"
    ORGANIZATION ||--o{ WORK_ITEM : "division"

    WORK_ITEM {
        uuid id PK
        varchar code UK "WI-2026-XXXXX"
        text title
        text description
        uuid item_type_id FK "TAREA|HITO|REVISION|APROBACION"
        uuid status_id FK "6 states + transitions"
        uuid assignee_id FK
        uuid division_id FK
        uuid priority_id FK "URGENTE|ALTA|NORMAL|BAJA"
        uuid origin_id FK
        date due_date
        uuid story_id FK "Funtor Story->WorkItem"
        uuid commitment_id FK
        uuid ipr_id FK
        uuid agreement_id FK
        uuid resolution_id FK
        uuid problem_id FK
        uuid parent_id FK
        uuid blocked_by_item_id FK
        text blocked_reason
        timestamptz started_at
        timestamptz completed_at
        uuid verified_by_id FK
        timestamptz verified_at
        text[] tags
    }

    WORK_ITEM_HISTORY {
        uuid id PK
        uuid work_item_id FK
        uuid event_type_id FK "CREATED|STATUS_CHANGE|REASSIGNED|..."
        uuid previous_status_id FK
        uuid new_status_id FK
        uuid previous_assignee_id FK
        uuid new_assignee_id FK
        text comment
        timestamptz occurred_at
        uuid performed_by_id FK
    }

    STORY {
        uuid id PK
        varchar code UK
        text as_a
        text i_want
        text so_that
    }

    OPERATIONAL_COMMITMENT {
        uuid id PK
        varchar code UK
        uuid responsible_id FK
        uuid state_id FK
        date due_date
    }

    USER {
        uuid id PK
        uuid person_id FK,UK
        varchar email UK
        uuid system_role_id FK
        boolean is_active
    }
```

### 2.6 Dominio: Event Sourcing (Transacciones)

```mermaid
erDiagram
    CATEGORY ||--o{ EVENT : "event_type"
    CATEGORY ||--o{ MAGNITUDE : "aspect"
    CATEGORY ||--o{ MAGNITUDE : "unit"
    USER ||--o{ EVENT : "actor"
    ACTOR ||--o{ EVENT : "actor_ref"

    EVENT {
        uuid id PK
        uuid event_type_id FK "CDP|COMPROMISO|DEVENGO|PAGO|..."
        varchar subject_type "ipr|agreement|budget_commitment"
        uuid subject_id "Polymorphic FK"
        uuid actor_id FK "core.user"
        uuid actor_ref_id FK "ref.actor (optional)"
        timestamptz occurred_at "Partition key (PK compuesto)"
        timestamptz recorded_at
        jsonb data "Event payload"
        uuid created_by_id FK
    }

    MAGNITUDE {
        uuid id PK
        varchar subject_type
        uuid subject_id
        uuid aspect_id FK "BUDGETED|CURRENT|COMMITTED|..."
        uuid unit_id FK "CLP|UTM|UF|PERCENT"
        numeric numeric_value "(18,2)"
        date as_of_date "Partition key (PK compuesto)"
        timestamptz created_at
        uuid created_by_id FK
    }

    CATEGORY {
        uuid id PK
        varchar scheme
        varchar code
        text label
        jsonb valid_transitions
    }

    USER {
        uuid id PK
        varchar email UK
    }

    ACTOR {
        uuid id PK
        varchar code UK
        agent_type_enum agent_type
    }
```

---

## 3. Data Dictionary - Entidades Principales

### 3.1 core.ipr (Iniciativa de Inversión Pública Regional)

| Column | Type | Null | Key | Description |
|--------|------|------|-----|-------------|
| id | UUID | No | PK | Identificador único |
| codigo_bip | VARCHAR(20) | No | UK | Código SNI/BIP |
| name | TEXT | No | | Nombre de la iniciativa |
| ipr_nature | ipr_nature_enum | No | | PROYECTO\|PROGRAMA\|PROGRAMA_INVERSION\|ESTUDIO_BASICO\|ANF |
| ipr_type_id | UUID | Yes | FK→ref.category | Tipo funcional |
| mcd_phase_id | UUID | Yes | FK→ref.category | Fase MCD (F0-F5) |
| status_id | UUID | Yes | FK→ref.category | Estado operativo (28 estados) |
| budget_subtitle_id | UUID | Yes | FK→ref.category | Subtítulo presupuestario (21-35) |
| funding_source_id | UUID | Yes | FK→ref.category | Fuente de financiamiento |
| mechanism_id | UUID | Yes | FK→ref.category | Mecanismo de evaluación |
| formulator_id | UUID | Yes | FK→core.organization | Organización formuladora |
| executor_id | UUID | Yes | FK→core.organization | Unidad técnica ejecutora |
| territory_id | UUID | Yes | FK→core.territory | Territorio beneficiario |
| assignee_id | UUID | Yes | FK→core.user | Analista asignado |
| has_open_problems | BOOLEAN | No | | Tiene problemas abiertos |
| alert_level_id | UUID | Yes | FK→ref.category | Nivel de alerta |
| created_at | TIMESTAMPTZ | No | | Fecha creación |
| updated_at | TIMESTAMPTZ | No | | Fecha actualización |
| deleted_at | TIMESTAMPTZ | Yes | | Soft delete |

**Índices:**
- `pk_ipr` (id) - Primary
- `uk_ipr_bip` (codigo_bip) - Unique
- `idx_ipr_phase` (mcd_phase_id)
- `idx_ipr_status` (status_id)
- `idx_ipr_mechanism` (mechanism_id)
- `idx_ipr_phase_mechanism` (mcd_phase_id, mechanism_id) - Composite

### 3.2 core.work_item (Ítem de Trabajo)

| Column | Type | Null | Key | Description |
|--------|------|------|-----|-------------|
| id | UUID | No | PK | Identificador único |
| code | VARCHAR(32) | Yes | UK | Código generado (WI-YYYY-NNNNN) |
| title | TEXT | No | | Título descriptivo |
| description | TEXT | Yes | | Descripción detallada |
| item_type_id | UUID | No | FK→ref.category | Tipo (TAREA\|HITO\|REVISION\|APROBACION) |
| status_id | UUID | No | FK→ref.category | Estado (6 estados con transiciones) |
| assignee_id | UUID | Yes | FK→core.user | Usuario asignado |
| division_id | UUID | Yes | FK→core.organization | División responsable |
| priority_id | UUID | Yes | FK→ref.category | Prioridad |
| due_date | DATE | Yes | | Fecha límite |
| story_id | UUID | Yes | FK→meta.story | Historia origen |
| commitment_id | UUID | Yes | FK→core.operational_commitment | Compromiso origen |
| ipr_id | UUID | Yes | FK→core.ipr | IPR relacionada |
| agreement_id | UUID | Yes | FK→core.agreement | Convenio relacionado |
| parent_id | UUID | Yes | FK→core.work_item | Ítem padre (jerarquía) |
| blocked_by_item_id | UUID | Yes | FK→core.work_item | Bloqueado por |
| blocked_reason | TEXT | Yes | | Razón del bloqueo |
| started_at | TIMESTAMPTZ | Yes | | Inicio real |
| completed_at | TIMESTAMPTZ | Yes | | Finalización |
| verified_by_id | UUID | Yes | FK→core.user | Verificador |
| verified_at | TIMESTAMPTZ | Yes | | Fecha verificación |
| tags | TEXT[] | Yes | | Etiquetas |

**Índices:**
- `idx_work_item_assignee` (assignee_id)
- `idx_work_item_status` (status_id)
- `idx_work_item_due` (due_date)
- `idx_work_item_blocked` (blocked_by_item_id) WHERE blocked_by_item_id IS NOT NULL
- `idx_workitem_tags` (tags) USING GIN

### 3.3 ref.category (Patrón Category - Gist 14.0)

| Column | Type | Null | Key | Description |
|--------|------|------|-----|-------------|
| id | UUID | No | PK | Identificador único |
| scheme | VARCHAR(32) | No | UK(1) | Esquema/namespace (75+ schemes) |
| code | VARCHAR(32) | No | UK(2) | Código dentro del scheme |
| label | TEXT | No | | Etiqueta visible |
| description | TEXT | Yes | | Descripción |
| parent_id | UUID | Yes | FK→ref.category | Categoría padre (jerarquía) |
| parent_code | VARCHAR(32) | Yes | | Código del padre (para seed) |
| phase_id | UUID | Yes | FK→ref.category | Fase asociada (para ipr_state) |
| valid_transitions | JSONB | Yes | | Estados destino válidos |
| sort_order | INTEGER | Yes | | Orden de presentación |

**Schemes principales:**
- `mcd_phase` - Fases MCD (F0-F5)
- `ipr_state` - Estados IPR (28)
- `ipr_nature` - Naturaleza IPR
- `mechanism` - Mecanismos de evaluación (7 tracks)
- `work_item_status` - Estados work item (6)
- `commitment_state` - Estados compromiso (6)
- `agreement_state` - Estados convenio (10)
- `event_type` - Tipos de evento
- `aspect` - Aspectos presupuestarios

---

## 4. Relaciones Clave

### 4.1 Cardinalidades Principales

| Relación | Cardinalidad | Descripción |
|----------|--------------|-------------|
| Organization → Person | 1:M | Una organización emplea muchas personas |
| Person → User | 1:1 | Una persona tiene exactamente un usuario (UNIQUE) |
| IPR → Agreement | 1:M | Una IPR puede tener múltiples convenios |
| IPR → Budget_Commitment | 1:M | Una IPR puede tener múltiples compromisos |
| Agreement → Installment | 1:M | Un convenio tiene múltiples cuotas |
| Committee → Session | 1:M | Un comité celebra múltiples sesiones |
| Session → Session_Agreement | 1:M | Una sesión produce múltiples acuerdos |
| Story → Work_Item | 1:M | Una historia origina múltiples ítems |
| Work_Item → Work_Item | 1:M | Jerarquía padre-hijo |
| Category → Category | 1:M | Jerarquía de categorías |

### 4.2 Polimorfismo (subject_type/subject_id)

Las siguientes tablas usan el patrón polimórfico:

| Tabla | subject_type values | Descripción |
|-------|---------------------|-------------|
| txn.event | ipr, agreement, budget_commitment, work_item | Eventos sobre cualquier entidad |
| txn.magnitude | ipr, budget_program, agreement | Magnitudes financieras |
| core.alert | ipr, agreement, work_item, commitment | Alertas sobre cualquier entidad |
| core.risk | ipr, agreement, project | Riesgos identificados |

---

## 5. Constraints de Integridad

### 5.1 CHECK Constraints

```sql
-- HAIC: Agentes no-humanos requieren humano accountable
CONSTRAINT chk_human_accountable CHECK (
    agent_type = 'HUMAN' OR human_accountable_id IS NOT NULL
)

-- Person-User: Relación 1:1
CONSTRAINT uk_user_person UNIQUE (person_id)

-- Category: Unicidad scheme+code
CONSTRAINT uk_category_scheme_code UNIQUE (scheme, code)

-- Budget Program: Unicidad code+year
CONSTRAINT uk_budget_program UNIQUE (code, fiscal_year)
```

### 5.2 Transiciones de Estado (valid_transitions)

El campo `valid_transitions` en `ref.category` define las transiciones permitidas:

```sql
-- Ejemplo: work_item_status
PENDIENTE → [EN_PROGRESO, CANCELADO]
EN_PROGRESO → [COMPLETADO, BLOQUEADO, CANCELADO]
BLOQUEADO → [EN_PROGRESO]
COMPLETADO → [VERIFICADO, EN_PROGRESO]
VERIFICADO → [] (terminal)
CANCELADO → [] (terminal)
```

---

## 6. Notas de Implementación

### 6.1 Particionamiento

| Tabla | Estrategia | Columna | Particiones |
|-------|------------|---------|-------------|
| txn.event | RANGE | occurred_at | 12 mensuales + default |
| txn.magnitude | RANGE | as_of_date | 4 trimestrales + default |

### 6.2 Índices Especiales

| Tipo | Tablas | Propósito |
|------|--------|-----------|
| GIN | work_item(tags) | Búsqueda en arrays |
| GIN | ipr(metadata), agreement(metadata) | Búsqueda JSONB |
| GIN FTS | ipr(name), work_item(title+description) | Full-text search |
| Partial | *_active WHERE deleted_at IS NULL | Registros activos |

### 6.3 ENUMs

| ENUM | Valores | Usado en |
|------|---------|----------|
| agent_type_enum | HUMAN, AI, ALGORITHMIC, ORGANIZATIONAL, MACHINE, MIXED | meta.role, ref.actor |
| ipr_nature_enum | PROYECTO, PROGRAMA, PROGRAMA_INVERSION, ESTUDIO_BASICO, ANF | core.ipr |
| cognition_level_enum | C0, C1, C2, C3 | meta.role |
| delegation_mode_enum | M1, M2, M3, M4, M5, M6 | meta.role |
| process_layer_enum | STRATEGIC, TACTICAL, OPERATIONAL | meta.process |
| story_status_enum | DRAFT, ENRICHED, APPROVED, RETIRED | meta.story, meta.story_entity |

---

**Fin del Documento ERD**

*Generado: 2026-01-27*
*Modelo: GORE_OS v3.0*
