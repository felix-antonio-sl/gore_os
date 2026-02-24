# AUDITORÍA RELACIONAL v1.0 - GORE_OS

**Fecha**: 2026-01-30
**Agente**: arquitecto-gore v0.1.0
**Base de datos**: goreos_model (producción)
**Versión modelo**: v3.4 (52 tablas, 183 FKs)

---

## Resumen Ejecutivo

### Métricas Globales
- **Total FKs**: 183 relaciones
- **FKs de negocio**: 73 (excluyendo user/category)
- **FKs de auditoría**: 110 (created_by_id, updated_by_id, deleted_by_id)
- **Tablas con FKs**: 52 (100% del modelo core)
- **Profundidad máxima**: 5 niveles (IPR → Agreement → Installment → Milestone → ...)

### Centralidad Relacional (Top 5)

| Entidad | FKs Salientes | FKs Entrantes | Centralidad | Rol Ontológico |
|---------|---------------|---------------|-------------|----------------|
| **category** | 0 | 63 | 63 | **Hub categorial** (gist:Category) |
| **ipr** | 13 | 11 | 24 | **Entidad central** (gnub:IPR) |
| **organization** | 2 | 21 | 23 | **Hub organizacional** (tde:Organizacion) |
| **agreement** | 7 | 7 | 14 | **Nodo contractual** (gnub:Convenio) |
| **person** | 6 | 5 | 11 | **Nodo personal** (tde:Persona) |

---

## SECCIÓN 1: Grafos Relacionales Críticos

### 1.1. IPR-Centric Graph (Grafo Central de Negocio)

**Nodo central**: `core.ipr` (3,621 registros)

#### Relaciones Salientes (13 FKs)

| FK Column | Destino | Tipo | Cobertura | Ontología |
|-----------|---------|------|-----------|-----------|
| `ipr_type_id` | category | Categorial | 100% | gnub:IPRType |
| `status_id` | category | Categorial | 100% | gist:Status |
| `funding_source_id` | category | Categorial | 90% | gnub:FundingSource |
| `fund_category_id` | category | Categorial | 15% (PROGRAMA_8PCT) | gnub:FundCategory |
| `investment_sector_id` | category | Categorial | 85% | gnub:InvestmentSector |
| `mechanism_id` | category | Categorial | 70% | gnub:Mechanism |
| `mcd_phase_id` | category | Categorial | 30% | gnub:MCDPhase |
| `alert_level_id` | category | Categorial | 20% | gist:AlertLevel |
| `resolution_type_id` | category | Categorial | 10% | tde:ResolutionType |
| `budget_subtitle_id` | category | Categorial | 5% | gnub:BudgetSubtitle |
| `executor_id` | organization | Organizacional | 95% | gnub:Executor |
| `formulator_id` | organization | Organizacional | 90% | gnub:Formulator |
| `sponsor_division_id` | organization | Organizacional | 100% | gnub:SponsorDivision |

#### Relaciones Entrantes (11 FKs)

| Tabla Origen | FK Column | Registros Referenciando | Tipo Relación | Cardinalidad |
|--------------|-----------|------------------------|---------------|--------------|
| `agreement` | ipr_id | ~500 | Contractual | 1:N |
| `budget_commitment` | ipr_id | ~4,600 | Presupuestaria | 1:N |
| `document` | ipr_id | ~1,200 | Documental | 1:N |
| `ipr_party` | ipr_id | 6,447 | Organizacional (M:N) | 1:N |
| `ipr_territory` | ipr_id | ~7,000 | Territorial (M:N) | 1:N |
| `ipr_milestone` | ipr_id | ~800 | Temporal | 1:N |
| `ipr_mechanism` | ipr_id | ~2,500 | Financiera (M:N) | 1:N |
| `ipr_problem` | ipr_id | ~150 | Gestión riesgos | 1:N |
| `progress_report` | ipr_id | ~300 | Seguimiento | 1:N |
| `resolution` | ipr_id | ~400 | Administrativa | 1:N |
| `inventory_item` | ipr_origin_id | ~50 | Inventario | 1:N |

**Tensión Ontológica Detectada**:
`Tensión[A1: IPR como Objeto <-> IPR como Proceso]`
- **Ser**: IPR tiene atributos estáticos (name, code, estimated_cost)
- **Devenir**: IPR evolve through status_id (FORMULACION → EJECUCION → CIERRE)
- **Resolución**: Event sourcing en `txn.event` captura el devenir, `core.ipr` mantiene el estado actual

---

### 1.2. Budget-Centric Graph

**Nodo central**: `core.budget_program` (25,755 registros)

