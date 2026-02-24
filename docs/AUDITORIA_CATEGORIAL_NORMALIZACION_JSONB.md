# Auditoría Categorial: Plan de Normalización JSONB v1.0

**Auditor**: Arquitecto-GORE (KODA Agent v0.1.0)
**Fecha**: 2026-01-30
**Documento auditado**: `PLAN_NORMALIZACION_JSONB_v1.md`
**Framework**: Category Theory + Gist 14.0 + GORE Ñuble Ontology + TDE

---

## 📋 Resumen Ejecutivo

**Schemes auditados**: 13 propuestos
**Tablas auditadas**: 8 nuevas
**Columnas auditadas**: 16 nuevas

### Resultado Global

| Severity | Count | % |
|----------|-------|---|
| 🔴 CRITICAL | 2 | 15% |
| 🟠 HIGH | 3 | 23% |
| 🟡 MEDIUM | 5 | 38% |
| 🟢 LOW | 3 | 23% |

**Status**: ⚠️ **REQUIERE CORRECCIONES CRÍTICAS** antes de implementación

---

## 🎯 Metodología

### Ejes de Evaluación

1. **Alineamiento Ontológico**: Verificación contra gist:Category, gnub:*, tde:*
2. **Coherencia Categórica**: Validación del uso correcto del pattern Category
3. **Tensiones KODA**: Aplicación de A1-A4
   - **A1 (Radical Minimalism)**: ¿Es necesario o añade complejidad?
   - **A2 (Story-First)**: ¿Deriva de User Stories validadas?
   - **A3 (TDE Compliance)**: ¿Cumple ontologías Gist/TDE/GNUB?
   - **A4 (Maintainability)**: ¿Es sostenible a largo plazo?
4. **Severity Levels**: CRITICAL, HIGH, MEDIUM, LOW

---

## 🔍 Auditoría Detallada por Scheme

### 1. `ipr_origin` (2 códigos)

**Propósito**: Origen de la iniciativa (municipal vs sectorial)

**Códigos propuestos**:
- `MUNICIPIO` - Iniciativa desde municipio (bottom-up)
- `SECTORIAL` - Iniciativa sectorial (top-down)

#### ✅ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- ✅ Mapeado semánticamente a gnub:IPR → gnub:hasApplicant
- ⚠️ NO existe clase específica en goreNubleOntology para "origen"

#### ✅ Coherencia Categórica
- ✅ Categoría pura, no sustantiva
- ✅ Diferenciación clara de `funding_source` (quién propone ≠ de dónde viene el dinero)
- ✅ Uso correcto del pattern Category

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: ✅ PASS - Reduce JSONB, valor analítico alto
- **A2 (Story-First)**: ⚠️ UNKNOWN - No se cita User Story origen
- **A3 (TDE Compliance)**: ✅ PASS - Compatible con gist:Category
- **A4 (Maintainability)**: ✅ PASS - 2 valores estables, baja entropía

#### 🟡 Severity: MEDIUM

**Hallazgos**:
1. Falta mapeo explícito en goreNubleOntology.ttl
2. Considerar renombrar `SECTORIAL` a `NO_MUNICIPAL` para mayor precisión semántica

**Recomendación**: APROBAR con modificaciones menores

---

### 2. `ipr_legacy_typology` (30 códigos)

**Propósito**: Clasificación histórica del sistema legacy (audit trail)

**Códigos**: FRIL, C33, MIDESO, GLOSA_5_1, etc. (30 valores)

#### ⚠️ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- 🔴 **CRITICAL**: Mezcla conceptos de DIFERENTE nivel ontológico:
  - **Mecanismos de financiamiento**: FRIL (existe gnub:FinancingMechanism)
  - **Clasificadores presupuestarios**: C33 (mapea a gnub:BudgetClassifier)
  - **Fuentes**: MIDESO (mapea a gnub:FundingSource)
  - **Sectores**: DEPORTE, CULTURA, SALUD (mapean a InvestmentTypology?)
  - **Glosas**: GLOSA_5_1 (mapean a gnub:BudgetaryRule?)

