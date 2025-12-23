# Reporte de Extracción Funcional: Legacy `para_titi` → `gore_os`

**Origen**: Proyecto Legacy `para_titi` (Sist. Gestión de Crisis IPR v4.1)
**Destino**: `gore_os` (Core System)
**Objetivo**: Replicación funcional categorial ("Dissección Molecular")

---

## 1. Visión General: El Modelo de "Crisis & Compromisos"

El núcleo de `para_titi` no es gestionar IPRs (eso lo hace el sistema base), sino gestionar la **atención** sobre esas IPRs. Funciona como una capa de "Metadatos Ejecutables" sobre la inversión.

### Las Moléculas Funcionales

Hemos identificado 4 moléculas funcionales principales que deben persistir e integrarse en `gore_os`:

1. **M1: Motor de Problemas (Crisis Engine)**: Detección, clasificación y ciclo de vida de nudos críticos.
2. **M2: Gestor de Compromisos (Task Force)**: Asignación de tareas operativas con plazos, alertas y verificación.
3. **M3: Radar de Alertas (Signal Detection)**: Reglas automáticas que escanean el estado de la inversión.
4. **M4: Vistas de Mando (Role-Based Dashboards)**: Agregaciones específicas por perfil.

---

## 2. Disección Molecular

### M1: Motor de Problemas (Crisis Engine)

*La entidad `ProblemaIPR` actúa como un "Ticket de Bloqueo" sobre la inversión.*

**Estructura de Datos (Átomo):**

* **Target**: `iniciativa_id` (Obligatorio) + `convenio_id` (Opcional).
* **Taxonomía**:
  * `Tipo`: TECNICO, FINANCIERO, ADMINISTRATIVO, LEGAL, COORDINACION, EXTERNO.
  * `Impacto`: BLOQUEA_PAGO, RETRASA_OBRA, RETRASA_CONVENIO, RIESGO_RENDICION, OTRO.
* **Ciclo de Vida**: ABIERTO → EN_GESTION → (RESUELTO | CERRADO_SIN_RESOLVER).
* **Actores**: Detectado por (Usuario) → Resuelto por (Usuario).

**Lógica de Negocio:**

1. **Detección Manual**: Un usuario "levanta la mano" creando un problema.
2. **Cálculo de Días Abierto**: `today - detectado_en`.
3. **Bloqueo Semántico**: Una IPR con problemas abiertos se marca automáticamente como `tiene_problemas_abiertos = true`.

---

### M2: Gestor de Compromisos (Task Force)

*La entidad `CompromisoOperativo` es la unidad de trabajo para resolver problemas.*

**Estructura de Datos (Átomo):**

* **Origen**: Puede nacer de un `ProblemaIPR` o de una `InstanciaColectiva` (Reunión).
* **Tipificación**: Catálogo `TipoCompromisoOperativo` (e.g., "Gestionar CDP", "Visita Terreno").
* **Asignación**:
  * `Responsable`: Usuario específico (Atómico).
  * `División`: Derivada del usuario (Contextual).
* **Temporalidad**: `fecha_limite` (Deadlines estrictos).
* **Estados**: PENDIENTE → EN_PROGRESO → COMPLETADO → VERIFICADO.

**Lógica de Negocio:**

1. **Invariante de Verificación**: Un compromiso no está cerrado hasta que es `VERIFICADO` (normalmente por la jefatura).
2. **Regla de Vencimiento**: Si `fecha_limite < hoy` y estado no es terminal, está **VENCIDO**.
3. **Escalabilidad**: Compromisos `URGENTE` o vencidos suben al dashboard de Jefatura/Admin Regional.

---

### M3: Radar de Alertas (Signal Detection)

*Sistema de monitoreo pasivo que genera señales activas (`AlertaIPR`).*

**Tipos de Señales (Detectores):**