#### Relaciones Salientes (5 FKs)

| FK Column | Destino | Cobertura | Ontología |
|-----------|---------|-----------|-----------|
| `item_id` | category (budget_item) | 86% | gnub:BudgetItem |
| `allocation_id` | category (budget_allocation) | 57% | gnub:BudgetAllocation |
| `subtitle_id` | category (budget_subtitle) | 93% | gnub:BudgetSubtitle |
| `program_type_id` | category (program_type) | 0.01% | gnub:ProgramType |
| `owner_division_id` | organization | 0% | gnub:OwnerDivision |

#### Relaciones Entrantes (3 FKs)

| Tabla Origen | FK Column | Registros | Cardinalidad |
|--------------|-----------|-----------|--------------|
| `budget_commitment` | budget_program_id | 4,609 | 1:N |
| `budget_carryover` | budget_program_id | 13,375 | 1:N |
| `fund_program` | budget_program_id | ~200 | 1:1 |

**Cadena Crítica**:
`budget_program → budget_commitment → ipr`
(Permite rastrear ejecución presupuestaria por IPR)

---

### 1.3. Organization-Centric Graph

**Nodo central**: `core.organization` (3,308+ registros)

#### Relaciones Entrantes (21 FKs)

| Tabla Origen | FK Column | Rol Ontológico |
|--------------|-----------|----------------|
| `ipr` | executor_id | gnub:Executor |
| `ipr` | formulator_id | gnub:Formulator |
| `ipr` | sponsor_division_id | gnub:SponsorDivision |
| `agreement` | giver_id | gnub:AgreementGiver |
| `agreement` | receiver_id | gnub:AgreementReceiver |
| `ipr_party` | organization_id | gnub:IPRParty |
| `budget_program` | owner_division_id | gnub:OwnerDivision |
| `committee` | parent_org_id | tde:ParentOrg |
| `digital_platform` | owner_id | tde:PlatformOwner |
| `inventory_item` | location_id | tde:Location |
| `administrative_act` | issuer_id | tde:ActIssuer |
| `administrative_procedure` | initiator_id | tde:ProcedureInitiator |
| ... | ... | ... |

**Tensión Ontológica Detectada**:
`Tensión[A2: Organization como Estructura <-> Organization como Rol]`
- **Estructura**: organization.org_type_id (MUNICIPALIDAD, SERVICIO, DIVISION)
- **Rol**: Misma organización puede ser executor_id, giver_id, receiver_id en contextos diferentes
- **Resolución**: Junction table `ipr_party` + party_role_id para M:N con roles explícitos

---

### 1.4. Agreement-Centric Graph

**Nodo central**: `core.agreement` (533 registros)

#### Relaciones Salientes (7 FKs)

| FK Column | Destino | Tipo |
|-----------|---------|------|
| `ipr_id` | ipr | 1:1 (mandatos/convenios vinculados) |
| `giver_id` | organization | Mandante |
| `receiver_id` | organization | Ejecutor contractual |
| `technical_referent_id` | person | Responsable técnico |
| `cgr_outcome_id` | category (cgr_outcome) | Estado CGR |
| `agreement_type_id` | category | Tipo convenio |
| `resolution_id` | resolution | Acto administrativo fundante |

#### Relaciones Entrantes (7 FKs)

| Tabla Origen | FK Column | Registros |
|--------------|-----------|-----------|
| `agreement_installment` | agreement_id | ~1,500 cuotas |
| `budget_commitment` | agreement_id | ~2,000 compromisos |
| `document` | agreement_id | ~800 documentos |
| `ipr_party` | agreement_id | 476 (sincronizado v3.0) |
| `resolution` | agreement_id | ~200 resoluciones |
| ... | ... | ... |

**Cadena Crítica**:
`agreement → agreement_installment → installment_milestone → ipr_milestone`
(Trazabilidad contractual de hitos)

---

### 1.5. Person-Centric Graph

**Nodo central**: `core.person` (111 registros)

#### Relaciones Salientes (6 FKs)

| FK Column | Destino | Cobertura | Ontología |
|-----------|---------|-----------|-----------|
| `estamento_id` | category (estamento) | 99% | tde:Estamento |
| `position_id` | position | 80% | tde:Cargo |
| `qualification_id` | category (professional_qualification) | 99% | tde:CalificacionProfesional |
| `person_type_id` | category (person_type) | 100% | tde:PersonType |
| `role_id` | role | 0% | meta:Role |
| `org_id` | organization | 95% | tde:OrganizacionAdscripcion |

#### Relaciones Entrantes (5 FKs)