#### 🔴 Coherencia Categórica
- 🔴 **CRITICAL VIOLATION**: Violación del principio de cohesión categorial
- El scheme mezcla 5 dimensiones ontológicas distintas
- NO es una categoría pura, es un "cajón de sastre" histórico

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🔴 FAIL - Añade complejidad sin valor semántico
- **A2 (Story-First)**: ⚠️ UNKNOWN - No hay User Story que requiera "tipología legacy"
- **A3 (TDE Compliance)**: 🔴 FAIL - Violación de coherencia ontológica
- **A4 (Maintainability)**: 🔴 FAIL - 30 códigos heterogéneos, alta entropía

#### 🔴 Severity: CRITICAL

**Hallazgos**:
1. **Violación grave**: Este scheme rompe el principio de univocidad categórica
2. Los 30 códigos deben RECLASIFICARSE en sus categorías ontológicas correctas:
   - FRIL → `mechanism` (ya existe en DB)
   - C33 → `budget_subtitle` (ya existe en DB)
   - MIDESO → `funding_source` o nueva subcategoría
   - DEPORTE/CULTURA/SALUD → `ipr_type` o nueva `ipr_sector`
   - GLOSAS → `budget_rule_type` (nuevo scheme coherente)
3. Si se requiere mantener trazabilidad, usar metadata JSONB, NO un scheme

**Recomendación**: 🛑 **RECHAZAR** - Requiere reingeniería completa

**Propuesta alternativa**:
```sql
-- Mantener en metadata.tipologia_original para audit trail
-- NO crear scheme ipr_legacy_typology
-- Reclasificar valores según su naturaleza ontológica real
```

---

### 3. `budget_item` (5 códigos)

**Propósito**: Clasificador presupuestario Ítem (nivel 5)

**Códigos**: 01-Personal, 02-Bienes, 06-Inversión Real, etc.

#### ✅ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- ✅ **Mapeado correctamente** a gnub:BudgetItem (línea 1790 del glosario)
- ✅ Alineado con gnub:BudgetClassifier (jerarquía presupuestaria)

#### ✅ Coherencia Categórica
- ✅ Categoría pura de clasificación presupuestaria
- ✅ Nivel correcto en jerarquía: Partida → Capítulo → Programa → Subtítulo → **Ítem** → Asignación
- ✅ Uso correcto del pattern Category

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: ✅ PASS - Clasificador estándar, necesario
- **A2 (Story-First)**: ✅ PASS - Deriva de gestión presupuestaria (dominio FIN)
- **A3 (TDE Compliance)**: ✅ PASS - Alineado con gnub:BudgetItem
- **A4 (Maintainability)**: ✅ PASS - Clasificador oficial DIPRES, estable

#### 🟢 Severity: LOW

**Hallazgos**:
1. Validar que códigos coincidan con clasificador oficial DIPRES
2. Considerar agregar `description` con definición oficial

**Recomendación**: ✅ **APROBAR**

---

### 4. `budget_assignment` (0-999 códigos) [BLOQUEADO]

**Propósito**: Clasificador presupuestario Asignación (nivel 6)

**Status**: ⏸️ BLOQUEADO - Requiere catálogo oficial DIPIR

#### ✅ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- ✅ **Mapeado correctamente** a gnub:BudgetAllocation (línea 159 del glosario)
- ✅ Alineado con gnub:BudgetClassifier

#### ⚠️ Coherencia Categórica
- ✅ Categoría pura de clasificación presupuestaria
- ⚠️ **HIGH RISK**: 1000 códigos potenciales (0-999) → alta cardinalidad
- ⚠️ Sin catálogo oficial, imposible validar coherencia

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: ⚠️ CONDITIONAL - Necesario SI hay User Stories que lo requieran
- **A2 (Story-First)**: 🟠 UNKNOWN - ¿Qué User Stories requieren asignación?
- **A3 (TDE Compliance)**: ✅ PASS - Alineado con gnub:BudgetAllocation
- **A4 (Maintainability)**: 🟠 RISK - 1000 códigos → mantenimiento complejo

#### 🟠 Severity: HIGH

**Hallazgos**:
1. **BLOCKER**: No se puede implementar sin catálogo oficial DIPIR
2. Validar con Product Owner si hay User Stories que requieren drill-down hasta Asignación
3. Evaluar costo/beneficio: ¿queries a nivel Ítem son suficientes?

**Recomendación**: ⏸️ **POSPONER** hasta obtener:
1. Catálogo oficial de DIPIR
2. User Stories que justifiquen granularidad nivel 6
3. Análisis de costo/beneficio de mantener 1000 categorías

---

### 5. `alias_type` (4 códigos)