1. **Obra Terminada Sin Pago**: `avance_fisico >= 95%` AND `saldo_pendiente > 0`.
2. **Cuota Vencida**: `fecha_cuota < hoy` AND `estado != PAGADA`.
3. **Convenio por Vencer**: `fecha_termino < hoy + 30 dias`.
4. **Compromiso Vencido**: `fecha_limite < hoy` AND `estado != COMPLETADO`.
5. **Rendición Pendiente**: (Lógica futura mockeada en legacy).

**Niveles de Criticidad (Semáforo):**

* 🔴 **CRÍTICO**: Requiere acción inmediata (Admin Regional).
* 🟠 **ALTO**: Requiere gestión prioritaria (Jefe División).
* 🟡 **ATENCIÓN**: Advertencia temprana (Encargado).
* 🔵 **INFO**: Informativo.

---

### M4: Vistas de Mando (Role-Based Dashboards)

*Cada rol tiene una "lente" diferente sobre los mismos datos.*

#### 1. Administrador Regional (La Torre de Control)

* **Objetivo**: Gestión de Crisis y Coordinación.
* **KPIs**:
  * IPRs Críticas (Nivel Alerta = CRITICO).
  * Problemas Escalados (Impacto = ALTO/CRITICO).
  * Compromisos Vencidos Globales.
* **Flujo**: Reunión Semanal de Crisis (Revisar alertas → Pedir explicaciones → Crear compromisos).

#### 2. Jefe de División (El Supervisor)

* **Objetivo**: Que su equipo cumpla.
* **KPIs**:
  * Compromisos vencidos *de su división*.
  * Problemas asignados a *su división*.
* **Flujo**: Seguimiento de equipo (Verificar compromisos completados).

#### 3. Encargado Operativo (El Ejecutor)

* **Objetivo**: Limpiar su bandeja de entrada.
* **Vista**: "Mis Compromisos" (Lista priorizada por fecha/urgencia).
* **Flujo**: Actualizar avance IPR → Marcar compromiso completado.

#### 4. Profesional DAF (El Financiero)

* **Objetivo**: Flujo de caja y cumplimiento administrativo.
* **KPIs**:
  * Convenios por vencer.
  * Rendiciones pendientes (Cuellos de botella financieros).

---

## 3. Requisitos para `gore_os` (La Migración)

Para replicar esto en `gore_os` (Stack Composicional), necesitamos:

### A. Modelo de Datos (Drizzle Schema)

Habilitar el namespace `gore_ejecucion` con las siguientes tablas:

1. `problema_ipr`
2. `compromiso_operativo`
3. `tipo_compromiso_operativo` (Catálogo maestro)
4. `historial_compromiso` (Event Sourcing esencial)
5. `alerta_ipr`

### B. Lógica de Dominio (Effect Services)

1. **AlertService**: Worker periódico que ejecute las reglas de detección y popule `AlertaIPR`.
2. **CommitmentService**: Máquina de estados para `CompromisoOperativo` (usando XState para transiciones validas: Completar → Verificar).
3. **CrisisService**: Lógica de "Semáforos" (cálculo de nivel de alerta de IPR basado en sus problemas y alertas).

### C. API (tRPC Routers)

1. `dashboard.getRegionalSummary`
2. `dashboard.getDivisionSummary`
3. `dashboard.getMyCommitments`
4. `crisis.createProblem`
5. `commitment.verify`

---

## 4. Estrategia de Implementación

*Sugerencia de orden de ataque:*

1. **Fundamentos**: Migrar schemas Drizzle para `problema` y `compromiso`.
2. **Motor de Compromisos**: Implementar CRUD + FSM de compromisos (es lo más usado).
3. **Integración IPR**: Conectar compromisos a la tabla `iniciativa` existente en `gore_os`.
4. **Dashboards**: Implementar las consultas agregadas (con `groupby` y `counts`) en tRPC.
5. **Alertas**: Implementar el worker de reglas al final (ya que depende de datos vivos).