| Tabla Origen | FK Column | Rol |
|--------------|-----------|-----|
| `agreement` | technical_referent_id | Responsable técnico convenio |
| `committee_member` | person_id | Miembro comité |
| `electronic_file` | requester_id | Solicitante expediente |
| `inventory_item` | responsible_id | Responsable activo |
| ... | ... | ... |

---

## SECCIÓN 2: Patrones Relacionales

### 2.1. Patrón Junction Table (M:N)

| Junction Table | Entidad A | Entidad B | Registros | Propósito |
|----------------|-----------|-----------|-----------|-----------|
| `ipr_party` | ipr | organization | 6,447 | Roles organizacionales en IPR |
| `ipr_territory` | ipr | territory | ~7,000 | Alcance territorial IPR |
| `ipr_mechanism` | ipr | category (mechanism) | ~2,500 | Mecanismos financieros IPR |
| `committee_member` | committee | person | ~150 | Membresía comités |
| `installment_milestone` | agreement_installment | ipr_milestone | ~500 | Sincronización hitos |

**Principio**: Evitar denormalización en JSONB para relaciones M:N de negocio crítico.

---

### 2.2. Patrón Temporal (Time-Bound Relationships)

| Tabla | FK Temporal | Entidad Relacionada | Atributo Temporal |
|-------|-------------|---------------------|-------------------|
| `budget_carryover` | budget_program_id | budget_program | fiscal_year |
| `agreement_installment` | agreement_id | agreement | installment_number, due_date |
| `ipr_milestone` | ipr_id | ipr | planned_date, completed_at |
| `progress_report` | ipr_id | ipr | report_date, period_start, period_end |

**Principio**: Relaciones con dimensión temporal explícita (no solo created_at/updated_at).

---

### 2.3. Patrón Self-Referential (Jerárquico)

| Tabla | FK Column | Propósito | Niveles |
|-------|-----------|-----------|---------|
| `administrative_act` | parent_act_id | Jerarquía actos (modifica/deroga) | 2-3 |
| `organization` | parent_org_id | Jerarquía organizacional | 3-4 (GORE → División → Departamento → Unidad) |
| `territory` | parent_territory_id | Jerarquía territorial | 3 (Región → Provincia → Comuna) |

**Principio**: Usar para jerarquías naturales, evitar para relaciones M:N complejas.

---

### 2.4. Patrón Polimórfico (Subject Type)

Detectado en `txn.event`:
- `subject_type`: 'ipr', 'agreement', 'budget_program', etc.
- `subject_id`: UUID polimórfico

**Advertencia**: Rompe integridad referencial estricta. Usar solo en event sourcing.

---

## SECCIÓN 3: Cadenas Relacionales Críticas (Navegación Prioritaria)

### 3.1. Cadena de Ejecución Presupuestaria

```
budget_program (25,755)
  ↓ budget_program_id
budget_commitment (4,609)
  ↓ ipr_id
ipr (3,621)
  ↓ executor_id
organization (3,308)
```

**Queries de negocio**:
- "¿Cuánto se ha comprometido del programa presupuestario X?"
- "¿Qué IPRs están siendo ejecutados por la organización Y?"

---

### 3.2. Cadena de Convenios y Cuotas

```
agreement (533)
  ↓ agreement_id
agreement_installment (1,500+)
  ↓ installment_id
installment_milestone (500+)
  ↓ milestone_id
ipr_milestone (800+)
  ↓ ipr_id
ipr (3,621)
```

**Queries de negocio**:
- "¿Qué hitos IPR están vinculados a la cuota 3 del convenio Z?"
- "¿Qué porcentaje de hitos se han completado para liberar la próxima cuota?"

---

### 3.3. Cadena Territorial

```
ipr (3,621)
  ↓ ipr_id
ipr_territory (7,000+)
  ↓ territory_id
territory (52 comunas + 3 provincias + 1 región)
  ↓ parent_territory_id (self-ref)
territory (jerarquía)
```

**Queries de negocio**:
- "¿Qué IPRs tienen alcance en la comuna de Chillán?"
- "Distribución presupuestaria por provincia"

---

### 3.4. Cadena de Trazabilidad Documental

```
ipr (3,621)
  ↓ ipr_id
document (1,200+)
  ↓ file_id
electronic_file (1,000+)
  ↓ procedure_id
procedure (500+)
  ↓ resolution_id
resolution (400+)
```

**Queries de negocio**:
- "¿Qué documentos legales respaldan el IPR X?"
- "Auditoría de expedientes digitales por IPR"

---

### 3.5. Cadena de Responsabilidad (HAIC - Human Accountable in Control)