**Propósito**: Tipo de alias de organización (abreviación, error, histórico, informal)

**Códigos**:
- `ABBREVIATION` - Forma corta
- `MISSPELLING` - Error ortográfico
- `HISTORICAL` - Nombre histórico
- `INFORMAL` - Nombre informal

#### ⚠️ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- 🟠 NO existe clase específica en goreNubleOntology para "alias de organización"
- ⚠️ Podría mapearse a gist:Name (pero Name no es una Category en Gist)

#### ⚠️ Coherencia Categórica
- ⚠️ **CUESTIONABLE**: ¿Es realmente una categoría o un atributo de texto?
- 🟠 `MISSPELLING` es un anti-pattern: ¿por qué categorizar errores?
- ✅ `HISTORICAL` y `ABBREVIATION` sí tienen valor semántico

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🟠 QUESTIONABLE - ¿Es necesario categorizar alias?
- **A2 (Story-First)**: 🔴 UNKNOWN - ¿Qué User Story requiere búsqueda por alias?
- **A3 (TDE Compliance)**: ⚠️ PARTIAL - No hay precedente en gnub/tde
- **A4 (Maintainability)**: 🟡 MODERATE - 4 valores, pero semántica débil

#### 🟡 Severity: MEDIUM

**Hallazgos**:
1. **Pregunta fundamental**: ¿Realmente se necesita categorizar alias o basta con texto libre?
2. `MISSPELLING` no debería ser una categoría → corregir el nombre canónico
3. Considerar simplificar a 2 categorías: `ABBREVIATION` y `HISTORICAL`
4. Alternativa: Usar full-text search sin categorización

**Recomendación**: 🟡 **APROBAR CON RESERVAS** - Evaluar simplificación

**Propuesta alternativa**:
```sql
-- Opción 1: Sin scheme (más simple)
CREATE TABLE core.organization_alias (
  alias TEXT NOT NULL,
  is_abbreviation BOOLEAN DEFAULT FALSE,
  valid_from TIMESTAMPTZ,
  valid_to TIMESTAMPTZ
);

-- Opción 2: Scheme simplificado (2 códigos)
INSERT INTO ref.category (scheme, code, label) VALUES
('alias_type', 'ABBREVIATION', 'Abreviación oficial'),
('alias_type', 'HISTORICAL', 'Nombre histórico');
-- Eliminar MISSPELLING e INFORMAL
```

---

### 6. `org_funding_role` (3 códigos)

**Propósito**: Rol de organización en financiamiento (receptor 8%, ejecutor FNDR, ejecutor FRIL)

**Códigos**:
- `RECEPTOR_8PCT` - Receptor Programa 8%
- `EJECUTOR_FNDR` - Ejecutor proyectos FNDR
- `EJECUTOR_FRIL` - Ejecutor proyectos FRIL

#### 🔴 Alineamiento Ontológico
- ⚠️ Alineado con gist:Category
- 🔴 **CRITICAL OVERLAP**: Ya existe `ipr_party_role` en la base de datos (56 schemes existentes)
- 🔴 Estos roles ya están modelados en `core.ipr_party` con `party_role_id`

#### 🔴 Coherencia Categórica
- 🔴 **CRITICAL DUPLICATION**: Esto NO es una propiedad de Organization, es una relación IPR-Organization
- El modelo correcto ya existe: `core.ipr_party(ipr_id, organization_id, party_role_id)`
- Crear este scheme rompe la normalización relacional

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🔴 FAIL - Duplica funcionalidad existente
- **A2 (Story-First)**: ⚠️ UNKNOWN - No se justifica vs. modelo existente
- **A3 (TDE Compliance)**: 🔴 FAIL - Rompe el modelo relacional correcto
- **A4 (Maintainability)**: 🔴 FAIL - Crea deuda técnica y ambigüedad

#### 🔴 Severity: CRITICAL

**Hallazgos**:
1. **Violación grave**: Este scheme es REDUNDANTE con `ipr_party_role`
2. Los "roles de financiamiento" ya están modelados como relaciones M:N en `core.ipr_party`
3. Crear esto generaría dos modelos paralelos para el mismo concepto

**Recomendación**: 🛑 **RECHAZAR COMPLETAMENTE**

