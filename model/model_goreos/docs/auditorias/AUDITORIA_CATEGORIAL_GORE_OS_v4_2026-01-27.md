# Auditoria Categorial - GORE_OS v3.0 (model/model_goreos)

Fecha: 2026-01-27  
Auditor: Arquitecto Categorico (Teoria de Categorias aplicada a dominios de datos)  
Directorio auditado: model/model_goreos  
Artefactos: goreos_ddl.sql, goreos_triggers.sql, goreos_triggers_remediation.sql, goreos_indexes.sql, seeds *.sql, docs/*.md  

Nota KB: catalogo fxsl resuelto. URN no encontrado en catalogo: urn:knowledge:fxsl:mbt:tensiones:1.0.0 (no usado).

---

## 0) Clasificacion DIK y modo de auditoria

- INFORMATION (dominante): DDL, indices, docs como esquema ejecutable.
- KNOWLEDGE (embebido): triggers, decisiones de diseno, invariantes declaradas y remediacion.
- Modos: STATIC (estructura + referencias + constraints), TEMPORAL (particiones + versionado), BEHAVIORAL (triggers + transiciones), DAL-INTEGRATED (contratos API/ETL, no presentes).

---

## 1) Hechos observables (inventario minimo)

- Tablas: 50 (meta=5, ref=3, core=40, txn=2). Evidencia: goreos_ddl.sql:1598-1601.
- Particiones: txn.event (12 mensuales + default) y txn.magnitude (4 trimestrales + default). Evidencia: goreos_ddl.sql:1449-1476 y 1494-1503.
- Triggers activos en core: 4 (history, commitment_history, ipr_problem_flag, budget_program_current). Evidencia: goreos_triggers.sql:359-382 y resumen 452-454.
- Triggers de remediacion categorial existen pero estan fuera del DDL base. Evidencia: goreos_triggers_remediation.sql:1-317.
- Orden de instalacion recomendado incluye remediacion y indices. Evidencia: README.md:73-92.

---

## 2) Hallazgos por dimension

### 2.1 STATIC - Estructura

**HIGH - STR-001 (BROKEN-DIAGRAM): doble codificacion de jerarquia en ref.category sin invariante en el DDL base**

- Evidencia: ref.category parent_id + parent_code en goreos_ddl.sql:244-245.
- Impacto: deriva silenciosa entre ambos ejes; el diagrama deja de conmutar.
- Recomendacion: definir canonico (parent_id o parent_code) y forzar sincronizacion. Existe solucion en goreos_triggers_remediation.sql:217-245, pero debe ser obligatoria en despliegue.

**MEDIUM - STR-002 (REQUIRES_ACYCLIC): jerarquias sin garantia de aciclicidad**

- Evidencia: parent_id en ref.category, core.organization, core.territory, core.work_item (goreos_ddl.sql:244-246, 355-357, 471-476, 1288-1289).
- Impacto: ciclos rompen closures, reportes y agregaciones.
- Recomendacion: triggers de deteccion de ciclos (CTE) o closure table/ltree para jerarquias criticas.

**MEDIUM - STR-003 (AD-HOC-CONSTRUCTION): metadata JSONB sin contrato de tipo en la mayoria de tablas**

- Evidencia: metadata JSONB DEFAULT '{}'::jsonb en multiples tablas, sin CHECK global (p.ej. goreos_ddl.sql:258, 486, 649, 1383).
- Impacto: metadata puede ser array/string; indices GIN menos previsibles.
- Recomendacion: CHECK jsonb_typeof(metadata)='object' para todas las tablas (solo existe para ref.category en remediation: goreos_triggers_remediation.sql:300-305).

**MEDIUM - STR-004 (NON-DISJOINT-COPRODUCT): ipr_mechanism como suma de variantes sin restricciones**

- Evidencia: core.ipr_mechanism mezcla atributos de SNI/C33/FRIL/FRPD/SUBV8 sin discriminador ni CHECK (goreos_ddl.sql:661-699). El mecanismo vive en core.ipr.mechanism_id (goreos_ddl.sql:621-658).
- Impacto: combinaciones invalidas (atributos de mecanismos incompatibles) y perdida de semantica.
- Recomendacion: modelar coproducto con tablas por variante o CHECKs condicionados por mechanism_id.

**MEDIUM - STR-005 (COPRODUCTO NO CONTROLADO): origen de work_item no restringido**

- Evidencia: work_item admite story_id, commitment_id, problem_id, ipr_id, agreement_id, resolution_id sin exclusividad (goreos_ddl.sql:1296-1306).
- Impacto: un work_item puede nacer de multiples fuentes, rompiendo interpretacion de origen.
- Recomendacion: constraint XOR (exactamente una fuente) o tabla de origen con type+id (sum type controlado).

**LOW - STR-006 (SUBTIPO DEBIL): vehicle no exige inventory_item_id**

- Evidencia: core.vehicle.inventory_item_id no es NOT NULL (goreos_ddl.sql:1042-1045).
- Impacto: vehiculo sin activo base rompe especializacion.
- Recomendacion: NOT NULL o trigger que cree inventory_item automaticamente.

### 2.2 STATIC - Referencial y Semantica

**HIGH - REF-001 (NON-FUNCTORIAL): FKs a ref.category sin validacion de scheme en el DDL base**

- Evidencia: multiples columnas a ref.category (ej. core.ipr.mcd_phase_id, status_id, mechanism_id) en goreos_ddl.sql:621-658.
- Impacto: integridad referencial sin integridad semantica (se puede insertar un category de scheme incorrecto).
- Recomendacion: activar triggers de validacion de scheme (goreos_triggers_remediation.sql:80-210) o migrar a categorias tipadas por scheme.

**HIGH - REF-002 (DANGLING-REF): referencias polimorficas sin FK**

- Evidencia: subject_type/subject_id en core.alert y txn.event (goreos_ddl.sql:1360-1366, 1422-1424); target_type/target_id en core.agenda_item_context (goreos_ddl.sql:1268-1272).
- Impacto: dangling refs y joins manuales; se pierde verificabilidad.
- Recomendacion: registro global de sujetos (tabla core.subject) o FKs por tipo via tablas puente.

**MEDIUM - REF-003 (UNCONTROLLED-SEMANTICS): subject_type no referenciado a meta.entity**

- Evidencia: subject_type como VARCHAR libre (goreos_ddl.sql:1364-1365, 1423-1424, 1481-1482).
- Impacto: codigos inconsistentes por typo o cambios de naming.
- Recomendacion: FK a meta.entity.code o ENUM estable.

**LOW - REF-004 (WEAK-ROLE-CONSTRAINT): ref.actor ORGANIZATIONAL no exige organization_id**

- Evidencia: organization_id es opcional y constraint chk_actor_type no lo exige (goreos_ddl.sql:288-310).
- Impacto: actor organizacional sin organizacion concreta.
- Recomendacion: CHECK (agent_type != 'ORGANIZATIONAL' OR organization_id IS NOT NULL).

### 2.3 STATIC - Completitud / Invariantes

**HIGH - CPL-001 (MISSING-PROC): transiciones de estado definidas pero enforcement fuera del DDL base**

- Evidencia: valid_transitions en ref.category (goreos_ddl.sql:248-249) y triggers en remediation (goreos_triggers_remediation.sql:12-77).
- Impacto: si remediation no se aplica, las maquinas de estado quedan como documentacion.
- Recomendacion: mover triggers de transicion al pipeline base o activar por default en entornos productivos.

**HIGH - CPL-002 (MISSING-PROC): validacion de scheme depende de remediation**

- Evidencia: fn_validate_category_scheme existe pero sin triggers en el DDL (goreos_ddl.sql:1547-1568); triggers se definen solo en remediation (goreos_triggers_remediation.sql:80-210).
- Impacto: semantica de categorias no garantizada si el paso 6 se omite.
- Recomendacion: incluir triggers en el despliegue obligatorio o declarar precondicion de instalacion.

**MEDIUM - CPL-003 (POLICY-DRIFT): soft delete es politica de app, sin constraints de coherencia**

- Evidencia: columnas deleted_at/deleted_by_id en todas las tablas; triggers soft delete comentados (goreos_triggers.sql:404-419).
- Impacto: riesgo de estados parciales (deleted_at sin deleted_by_id).
- Recomendacion: CHECK (deleted_at IS NULL) = (deleted_by_id IS NULL) o triggers opcionales controlados por feature flag.

**LOW - CPL-004 (MISSING-PROC): created_by_id/updated_by_id no se autopueblan**

- Evidencia: set_current_user/get_current_user definidos pero no usados por triggers de auditoria (goreos_triggers.sql:425-447).
- Impacto: auditoria depende 100% de la aplicacion.
- Recomendacion: triggers genericos (BEFORE INSERT/UPDATE) para poblar *_by_id cuando app.current_user_id exista.

### 2.4 STATIC - Calidad y Constraints

**MEDIUM - QLT-001 (CONSTRAINT-GAP): fechas y montos sin checks basicos**

- Evidencia: core.agreement valid_from/valid_to sin check (goreos_ddl.sql:846-849); core.rendition period_start/period_end (goreos_ddl.sql:898-900); core.committee_member start_date/end_date (goreos_ddl.sql:941-943); core.session started_at/ended_at (goreos_ddl.sql:959-963); core.agreement_installment paid_amount sin limite vs amount (goreos_ddl.sql:875-880).
- Impacto: incoherencias temporales y financieras.
- Recomendacion: CHECKs de orden (start<=end) y montos (paid_amount <= amount; montos >= 0).

**LOW - QLT-002 (CASE-SENSITIVITY): email unico pero sensible a mayusculas**

- Evidencia: core.user.email UNIQUE (goreos_ddl.sql:401-408).
- Impacto: duplicados logicos (<Test@x.com> vs <test@x.com>).
- Recomendacion: CITEXT o UNIQUE sobre lower(email).

**LOW - QLT-003 (STRUCTURE): valid_transitions JSONB sin validacion de tipo**

- Evidencia: valid_transitions JSONB en ref.category (goreos_ddl.sql:248-249) sin CHECK.
- Impacto: puede guardar objeto/array invalido; rompe validacion de transiciones.
- Recomendacion: CHECK jsonb_typeof(valid_transitions)='array' y validacion de codigos.

### 2.5 TEMPORAL - Evolucion y Operacion

**HIGH - TMP-001 (TECH-DEBT): particiones fijadas a 2026 + default**

- Evidencia: particiones 2026 en txn.event y txn.magnitude (goreos_ddl.sql:1449-1503).
- Impacto: desde 2027 crece en _default; degradacion de performance y mantenimiento.
- Recomendacion: job anual o funcion create_partitions(year) y alertas preventivas.

**MEDIUM - TMP-002 (VERSION-CHAIN): DDL monolitico con DROP TYPE ... CASCADE**

- Evidencia: DDL inicia con DROP TYPE IF EXISTS ... CASCADE (goreos_ddl.sql:45-70).
- Impacto: no apto para migraciones incrementales; riesgo en entornos con datos.
- Recomendacion: cadena de migraciones versionadas (Flyway/Liquibase) con politicas no destructivas.

**LOW - TMP-003 (IDENTITY-SCOPE): PK compuesta en txn.event/txn.magnitude**

- Evidencia: PRIMARY KEY (id, occurred_at) y (id, as_of_date) (goreos_ddl.sql:1431-1433, 1489-1492).
- Impacto: consumidores pueden asumir id global unico y fallar en integraciones.
- Recomendacion: documentar invariante o usar PK global + UNIQUE por particion.

### 2.6 BEHAVIORAL - Triggers y Preservacion

**MEDIUM - BEH-001 (OPT-IN-CRITICAL): event sourcing desactivado por defecto**

- Evidencia: triggers a txn.event comentados (goreos_triggers.sql:383-402).
- Impacto: si se espera trazabilidad, no se obtiene.
- Recomendacion: definir politica clara por ambiente y activar donde compliance lo exija.

**MEDIUM - BEH-002 (RUNTIME-RISK): get_current_user() castea UUID sin validacion**

- Evidencia: get_current_user usa current_setting(... )::UUID (goreos_triggers.sql:436-442); version segura existe solo en remediation (goreos_triggers_remediation.sql:251-273).
- Impacto: errores en runtime si app.current_user_id es invalido.
- Recomendacion: usar get_current_user_safe en triggers y poblar current_user de forma defensiva.

**LOW - BEH-003 (BEHAVIOR-GAP): no hay triggers para validacion de estados en tablas adicionales**

- Evidencia: remediation cubre ipr, work_item, commitment, agreement, act, installment, file (goreos_triggers_remediation.sql:12-77) pero no otras tablas con status_id (p.ej. core.session_agreement, core.risk).
- Impacto: estados heterogeneos sin control uniforme.
- Recomendacion: completar cobertura o declarar explicitamente que esos estados son libres.

### 2.7 DAL / Integracion

**LOW - DAL-001 (TRACEABILITY-GAP): sin artefactos API derivados del esquema**

- Evidencia: no hay OpenAPI/GraphQL/JSON Schema generados en model/model_goreos.
- Impacto: riesgo de drift entre modelo y contratos de integracion.
- Recomendacion: generar artefactos a partir del esquema (funtor Schema->API) y versionarlos.

---

## 3) Oportunidades de mejora (priorizadas)

P0 (integridad inmediata)

- Hacer obligatoria la ejecucion de goreos_triggers_remediation.sql en todos los ambientes.
- Activar validacion de schemes y transiciones en tablas criticas (ipr, agreement, commitment, work_item).

P1 (semantica categorial)

- Introducir un registro global de sujetos (core.subject) y reemplazar subject_type/subject_id.
- Formalizar coproductos (work_item origen, ipr_mechanism variantes) con constraints.

P2 (calidad de datos)

- CHECKs basicos para fechas y montos; coherencia deleted_at/deleted_by_id.
- Validacion global de metadata JSONB como objeto.

P3 (operacion)

- Automatizar particiones y alertar sobre default partition.
- Adoptar migraciones versionadas; evitar DROP ... CASCADE en ambientes con datos.

P4 (integracion)

- Generar contratos API (OpenAPI/GraphQL) y data dictionary operativo desde el DDL.

---

## 4) Riesgos residuales

- Dependencia fuerte de ejecucion correcta del orden de instalacion; si se omite remediation, la semantica no se preserva.
- Referencias polimorficas sin FK son el mayor punto de posible deriva en integraciones.
- Particiones futuras sin automatizacion generan deuda operativa a 12 meses.

---

## 5) Cierre

El modelo es estructuralmente consistente y rico en semantica categorial, pero varias invariantes clave dependen de scripts externos (remediation) o de la aplicacion. La prioridad es convertir esas invariantes en garantias sistematicas para preservar conmutatividad y trazabilidad.