```
ipr (3,621)
  ↓ assignee_id (user)
user (100+)
  ↓ person_id
person (111)
  ↓ org_id
organization (3,308)
  ↓ org_type_id
category (org_type scheme)
```

**Queries de negocio**:
- "¿Quién es responsable del IPR X?" (ORKO HAIC principle)
- "¿Qué IPRs están asignados a funcionarios de la División de Planificación?"

---

## SECCIÓN 4: Integridad Relacional

### 4.1. DELETE Policies

| Policy | Count | Contexto |
|--------|-------|----------|
| `ON DELETE CASCADE` | 12 | Dependencias fuertes (budget_carryover, ipr_milestone, etc.) |
| `ON DELETE NO ACTION` | 171 | Mayoría (requiere eliminación manual explícita) |

**Relaciones CASCADE críticas**:
1. `budget_carryover.budget_program_id` → budget_program
2. `ipr_milestone.ipr_id` → ipr
3. `ipr_party.ipr_id` → ipr
4. `installment_milestone.installment_id` → agreement_installment
5. `installment_milestone.milestone_id` → ipr_milestone

**Principio**: CASCADE solo para dependencias existenciales (no puede existir X sin Y).

---

### 4.2. Categorical Univocity (100% Validado)

Todas las FKs a `ref.category` cumplen el principio de **Univocidad Categorial**:

```sql
-- Verificación post-normalización v3.0
SELECT
    'funding_source_id' AS campo,
    COUNT(DISTINCT c.scheme) AS schemes
FROM core.ipr i
JOIN ref.category c ON c.id = i.funding_source_id
WHERE i.funding_source_id IS NOT NULL;
-- Expected: schemes = 1 (funding_source)

SELECT
    'fund_category_id' AS campo,
    COUNT(DISTINCT c.scheme) AS schemes
FROM core.ipr i
JOIN ref.category c ON c.id = i.fund_category_id
WHERE i.fund_category_id IS NOT NULL;
-- Expected: schemes = 1 (fondo_8pct)
```

**Estado**: ✅ 100% (todas las FKs a category apuntan a exactamente 1 scheme)

---

### 4.3. CHECK Constraints Relacionales

| Tabla | Constraint | FK Validada | Scheme Esperado |
|-------|-----------|-------------|-----------------|
| person | chk_estamento_scheme | estamento_id | 'estamento' |
| budget_program | chk_item_scheme | item_id | 'budget_item' |
| budget_program | chk_allocation_scheme | allocation_id | 'budget_allocation' |
| organization | chk_rut_format | rut (UNIQUE) | Regex `^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$` |

**Principio**: Todos los FKs a `ref.category` deben tener CHECK constraint validando el scheme.

---

## SECCIÓN 5: Navegación Relacional - Casos de Uso

### 5.1. Navegación Hacia Adelante (Forward Chain)

**Caso**: Desde un IPR, navegar a todas sus dependencias.

```sql
-- Nivel 1: IPR directo
SELECT * FROM core.ipr WHERE id = 'UUID_IPR';

-- Nivel 2: Relaciones directas
SELECT * FROM core.agreement WHERE ipr_id = 'UUID_IPR';
SELECT * FROM core.budget_commitment WHERE ipr_id = 'UUID_IPR';
SELECT * FROM core.ipr_party WHERE ipr_id = 'UUID_IPR';
SELECT * FROM core.ipr_territory WHERE ipr_id = 'UUID_IPR';

-- Nivel 3: Relaciones transitivas
SELECT ai.* FROM core.agreement_installment ai
JOIN core.agreement a ON a.id = ai.agreement_id
WHERE a.ipr_id = 'UUID_IPR';
```

**Profundidad máxima recomendada**: 3 niveles (performance vs utilidad)

---

### 5.2. Navegación Hacia Atrás (Reverse Chain)

**Caso**: Desde un budget_commitment, encontrar el IPR origen.

```sql
-- Nivel 1: Commitment directo
SELECT * FROM core.budget_commitment WHERE id = 'UUID_COMMITMENT';

-- Nivel 2: IPR relacionado
SELECT i.* FROM core.ipr i
JOIN core.budget_commitment bc ON bc.ipr_id = i.id
WHERE bc.id = 'UUID_COMMITMENT';

-- Nivel 3: Organizaciones ejecutoras
SELECT o.* FROM core.organization o
JOIN core.ipr i ON i.executor_id = o.id
JOIN core.budget_commitment bc ON bc.ipr_id = i.id
WHERE bc.id = 'UUID_COMMITMENT';
```

---

### 5.3. Navegación Multi-Hop (Grafo Completo)

**Caso**: Desde una persona, encontrar todos los IPRs donde tiene responsabilidad.