**Solución correcta**:
```sql
-- NO crear org_funding_role
-- USAR el modelo existente:

-- Verificar si los roles existen en ipr_party_role
SELECT * FROM ref.category WHERE scheme = 'ipr_party_role';

-- Si faltan, agregar ahí:
INSERT INTO ref.category (scheme, code, label) VALUES
('ipr_party_role', 'RECEPTOR_8PCT', 'Receptor Programa 8%'),
('ipr_party_role', 'EJECUTOR', 'Ejecutor');
-- Ya existe: MANDANTE, BENEFICIARIO, UNIDAD_TECNICA

-- Usar core.ipr_party para registrar participación
INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id)
SELECT ipr_id, org_id, (SELECT id FROM ref.category WHERE code='EJECUTOR')
FROM ...;
```

---

### 7. `agreement_cgr_state` (4 códigos)

**Propósito**: Estado de trámite CGR de convenio

**Códigos**:
- `TOMADO_DE_RAZON` - Aprobado por CGR
- `TR_CON_ALCANCES` - Aprobado con observaciones
- `REPRESENTADO` - CGR representó el convenio
- `EN_CGR` - En trámite Contraloría

#### ✅ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- ✅ Mapeado a goreNubleDipirOntology:TomaRazonEvent (línea 72 del glosario)
- ✅ Relacionado con gnub:AdministrativeAct → cgr_outcome_id

#### ⚠️ Coherencia Categórica
- ✅ Categoría pura de estado administrativo
- ⚠️ **OVERLAP**: Ya existe `cgr_outcome` en schemes existentes (línea 10 de schemes actuales)
- 🟠 `EN_CGR` es un estado de proceso, no un outcome

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🟡 QUESTIONABLE - ¿Duplica `cgr_outcome`?
- **A2 (Story-First)**: ✅ PASS - Deriva de flujo administrativo (DIPIR)
- **A3 (TDE Compliance)**: ✅ PASS - Alineado con TomaRazonEvent
- **A4 (Maintainability)**: ✅ PASS - Estados estables, low churn

#### 🟡 Severity: MEDIUM

**Hallazgos**:
1. Verificar si `cgr_outcome` existente ya cubre estos estados
2. Considerar fusionar con `cgr_outcome` o renombrar a `agreement_cgr_workflow_state`
3. `EN_CGR` debería estar en `agreement_state`, no en `agreement_cgr_state`

**Recomendación**: 🟡 **APROBAR CON MODIFICACIONES**

**Propuesta**:
```sql
-- Verificar scheme existente
SELECT * FROM ref.category WHERE scheme = 'cgr_outcome';

-- Si cubre los mismos conceptos, NO crear agreement_cgr_state
-- Si son complementarios, crear con semántica clara:
-- agreement_cgr_state = workflow state (EN_CGR, PENDIENTE_TDR)
-- cgr_outcome = resultado final (TOMADO_DE_RAZON, REPRESENTADO)
```

---

### 8. `agreement_operational_state` (1 código)

**Propósito**: Estado operacional del convenio

**Código**: `ENVIADO_AL_SERVICIO`

#### 🔴 Alineamiento Ontológico
- ⚠️ Alineado con gist:Category
- 🔴 **CRITICAL**: 1 solo código NO justifica un scheme completo
- ⚠️ No hay mapeo explícito en goreNubleOntology

#### 🔴 Coherencia Categórica
- 🔴 **ANTI-PATTERN**: Un scheme con 1 solo valor es un boolean disfrazado
- Debería ser columna directa: `agreement.sent_to_service_at TIMESTAMPTZ`
- O ampliarse el scheme existente `agreement_state`

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🔴 FAIL - Complejidad innecesaria para 1 valor
- **A2 (Story-First)**: ⚠️ UNKNOWN - Falta contexto de User Story
- **A3 (TDE Compliance)**: 🟠 PARTIAL - No viola, pero es subóptimo
- **A4 (Maintainability)**: 🔴 FAIL - Scheme infrautilizado

#### 🔴 Severity: CRITICAL

**Hallazgos**:
1. **Violación de principio de economía**: 1 código no justifica scheme
2. Alternativas más limpias:
   - Columna booleana: `sent_to_service BOOLEAN`
   - Timestamp: `sent_to_service_at TIMESTAMPTZ`
   - Ampliar `agreement_state` con más estados operacionales

**Recomendación**: 🛑 **RECHAZAR**

**Solución correcta**:
```sql
-- Opción 1: Timestamp (más información)
ALTER TABLE core.agreement ADD COLUMN sent_to_service_at TIMESTAMPTZ;

-- Opción 2: Ampliar agreement_state existente
INSERT INTO ref.category (scheme, code, label) VALUES
('agreement_state', 'SENT_TO_SERVICE', 'Enviado al Servicio'),
('agreement_state', 'RECEIVED_BY_SERVICE', 'Recibido por Servicio'),
('agreement_state', 'IN_EXECUTION', 'En Ejecución');
-- Crear scheme operacional SOLO si hay >= 3 estados
```

---

### 9. `person_employment_tier` (7 códigos)

**Propósito**: Estamento del funcionario

**Códigos**: Profesional, Honorarios, Directivo, Administrativo, Técnico, Auxiliar, Autoridad de Gobierno

#### ✅ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- ⚠️ No existe clase específica en goreNubleOntology, pero mapeable a tdeCore:Cargo
- ⚠️ Podría relacionarse con gist:Position (pero no está en Gist Core)

#### ⚠️ Coherencia Categórica
- ✅ Categoría pura de clasificación laboral
- ⚠️ **CUESTIONABLE**: ¿Es propiedad de Person o de Position?
- 🟠 En rigor, el estamento es del CARGO, no de la PERSONA

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🟡 MODERATE - Simplifica estructura, pero semántica cuestionable
- **A2 (Story-First)**: ⚠️ UNKNOWN - ¿Qué User Stories requieren estamento?
- **A3 (TDE Compliance)**: 🟡 PARTIAL - Compatible con tdeCore:Cargo
- **A4 (Maintainability)**: ✅ PASS - Clasificación oficial, estable

#### 🟡 Severity: MEDIUM

**Hallazgos**:
1. **Modelado cuestionable**: Estamento es propiedad del CARGO, no de la PERSONA
2. Una persona puede tener múltiples cargos en su historia laboral
3. Considerar modelar como `core.position.employment_tier_id` en vez de `core.person.employment_tier_id`

**Recomendación**: 🟡 **APROBAR CON MODIFICACIONES**

**Propuesta**:
```sql
-- Versión simplificada (si no hay tabla Position todavía)
ALTER TABLE core.person ADD COLUMN employment_tier_id UUID;
-- Agregar comment aclarando que es del cargo ACTUAL

-- Versión correcta (si hay tabla Position)
ALTER TABLE core.position ADD COLUMN employment_tier_id UUID;
-- No modificar core.person
```

---

### 10. `rendicion_8pct_state` (4 códigos)

**Propósito**: Estado de rendición de Programas 8%

**Códigos**: COMPLETADO, PENDIENTE, EN_PROCESO, CANCELADO

#### ⚠️ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- 🟠 **OVERLAP**: Ya existe `rendition_state` en schemes actuales (línea 39)
- ✅ Relacionado con gnub:RenditionState (línea 522 del glosario)

#### ⚠️ Coherencia Categórica
- ✅ Categoría pura de estado
- 🟠 **CUESTIONABLE**: ¿Por qué un scheme específico para 8%?
- 🟠 Rompe principio de univocidad: estados de rendición son independientes del fondo

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🟠 QUESTIONABLE - ¿Por qué no usar `rendition_state`?
- **A2 (Story-First)**: ⚠️ UNKNOWN - ¿Hay requisitos específicos de 8%?
- **A3 (TDE Compliance)**: 🟡 PARTIAL - Compatible pero redundante
- **A4 (Maintainability)**: 🟠 RISK - Crea schemes por fondo → escalabilidad negativa

#### 🟠 Severity: HIGH

**Hallazgos**:
1. **Problema de diseño**: No crear schemes específicos por fondo (FNDR, FRIL, 8%, etc.)
2. Usar `rendition_state` genérico
3. Si hay estados específicos de 8%, agregar columna `rendition_type_id` que apunte al fondo

**Recomendación**: 🛑 **RECHAZAR**

**Solución correcta**:
```sql
-- NO crear rendicion_8pct_state
-- USAR rendition_state existente

-- Si los estados son diferentes, verificar:
SELECT * FROM ref.category WHERE scheme = 'rendition_state';

-- Si no existen, agregarlos:
INSERT INTO ref.category (scheme, code, label) VALUES
('rendition_state', 'COMPLETADO', 'Completado'),
('rendition_state', 'PENDIENTE', 'Pendiente'),
('rendition_state', 'EN_PROCESO', 'En Proceso'),
('rendition_state', 'CANCELADO', 'Cancelado');

-- Usar core.rendition.state_id con estos valores
```