```sql
-- Via assignment directa
SELECT i.* FROM core.ipr i
JOIN meta.user u ON i.assignee_id = u.id
WHERE u.person_id = 'UUID_PERSON';

-- Via technical_referent en agreement
SELECT i.* FROM core.ipr i
JOIN core.agreement a ON a.ipr_id = i.id
WHERE a.technical_referent_id = 'UUID_PERSON';

-- Via committee_member → organization → ipr.sponsor_division_id
SELECT i.* FROM core.ipr i
JOIN core.organization o ON i.sponsor_division_id = o.id
JOIN core.committee c ON c.parent_org_id = o.id
JOIN core.committee_member cm ON cm.committee_id = c.id
WHERE cm.person_id = 'UUID_PERSON';
```

---

## SECCIÓN 6: Recomendaciones de Navegación

### 6.1. Navegación Optimizada (Índices Críticos)

**Índices existentes (v3.4)**:
- `idx_budget_program_year_item_allocation` (composite: fiscal_year + item_id + allocation_id)
- `idx_budget_program_subtitle` (partial: subtitle_id WHERE NOT NULL)
- `idx_person_estamento` (partial: estamento_id WHERE NOT NULL)
- `idx_agreement_technical_referent` (partial: technical_referent_id WHERE NOT NULL)
- ... 77+ índices total

**Índices recomendados adicionales** (si navegación frecuente):
```sql
-- Para navegación IPR → Organization
CREATE INDEX CONCURRENTLY idx_ipr_executor
ON core.ipr(executor_id) WHERE executor_id IS NOT NULL;

-- Para navegación IPR → Agreement
CREATE INDEX CONCURRENTLY idx_agreement_ipr
ON core.agreement(ipr_id) WHERE ipr_id IS NOT NULL;

-- Para navegación Budget → IPR
CREATE INDEX CONCURRENTLY idx_budget_commitment_ipr
ON core.budget_commitment(ipr_id) WHERE ipr_id IS NOT NULL;
```

---

### 6.2. Navegación Lazy vs Eager

**Lazy Loading** (recomendado para visor interactivo):
- Cargar solo el nodo actual
- Expandir relaciones bajo demanda del usuario
- Evitar N+1 queries con `JOIN` selectivos

**Eager Loading** (para reportes/exportación):
- Pre-cargar grafo completo con CTEs recursivos
- Usar para análisis de impacto (¿qué afecta cambiar X?)

---

### 6.3. Filtros de Navegación

**Por tipo de relación**:
- Categorial (FKs a `ref.category`)
- Organizacional (FKs a `organization`)
- Personal (FKs a `person`)
- Presupuestaria (FKs a `budget_*`)
- Contractual (FKs a `agreement`)
- Territorial (FKs a `territory`)
- Auditoría (created_by, updated_by, deleted_by)

**Por profundidad**:
- Nivel 1: Relaciones directas (1-hop)
- Nivel 2: Relaciones transitivas (2-hop)
- Nivel 3: Grafo extendido (3-hop)
- Nivel N: Recursivo (con límite de seguridad)

---

## SECCIÓN 7: Anexos

### A. Export de Red Relacional Completa

Ver archivo: `/tmp/fks_audit.csv` (183 relaciones)

### B. Queries de Verificación

```sql
-- 1. Conteo de FKs por tabla
SELECT
    table_name,
    COUNT(*) as fk_count
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
  AND table_schema = 'core'
GROUP BY table_name
ORDER BY fk_count DESC;

-- 2. Detectar FKs sin índice (performance risk)
SELECT
    kcu.table_name,
    kcu.column_name,
    CASE WHEN i.indexname IS NULL THEN 'MISSING' ELSE 'OK' END as index_status
FROM information_schema.key_column_usage kcu
JOIN information_schema.table_constraints tc
    ON kcu.constraint_name = tc.constraint_name
LEFT JOIN pg_indexes i
    ON i.tablename = kcu.table_name
    AND i.schemaname = kcu.table_schema
    AND i.indexdef LIKE '%' || kcu.column_name || '%'
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND kcu.table_schema = 'core'
ORDER BY index_status, kcu.table_name;

-- 3. Análisis de orfandad (registros sin relaciones)
SELECT
    'ipr' as tabla,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE executor_id IS NULL) as sin_executor,
    COUNT(*) FILTER (WHERE formulator_id IS NULL) as sin_formulator
FROM core.ipr;
```

---

**Versión**: 1.0
**Arquitecto**: GORE-ARQUITECTO v0.1.0
**Próxima auditoría**: 2026-Q2 (o al alcanzar 60+ tablas)