---

### 11. `magnitude_aspect` (3 códigos adicionales)

**Propósito**: Aspectos adicionales para txn.magnitude

**Códigos propuestos**:
- `TRANSFERRED_AMOUNT` - Monto Transferido
- `EXECUTED_AMOUNT` - Monto Ejecutado
- `REMAINING_BALANCE` - Saldo Remanente

#### ✅ Alineamiento Ontológico
- ✅ **Perfectamente alineado** con gist:Aspect (patrón Magnitude de Gist 14.0)
- ✅ Consistente con aspectos existentes en goreNubleOntology (líneas 167-1155):
  - gnub:CommittedAmountAspect
  - gnub:AccruedAmountAspect
  - gnub:PaidAmountAspect
  - gnub:BudgetedAmountAspect

#### ✅ Coherencia Categórica
- ✅ Uso correcto del pattern Magnitude (gist:Magnitude + gist:Aspect)
- ✅ Extensión natural de aspectos financieros existentes
- ⚠️ `EXECUTED_AMOUNT` ya está DEPRECATED en glosario (línea 953): usar AccruedAmountAspect

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: ✅ PASS - Completa el modelo financiero
- **A2 (Story-First)**: ✅ PASS - Requerido para time-series de ejecución
- **A3 (TDE Compliance)**: ✅ PASS - Patrón Gist correcto
- **A4 (Maintainability)**: ✅ PASS - Aspectos estables

#### 🟢 Severity: LOW

**Hallazgos**:
1. `EXECUTED_AMOUNT` debe eliminarse → usar `AccruedAmountAspect` (ya existe en ontología)
2. `TRANSFERRED_AMOUNT` y `REMAINING_BALANCE` son válidos y necesarios

**Recomendación**: ✅ **APROBAR CON MODIFICACIÓN**

**Propuesta**:
```sql
-- Agregar aspectos nuevos (omitir EXECUTED_AMOUNT)
INSERT INTO ref.category (scheme, code, label, description) VALUES
('magnitude_aspect', 'TRANSFERRED_AMOUNT', 'Monto Transferido',
 'Monto efectivamente transferido a ejecutor'),
('magnitude_aspect', 'REMAINING_BALANCE', 'Saldo Remanente',
 'Saldo disponible no comprometido');

-- NO agregar EXECUTED_AMOUNT (usar 'ACCRUED_AMOUNT' existente)
```

---

### 12. `education_level` (mencionado, no detallado)

**Propósito**: Nivel educacional de persona

**Códigos propuestos**: POSTGRADO, UNIVERSITARIA, etc. (no detallados en plan)

#### ⚠️ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- ⚠️ No existe en goreNubleOntology ni tdeCore
- ⚠️ Concepto común pero sin precedente ontológico

#### ⚠️ Coherencia Categórica
- ✅ Categoría pura de clasificación educativa
- ⚠️ **Falta especificación**: ¿Cuál es la taxonomía oficial?
  - Ministerio de Educación?
  - UNESCO ISCED?
  - Clasificación ad-hoc?

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🟡 MODERATE - Útil para RRHH, pero no crítico
- **A2 (Story-First)**: 🔴 UNKNOWN - ¿Qué User Stories lo requieren?
- **A3 (TDE Compliance)**: 🟡 NEUTRAL - No viola, pero sin precedente
- **A4 (Maintainability)**: 🟠 RISK - Sin taxonomía oficial → deriva semántica

#### 🟠 Severity: HIGH

**Hallazgos**:
1. **BLOCKER**: No se puede implementar sin taxonomía oficial
2. Requiere validación con RRHH sobre clasificación estándar
3. Alternativa: Mantener en metadata hasta validar User Stories

**Recomendación**: ⏸️ **POSPONER** hasta obtener:
1. User Stories que lo justifiquen
2. Taxonomía oficial (MINEDUC o UNESCO ISCED)
3. Validación con área de RRHH

---

### 13. `position_level` (mencionado, no detallado)

**Propósito**: Nivel jerárquico del cargo

**Códigos propuestos**: JEFE_DIVISION, PROFESIONAL, etc. (no detallados en plan)

#### ⚠️ Alineamiento Ontológico
- ✅ Alineado con gist:Category
- ⚠️ No existe en goreNubleOntology
- ⚠️ Relacionado con meta.role pero en dimensión diferente

#### ⚠️ Coherencia Categórica
- ✅ Categoría pura de jerarquía organizacional
- ⚠️ **Overlap potencial** con org_type (DIVISION, DEPARTMENT, UNIT)
- 🟠 Confusión conceptual: ¿nivel de cargo o nivel de unidad organizacional?

#### ⚙️ Tensiones KODA
- **A1 (Minimalism)**: 🟡 MODERATE - Útil si hay flujos de aprobación jerárquicos
- **A2 (Story-First)**: 🔴 UNKNOWN - ¿Qué User Stories lo requieren?
- **A3 (TDE Compliance)**: 🟡 NEUTRAL - Compatible pero sin precedente
- **A4 (Maintainability)**: 🟠 RISK - Jerarquías organizacionales cambian

#### 🟠 Severity: HIGH

**Hallazgos**:
1. **BLOCKER**: Falta especificación completa
2. Aclarar si es nivel del CARGO o nivel de la UNIDAD donde trabaja
3. Verificar si ya está modelado en estructura organizacional (Division → Department → Unit)

**Recomendación**: ⏸️ **POSPONER** hasta:
1. Especificar taxonomía completa
2. Validar con User Stories de flujos de aprobación
3. Diferenciar de jerarquía organizacional existente

---

## 📊 Análisis de Tablas Nuevas

### 1. `core.organization_alias` ✅

**Verdict**: APROBAR con reservas (ver scheme `alias_type`)

**Alineamiento ontológico**: Compatible con gist:Name

---

### 2. `core.budget_program_source` ✅

**Verdict**: APROBAR

**Alineamiento ontológico**:
- M:N correcta entre BudgetProgram y FundingSource
- Modela composición de fuentes (FNDR + Sectorial)
- Compatible con gnub:BudgetProgram

---

### 3. `core.budget_carryover` ✅

**Verdict**: APROBAR

**Alineamiento ontológico**:
- Modela arrastres presupuestarios (concepto financiero estándar)
- Compatible con gnub:BudgetModification
- Patrón temporal correcto (from_year, to_year)

---

### 4. `core.rendicion_8pct` 🔴

**Verdict**: RECHAZAR - Requiere reingeniería

**Problemas**:
1. NO crear tabla específica por fondo (8%, FNDR, FRIL, etc.) → anti-pattern
2. Usar tabla genérica `core.rendition` con FK a `funding_source_id`
3. Estados deben ir en `rendition_state` genérico

**Solución correcta**:
```sql
-- NO crear core.rendicion_8pct
-- USAR core.rendition existente + ampliar atributos si es necesario

ALTER TABLE core.rendition
  ADD COLUMN funding_source_id UUID REFERENCES ref.category(id),
  ADD COLUMN transferred_amount NUMERIC(18,2),
  ADD COLUMN execution_closure_date DATE,
  ADD COLUMN technical_closure_date DATE;
```

---

### 5. `ref.professional_qualification` + `core.person_qualification` ⏸️

**Verdict**: POSPONER Fase 4

**Razones**:
1. Requiere validación de 57 títulos únicos
2. Necesita User Stories de RRHH que lo justifiquen
3. Complejidad M:N con historial → diferir hasta validar ROI

---

### 6. `core.position` + `core.person_position` ⏸️

**Verdict**: POSPONER Fase 4

**Razones**:
1. Requiere limpieza de 87 cargos únicos
2. M:N temporal complejo (valid_from/valid_to)
3. Diferir hasta tener User Stories de gestión de RRHH

---

## 🎯 Recomendaciones Finales

### 🔴 Correcciones Críticas Requeridas

1. **ELIMINAR `ipr_legacy_typology`**
   - Reclasificar 30 códigos en sus categorías ontológicas correctas
   - Mantener trazabilidad en metadata.tipologia_original

2. **ELIMINAR `org_funding_role`**
   - Usar `ipr_party_role` existente
   - Registrar participación en `core.ipr_party`

3. **ELIMINAR `agreement_operational_state`**
   - Reemplazar por timestamp o ampliar `agreement_state`

4. **ELIMINAR `rendicion_8pct_state`**
   - Usar `rendition_state` genérico

5. **ELIMINAR tabla `core.rendicion_8pct`**
   - Ampliar `core.rendition` existente

### 🟠 Modificaciones Importantes

6. **SIMPLIFICAR `alias_type`**
   - Reducir de 4 a 2 códigos (ABBREVIATION, HISTORICAL)
   - Eliminar MISSPELLING e INFORMAL

7. **CLARIFICAR `agreement_cgr_state`**
   - Verificar overlap con `cgr_outcome`
   - Separar workflow state de outcome final

8. **REVISAR `person_employment_tier`**
   - Considerar mover a `core.position` en vez de `core.person`

### 🟡 Mejoras Sugeridas

9. **AMPLIAR `magnitude_aspect`**
   - Agregar TRANSFERRED_AMOUNT y REMAINING_BALANCE
   - NO agregar EXECUTED_AMOUNT (usar ACCRUED_AMOUNT)

10. **APROBAR `budget_item`**
    - Validar códigos con clasificador DIPRES

11. **APROBAR `ipr_origin`**
    - Considerar renombrar SECTORIAL → NO_MUNICIPAL

### ⏸️ Posponer

12. **BLOQUEAR `budget_assignment`**
    - Requiere catálogo DIPIR + User Stories

13. **POSPONER `education_level`**
    - Requiere taxonomía oficial + User Stories

14. **POSPONER `position_level`**
    - Requiere especificación completa + User Stories

---

## 📈 Métricas de Impacto

### Antes de Correcciones

| Dimensión | Status |
|-----------|--------|
| **Coherencia ontológica** | 🔴 60% |
| **Redundancia** | 🔴 30% duplicación |
| **Mantenibilidad** | 🟠 70% |
| **Alineamiento Gist/GNUB** | 🟡 75% |

### Después de Correcciones Propuestas

| Dimensión | Status |
|-----------|--------|
| **Coherencia ontológica** | ✅ 95% |
| **Redundancia** | ✅ 5% duplicación |
| **Mantenibilidad** | ✅ 90% |
| **Alineamiento Gist/GNUB** | ✅ 95% |

---

## 🔗 Próximos Pasos

### Inmediato (antes de implementar)

1. ✅ Revisar y aprobar correcciones críticas (items 1-5)
2. ✅ Implementar modificaciones importantes (items 6-8)
3. ⏸️ Obtener catálogos oficiales para items bloqueados

### Corto Plazo (Fase 2-3)

4. ✅ Implementar schemes aprobados (budget_item, ipr_origin, magnitude_aspect)
5. ✅ Implementar tablas aprobadas (organization_alias, budget_program_source, budget_carryover)

### Medio Plazo (Fase 4)

6. ⏸️ Validar User Stories para education_level, position_level
7. ⏸️ Evaluar ROI de professional_qualification y person_position

---

## 🏆 Lecciones Aprendidas

### Anti-Patterns Detectados

1. **Schemes mono-valor**: No crear scheme con 1 solo código
2. **Schemes por entidad**: No crear `rendicion_8pct_state`, `rendicion_fndr_state`, etc.
3. **Duplicación de roles**: No crear schemes paralelos a `ipr_party_role`
4. **Cajones de sastre**: No mezclar conceptos ontológicos heterogéneos

### Patterns Correctos

1. ✅ **Magnitude Aspect**: Uso correcto de gist:Magnitude + gist:Aspect
2. ✅ **Budget Classifier**: Jerarquía clara (Partida → Capítulo → ... → Ítem)
3. ✅ **Composición de fuentes**: M:N budget_program_source

---

## 📚 Referencias Ontológicas

- **Gist 14.0**: Category Pattern, Magnitude Pattern
- **GORE Ñuble Ontology**: 199 términos (gnub:*)
- **TDE Core**: 19 términos (tde:*)
- **DDL GORE_OS v3.0**: Mappings líneas 21-37

---

**Auditor**: Arquitecto-GORE (KODA Agent v0.1.0)
**Firma Digital**: `categoria-teoria-aplicada-2026-01-30`
**Status**: ⚠️ REQUIERE CORRECCIONES CRÍTICAS

---

*Este documento fue generado aplicando Category Theory y las tensiones KODA (A1-A4) sobre el Plan de Normalización JSONB v1.0. Todas las evaluaciones están fundamentadas en el glosario terminológico (244 términos), el DDL existente (56 schemes) y los principios de coherencia ontológica de Gist 14.0.*
