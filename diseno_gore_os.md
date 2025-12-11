# Diseño y Especificaciones — GORE OS

> **Versión**: 3.0.0 PHOENIX-CATEGORICAL  
> **Ontología Base**: `data-gore/tracks/ontology/modular` v5.1.0  
> **Stack**: Bun + Hono + tRPC + Drizzle + XState + PostgreSQL

## Alcance
Consolidado de 19 módulos con: resumen, user stories enriquecidas (todas las existentes), modelo de datos clave, flujos/UI, APIs/servicios sugeridos, criterios de prueba y KPIs.

---

## Fundamentos Categóricos

### Categoría de Dominio C_GORE

El Sistema Operativo GORE se modela como realización de una **2-categoría** definida en la ontología:

| Componente | Definición | Cantidad |
|------------|------------|----------|
| **0-células** | Capas ontológicas (L0-L9, Lω, L∅) | 12 |
| **1-células** | Funtores entre capas | 32 |
| **2-células** | Transformaciones naturales | ~15 |
| **Objetos** | Entidades del dominio | ~1230 |
| **Morfismos** | Relaciones tipadas | ~4500 |

### Propiedades Categóricas Preservadas

| Propiedad | Realización Técnica | Verificación |
|-----------|--------------------|--------------|
| **Límites finitos** | PostgreSQL: JOINs, FKs, UNIQUE | DB constraints + compile-time |
| **Colímites** | Zod discriminatedUnion, JSONB | Runtime validation |
| **Clasificador Ω** | Zod schemas `χ: X → Bool` | Type inference |
| **Adjunción ORM⊣Reflect** | Drizzle schema-first | Schema = Types = Queries |
| **Coalgebras (FSM)** | XState machines | Bisimulation garantizada |

### Morfismos Inter-Módulo Clave

| Morfismo | Dominio | Codominio | Tipo | Descripción |
|----------|---------|-----------|------|-------------|
| `F_Financia` | Fondo | IPR | N:M | Fondo financia múltiples IPR |
| `F_Ejecuta` | Ejecutor | IPR | 1:N | Ejecutor responsable de IPR |
| `F_Territorial` | IPR | Comuna | N:1 | IPR localizada en comuna |
| `F_Formaliza` | Convenio | IPR | 1:1 | Vínculo contractual |
| `F_Consume` | IPR | CDP | 1:N | IPR consume disponibilidad |
| `F_Rinde` | Ejecutor | Rendición | 1:N | Ejecutor rinde gastos |

---

## Stack Tecnológico

### Decisiones Principales

| Capa | Tecnología | Justificación Categórica |
|------|------------|-------------------------|
| **Runtime** | Bun 1.x | TypeScript nativo, tipos preservados |
| **Framework** | Hono | Middlewares composicionales |
| **API** | tRPC v11 | Funtores tipados end-to-end |
| **Validación** | Zod | Clasificador Ω con inferencia |
| **ORM** | Drizzle | Adjunción verificable, schema-first |
| **FSM** | XState v5 | Coalgebras formales |
| **DB** | PostgreSQL 16 + PostGIS | Límites finitos + Topos geoespacial |

### Decisiones de NO Usar

| Tecnología | Razón |
|------------|-------|
| **MongoDB** | Pierde morfismos (FKs). Modelo es relacional (~4500 morfismos) |
| **GraphQL** | Over-engineering. tRPC ofrece mejor DX para sistema interno |
| **Prisma** | Query engine opaco. Drizzle preserva adjunción |

---

## Arquitectura C4 (alto nivel)

### Nivel 1 — Contexto de Sistema

- **Sistema principal:** `GORE_OS` — Sistema Operativo Cognitivo Regional que orquesta el ciclo de inversión pública, gestión financiera, ejecución, gobernanza, cumplimiento y homeostasis organizacional.
- **Actores internos (Esfera 1 — Núcleo GORE):** Gobernador Regional, Consejeros Regionales, Administrador Regional, Jefes de División, Analistas DIPIR, Supervisores de Proyecto, Profesionales DAF/UCR, Profesional GDP, Profesionales Bienestar, Abastecimiento, TIC, Cumplimiento, CIES, UGIT, PMO TIC, etc. (detallados en Anexo B).
- **Actores gobierno central (Esfera 2):** MDSF Regional, DIPRES/SES, CGR, CPLT, IND/CMN/MINCAP, SEREMI y otras entidades sectoriales que interactúan vía servicios de integración.
- **Ecosistema regional (Esfera 3):** Municipalidades (UF/UTR), Ciudadanía, OSC, Empresas, Academia, que consumen transparencia, IDE/GIS y otros servicios externos.
- **Sistemas externos clave:** MDSF/BIP, SIGFE, SISREC, Mercado Público, Previred, IMED/Medipass, Mutual de Seguridad, IDE Chile, portales de Transparencia/Lobby, sistemas sectoriales (IND, CMN, MINCAP), Red Estado, entre otros.

En la vista de contexto, todos estos actores usan o se integran con `GORE_OS` para formular, evaluar, aprobar, ejecutar y cerrar IPR; gestionar presupuesto y convenios; monitorear ejecución y crisis; gobernar (CORE, GR); cumplir normativa; y sostener personas/activos/bienestar y transformación digital.

### Nivel 2 — Contenedores lógicos

- **Portal Interno GORE_OS (Web App)**  
  - Tipo: SPA web interna.  
  - Usuarios: funcionarios GORE y municipalidades (DIPIR, DAF, UCR, JD, AR, Supervisores, GDP, Bienestar, Abastecimiento, etc.).  
  - Rol: UI unificada para todos los módulos internos (1–19) con vistas según rol y permisos.

- **Portal Externo / Transparencia (Web Pública)**  
  - Tipo: web pública.  
  - Rol: exposición de cartera, acuerdos CORE, transparencia activa, indicadores territoriales básicos, acceso a IDE/GIS público.

- **CIES Frontend (Consola de Operación)**  
  - Tipo: consola web especializada.  
  - Rol: monitoreo en tiempo real, mapas, incidentes y coordinación con enlaces externos (CIES-OP, CIES-SUP, CIES-ENL).

- **API Plataforma GORE_OS (Backend de Dominios)**  
  - Tipo: backend principal (tRPC + REST/OpenAPI para externos) que implementa los bounded contexts como funtores tipados.  
  - Dominios: 
    - Inversión Pública (IPR & cartera): módulos 1, 4, 5 (parte), 12, 13, 14.  
    - Finanzas Públicas: módulos 2, 3 (Presupuesto, Convenios, Rendiciones).  
    - Territorial & ERD: módulos 7, 9, 18.  
    - Gobernanza & Cumplimiento: módulos 5, 11, 13.  
    - Personas & Homeostasis: módulos 6, 15, 16, 17.  
    - Seguridad/TIC/Evolución: módulos 8, 10, 19.  
  - Rol: expone todos los endpoints funcionales descritos en este documento y orquesta la lógica de negocio.

- **Capa de Integración / Integración Externa**  
  - Tipo: servicios de integración o ESB ligero.  
  - Rol: adaptadores hacia MDSF/BIP, SIGFE, SISREC, Mercado Público, Previred, IMED, Mutual, IDE Chile, leylobby, CPLT, y sistemas sectoriales; provee APIs internas `/integracion/*` usadas por la API Plataforma.

- **IDE/Geo Plataforma (Infraestructura Geoespacial)**  
  - Tipo: stack geoespacial (Geoserver/Geonodo + catálogo).  
  - Rol: publicar capas y metadatos (IDE/GIS), servicios OGC (WMS/WFS/WCS), federar con IDE Chile y servir mapas para Territorial, CORE, CIES y portales.

- **CIES Servicio Tiempo Real**  
  - Tipo: backend orientado a streams/eventos.  
  - Rol: gestionar feeds de cámaras/sensores, incidentes y protocolos de respuesta, integrándose con actores externos de seguridad.

- **DB Operacional GORE_OS**  
  - Tipo: base de datos transaccional alineada a la ontología categórica GORE Ñuble v4.x.  
  - Rol: persistir entidades de los dominios `gore_*`, `L0_*`, `L4_*`, `Lomega_*` que aparecen en las user stories y modelos de datos.

- **Data Warehouse / Lago de Datos (Analítica)**  
  - Tipo: DW/Datamart o lago de datos.  
  - Rol: consolidar series históricas, indicadores ERD, KPIs de gestión y métricas de deuda técnica para reporting y analítica avanzada.

- **IdP/SSO (Gestión de Identidad y Accesos)**  
  - Tipo: proveedor de identidad (p.ej., Keycloak/AD/IdP estatal).  
  - Rol: autenticación/SSO y autorización coarse-grained para todos los frontends y la API Plataforma; se cruza con modelos `gore_seguridad` y `gore_actores`.

- **Observabilidad & Auditoría**  
  - Tipo: stack de logs/metrics/traces.  
  - Rol: cumplir requerimientos de trazabilidad, probidad y auditoría (CGR, Cumplimiento), registrando quién hizo qué, cuándo y con qué efecto.

## C4 Nivel 3 — Slice IPR+Presupuesto+Convenios

### Contenedores de dominio implicados (dentro de la API Plataforma)

- **Servicio IPR**  
  - Ciclo de inversión pública: postulación → admisibilidad → MDSF/RATE → CORE → ejecución → cierre.  
  - Mapea principalmente a módulos 1, 4, 5 (parte), 12, 13, 14.
- **Servicio Presupuesto**  
  - Ciclo presupuestario: CDP, afectación, devengo, pago, modificaciones, proyección, SIGFE.  
  - Mapea al módulo 2 (y parte de 3 vía vista financiera).
- **Servicio Convenios & Rendiciones**  
  - Gestión de convenios, cuotas, garantías, SISREC, rendiciones y contabilización SIGFE.  
  - Mapea al módulo 3 (y parte de 2 por devengo/pago por convenio).
- **Núcleo compartido (Shared Kernel)**  
  - Actores, territorial, documental, FSM, indicadores, normativa.

### 1. Servicio IPR — Componentes internos

**Capa Presentación / API**
- `IPRCommandController` — endpoints para crear/editar IPR, enviar a admisibilidad/MDSF, registrar observaciones, generar carpeta CORE, registrar problemas, modificaciones y cierres.  
- `IPRQueryController` — endpoints de consulta: timeline de estado, dashboard de cartera, semáforos de ejecución, historial de postulaciones, fichas IPR.

**Capa Aplicación**
- `IPRApplicationService` — orquesta casos de uso de IPR (creación, actualización, cambio de fase, vinculación con convenios).  
- `AdmisibilidadService` — aplica checklist por `codigo_track`, calcula resultado ADMISIBLE/CON OBS/INADMISIBLE y dispara transiciones FSM.  
- `RateSyncService` — coordina con `MDSFClient` para registrar "Informar Postulación", leer RATE (RS/FI/OT/AD) y actualizar `resultado_rate` notificando a UF/AD.  
- `CorePreparationService` — construye "carpeta CORE" (oficios, fichas, anexos) a partir de IPR con RS y parámetros de sesión.  
- `ExecutionMonitoringService` — usa `FSMService`, `AlertService` y `ExecutionKpiCalculator` para semáforos de ejecución, problemas/nudos y compromisos.

**Capa Dominio**
- Agregados:  
  - `IniciativaAggregate` (`gore_inversion.iniciativa`) — estado FSM, track, ejecutor, monto, comuna, vínculos a convenios y avances.  
  - `ChecklistAdmisibilidad` — ítems por mecanismo, resultado, observaciones.  
  - `EvaluacionRate` — resultado RATE y antecedentes.  
  - `ProblemaIPR`, `AlertaIPR`, `CompromisoOperativo` — severidad, impacto, responsable, plazo.  
  - `CarpetaCore` — tabla de IPR para sesión CORE y documentos asociados.  
- Servicios de dominio: `FSMService` (gestión `gore_fsm.*`), `IPRPolicy` (reglas de negocio), `ExecutionKpiCalculator` (cálculo de KPIs de ejecución).

**Capa Infraestructura**
- Repositorios: `IniciativaRepository`, `EvaluacionRepository`, `RateRepository`, `ProblemaRepository`, `CompromisoRepository`, `CarpetaCoreRepository`.  
- Adaptadores: `BIPClient`/`MDSFClient` (integración MDSF/BIP), `NotificationClient` (email/push a FE, UF, JD, AR, etc.), `DocumentGenerator` (fichas, oficios, carpeta CORE).

### 2. Servicio Presupuesto — Componentes internos

**Capa Presentación / API**
- `BudgetCommandController` — CDP, movimientos presupuestarios, modificaciones, programación de pagos.  
- `BudgetQueryController` — pipeline de afectación por IPR, dashboard de ejecución, deuda flotante, proyecciones.

**Capa Aplicación**
- `CdpService` — emisión y validación de CDP, verifica saldo de `asignacion`.  
- `BudgetExecutionService` — maneja el pipeline preafectación → compromiso → devengo → pago.  
- `BudgetModificationService` — asiste en modificaciones presupuestarias, determinando tipo de acto, visaciones y TdR.  
- `BudgetProjectionService` — computa proyección de ejecución vs programa de caja DIPRES y calcula deuda flotante.  
- `SigfeSyncService` — orquesta integración con SIGFE a través de `SigfeClient`.

**Capa Dominio**
- Agregados: `AsignacionPresupuestaria`, `Cdp`, `MovimientoPresupuestario`, `CuotaTransferencia` (perspectiva financiera).  
- Servicios de dominio: `BudgetRules` (validación de glosas y restricciones), `DebtCalculator` (deuda flotante por programa/subtítulo).

**Capa Infraestructura**
- Repositorios: `CdpRepository`, `MovimientoPresupuestarioRepository`, `AsignacionRepository`.  
- Adaptadores: `SigfeClient` (sincronización de movimientos), `NormativaGlosaStore` (reglas de glosa).

### 3. Servicio Convenios & Rendiciones — Componentes internos

**Capa Presentación / API**
- `ConvenioCommandController` — creación y gestión del ciclo de convenios (estados, cuotas, garantías).  
- `RendicionCommandController` — registro de rendiciones SISREC, revisión RTF, aprobación Jefe DAF, contabilización UCR.  
- `ConvenioQueryController` / `RendicionQueryController` — listados de convenios por estado, alertas de vencimiento, dashboards de rendiciones pendientes.

**Capa Aplicación**
- `ConvenioLifecycleService` — orquesta el ciclo del convenio: elaboración → visación → TdR → vigente → terminado.  
- `QuotaScheduleService` — maneja programación de `cuota_transferencia` (fechas, condiciones de liberación).  
- `GuaranteeService` — controla garantías asociadas (creación, vencimiento, renovación).  
- `SisrecSyncService` — registra convenios y transferencias en SISREC.  
- `RenditionReviewService` — flujo de revisión RTF (aprobar/observar).  
- `UcrAccountingService` — contabilización de rendiciones aprobadas en SIGFE.

**Capa Dominio**
- Agregados:  
  - `ConvenioAggregate` (`gore_financiero.convenio`) — cláusulas, ejecutor, estado, garantías, cuotas.  
  - `Garantia` — tipo, vigencia, monto.  
  - `Rendicion`/`TransaccionRendida` — detalle de gastos rendidos y estados de revisión.  
  - `AlertaConvenio` — vencimientos de convenios/garantías y otros hitos.
- Servicios de dominio: `ConvenioPolicy` (reglas sobre anexos, prórrogas, nuevos actos), `RenditionPolicy` (reglas de aprobación/observación y bloqueos Art.18).

**Capa Infraestructura**
- Repositorios: `ConvenioRepository`, `CuotaRepository`, `GarantiaRepository`, `RendicionRepository`, `AlertaConvenioRepository`.  
- Adaptadores: `SisrecClient` (creación de proyectos/programas y registro de rendiciones), `SigfeClient` (contabilización de rendiciones), `DocumentGenerator` (plantillas de convenios e informes de aprobación).

### 4. Núcleo compartido / Shared Kernel

- `ActorAggregate` (`gore_actores.*`) — personas, divisiones, entidades ejecutoras, municipios.  
- `TerritorialModel` (`gore_territorial.*`) — comuna, provincia, capas territoriales.  
- `DocumentoAggregate` (`gore_documental.*`) — documentos, versiones, firmas (FEA).  
- `FSMService`/`EventStore` — estados de IPR, convenios, rendiciones.  
- `IndicatorService` — cálculo y exposición de KPIs usados en dashboards de IPR, presupuesto y convenios.

### 5. Relaciones clave en el slice

- **IPR ↔ Presupuesto:** `IPRApplicationService` llama a `CdpService` y `BudgetExecutionService` para emitir CDP y reflejar afectación financiera por iniciativa.  
- **IPR ↔ Convenios:** sólo IPR con RS y acuerdo CORE pueden generar convenios; `IPRApplicationService` coopera con `ConvenioLifecycleService` usando `IniciativaId`.  
- **Convenios ↔ Presupuesto:** `QuotaScheduleService` y `BudgetExecutionService` coordinan compromisos, devengos y pagos por `convenioId`.  
- **Convenios & Rendiciones ↔ Externos:** `SisrecSyncService` usa `SisrecClient` y `UcrAccountingService` usa `SigfeClient` para cerrar el ciclo financiero.

---

## APIs Slice IPR+Presupuesto+Convenios (v1)

### Principios comunes

- **Protocolo interno**: tRPC (type-safe end-to-end)
- **Protocolo externo**: REST/OpenAPI (para integraciones con MDSF, SIGFE, etc.)
- **Base path REST**: `/api/v1`
- **Formato**: JSON
- **Auth**: SSO/JWT con `role` y `division` en claims
- **Errores**: `Result<T, AppError>` con tipos discriminados

### Ejemplo tRPC Router (interno)

```typescript
// apps/api/src/routers/ipr.ts
export const iprRouter = router({
  create: protectedProcedure
    .input(CreateIPRSchema)
    .mutation(({ input, ctx }) => iprService.create(input, ctx.user)),
  
  get: publicProcedure
    .input(z.object({ bip: z.string() }))
    .query(({ input }) => iprRepository.findByBip(input.bip)),
  
  admisibilidad: protectedProcedure
    .use(requireRole('ANALISTA_DIPIR'))
    .input(AdmisibilidadSchema)
    .mutation(({ input }) => admisibilidadService.registrar(input)),
  
  dashboard: protectedProcedure
    .input(DashboardFiltersSchema)
    .query(({ input }) => iprService.getDashboard(input)),
})
```

### Endpoints REST (para referencia e integraciones)

### 1. Servicio IPR

**Crear IPR**  
`POST /api/v1/ipr`

Request:
```json
{
  "trackCodigo": "SNI|FRIL|FRPD|8PCT|GLOSA06",
  "ejecutorId": "entidad-uuid",
  "montoTotal": 123456789,
  "comunaId": "comuna-uuid",
  "nombre": "Mejoramiento Plaza X",
  "descripcion": "...",
  "sector": "Deporte",
  "documentosAdjuntos": ["doc-uuid-1", "doc-uuid-2"]
}
```

**Registrar admisibilidad**  
`POST /api/v1/ipr/{iprId}/admisibilidad`

Request:
```json
{
  "resultado": "ADMISIBLE|CON_OBS|INADMISIBLE",
  "itemsChecklist": [
    { "codigo": "DOC_OBLIGATORIO_X", "cumple": true, "observacion": null }
  ],
  "observacionesGenerales": "...",
  "mecanismo": "SNI|FRIL|FRPD|..."
}
```

**Enviar a MDSF / registrar RATE**  
`POST /api/v1/ipr/{iprId}/enviar-a-mdsf`  
`GET  /api/v1/ipr/{iprId}/rate`  
`POST /api/v1/ipr/{iprId}/rate/actualizar` (uso interno integración).

**Carpeta CORE**  
`POST /api/v1/ipr/core/cartera` — define cartera para sesión CORE.  
`GET  /api/v1/ipr/core/cartera/{sesionCoreId}` — devuelve fichas y documentos.

**Ejecución, problemas y compromisos**  
`POST /api/v1/ipr/{iprId}/avance` — registra avance físico/financiero.  
`POST /api/v1/ipr/{iprId}/problemas` — crea `ProblemaIPR`.  
`POST /api/v1/ipr/{iprId}/compromisos` — crea compromiso operativo vinculado.

**Consultas**  
`GET /api/v1/ipr/{iprId}` — ficha completa.  
`GET /api/v1/ipr/{iprId}/timeline` — historial FSM.  
`GET /api/v1/ipr/dashboard` — filtros por estado, división, analista, track, comuna.  
`GET /api/v1/ipr/historial?rutEntidad=` — historial por formulador.

### 2. Servicio Presupuesto

**Emisión de CDP**  
`POST /api/v1/presupuesto/cdp`

Request:
```json
{
  "iprId": "ipr-uuid",
  "asignacionId": "asig-uuid",
  "monto": 123456,
  "glosa": "CDP Convenio Plaza"
}
```

**Pipeline afectación**  
`GET /api/v1/presupuesto/ipr/{iprId}/pipeline` — preafectación → compromiso → devengo → pago.

**Modificaciones y glosas**  
`POST /api/v1/presupuesto/modificaciones` — asistente de modificaciones; devuelve tipo de acto y visaciones sugeridas.  
`POST /api/v1/presupuesto/verificar-glosa` — valida movimiento contra glosas.

**Proyección y SIGFE**  
`GET  /api/v1/presupuesto/proyeccion?mes=&anio=` — ejecución vs programa caja; proyección deuda flotante.  
`POST /api/v1/presupuesto/sigfe/sync` — sincronización de movimientos con SIGFE.

### 3. Servicio Convenios & Rendiciones

**Generar convenio**  
`POST /api/v1/convenios`

Request:
```json
{
  "iprId": "ipr-uuid",
  "tipoEjecutor": "MUNICIPALIDAD|SERVICIO|PRIVADO",
  "plantillaId": "plantilla-uuid",
  "monto": 10000000,
  "fechaInicio": "2025-01-01",
  "fechaTermino": "2026-12-31"
}
```

**Gestionar estado de convenio**  
`GET  /api/v1/convenios?estado=&ejecutorId=&fechaTerminoDesde=&fechaTerminoHasta=`  
`PATCH /api/v1/convenios/{convenioId}/estado` — `ELABORACION|VISACION|TDR|VIGENTE|TERMINADO`.

**Cuotas y garantías**  
`POST /api/v1/convenios/{convenioId}/cuotas` — registra `cuota_transferencia`.  
`POST /api/v1/convenios/{convenioId}/garantias` — registra garantías.  
`GET  /api/v1/convenios/alertas` — convenios/garantías próximos a vencer.

**Rendiciones SISREC**  
`POST /api/v1/rendiciones` — registro de rendición (SISREC).  
`POST /api/v1/rendiciones/{rendicionId}/revisar` — RTF aprueba/observa.  
`POST /api/v1/rendiciones/{rendicionId}/contabilizar` — UCR contabiliza en SIGFE.

**Dashboard rendiciones**  
`GET /api/v1/rendiciones/dashboard?ejecutorId=&estado=&diasMoraDesde=` — ranking de ejecutores por mora, montos rendidos/observados.

---

## FSM del Dominio (Coalgebras Principales)

Las máquinas de estados finitos se modelan como **coalgebras** `c: Estado → F(Estado)` usando XState v5.

### FSM de IPR — 24 Estados

```
POSTULADA → PRE_ADMISIBLE → EN_ADMISIBILIDAD → ADMISIBLE → EN_EVALUACION_MDSF
                                                    ↓
                        ┌───────────────────────────┼───────────────────────────┐
                        ↓                           ↓                           ↓
                     CON_RS                      CON_FI                      CON_OT
                        ↓                           ↓                           ↓
                  EN_CARTERA ←──────────────── SUBSANADA ←────────────────── SUBSANADA
                        ↓
                  PRIORIZADA → EN_FINANCIAMIENTO → EN_FORMALIZACION → EN_EJECUCION
                                                                            ↓
                                                              EN_CIERRE → CERRADA
```

**Transiciones clave**:

| Estado Origen | Evento | Estado Destino | Actor |
|---------------|--------|----------------|-------|
| POSTULADA | EVALUAR_PRE | PRE_ADMISIBLE | Sistema |
| PRE_ADMISIBLE | ADMITIR | ADMISIBLE | Analista DIPIR |
| ADMISIBLE | ENVIAR_MDSF | EN_EVALUACION_MDSF | Analista DIPIR |
| EN_EVALUACION_MDSF | RECIBIR_RS | CON_RS | MDSF (integración) |
| EN_EVALUACION_MDSF | RECIBIR_FI | CON_FI | MDSF (integración) |
| CON_RS | PRIORIZAR | PRIORIZADA | JD-DIPIR |
| PRIORIZADA | APROBAR_CORE | EN_FINANCIAMIENTO | CORE |
| EN_FINANCIAMIENTO | FORMALIZAR | EN_FORMALIZACION | DAF |
| EN_FORMALIZACION | INICIAR_EJECUCION | EN_EJECUCION | Supervisor |
| EN_EJECUCION | CERRAR | EN_CIERRE | Supervisor |
| EN_CIERRE | VALIDAR_CIERRE | CERRADA | Analista DIPIR |

### FSM de Rendición — 9 Estados

```
PENDIENTE → EN_REVISION_RTF → APROBADA_RTF → EN_FIRMA_DAF → APROBADA → CONTABILIZADA
                ↓
           OBSERVADA → EN_SUBSANACION → (vuelve a EN_REVISION_RTF)
                ↓
           RECHAZADA (final)
```

### FSM de Convenio — 7 Estados

```
ELABORACION → EN_VISACION → EN_TDR → VIGENTE → EN_CIERRE → TERMINADO
                                        ↓
                                   EN_PRORROGA (loop)
```

---

## Invariantes del Sistema

Invariantes críticos extraídos de la ontología (`verificacion.yaml`) que deben verificarse:

### Invariantes Financieros (CRITICAL)

| ID | Nombre | Fórmula | Verificación |
|----|--------|---------|--------------|
| `INV_FIN_01` | Balance presupuestario | `Σ(ingresos) = Σ(gastos) + saldo` | por_transaccion |
| `INV_FIN_02` | CDP ≤ disponibilidad | `∀cdp. cdp.monto ≤ asignacion.disponible` | por_transaccion |
| `INV_FIN_03` | Cuotas = Convenio | `∀conv. Σ(cuotas.monto) = conv.monto_total` | por_transaccion |
| `INV_FIN_04` | Rendición ≤ Transferido | `∀rend. monto_rendido ≤ monto_transferido` | por_transaccion |

### Invariantes de Estado (CRITICAL)

| ID | Nombre | Fórmula | Verificación |
|----|--------|---------|--------------|
| `INV_FSM_01` | Transición válida | `∀ipr. transicion ∈ FSM.transiciones_permitidas` | por_transaccion |
| `INV_FSM_02` | Estado consistente | `∀ipr. estado_db = estado_fsm` | batch_diario |
| `INV_FSM_03` | No retroceso ilegal | `∀ipr. fase(t+1) ≥ fase(t) ∨ evento_subsanacion` | por_transaccion |

### Invariantes de Activos (CRITICAL)

| ID | Nombre | Fórmula | Verificación |
|----|--------|---------|--------------|
| `INV_L0A_02` | Conservación stock | `stock = Σ(ingresos) - Σ(egresos) + Σ(ajustes)` | por_transaccion |
| `INV_L0A_03` | Stock no negativo | `∀item. stock ≥ 0` | por_transaccion |
| `INV_L0A_04` | Km monotónico | `∀v,t1<t2. km(v,t1) ≤ km(v,t2)` | por_transaccion |

### Invariantes de Personas (HIGH)

| ID | Nombre | Fórmula | Verificación |
|----|--------|---------|--------------|
| `INV_L0P_01` | Saldo feriado coherente | `saldo = acumulado - consumido` | por_transaccion |
| `INV_L0P_02` | Permisos ≤ 6 días/año | `∀func. permisos_usados ≤ 6` | por_transaccion |

---

## 1. MÓDULO IPR — Gestión de Inversión Pública Regional
**Dominio:** `gore_inversion`, `gore_evaluacion` · **Función:** Financiar + Ejecutar · **Journeys:** J01, J05, J06, JX01-JX05  
**Resumen:** Asistir formulación, admisibilidad, evaluación RATE/MDSF, CORE, ejecución y cierre con trazabilidad y alertas.

### User Stories enriquecidas
- **FE-IPR-001** Árbol financiamiento → AC: wizard con track (SNI/FRIL/FRPD/8%/Glosa06), persistencia y checklist.
- **FE-IPR-002** Checklist documentos → AC: obligatorio/opcional, ejemplos, glosa.
- **FE-IPR-003** Cargar postulación → AC: valida esquema/pesos, número ingreso, estado RECIBIDA, expediente.
- **FE-IPR-004** Notificación observaciones → AC: email+push con detalle y plazo 60d, acuse lectura.
- **FE-IPR-005** Subsanación en línea → AC: estado SUBSANACIÓN ENVIADA, versionado, notifica GORE.
- **FE-IPR-006** Estado tiempo real → AC: timeline fases con fechas y SLA.
- **FE-IPR-007** Historial postulaciones → AC: tasa admisibilidad y motivos frecuentes.
- **FE-IPR-009** Descargar convenio → AC: PDF, estado firmas FEA/visaciones.
- **FE-IPR-010** Reporte avance mensual → AC: notifica RTF, valida coherencia físico/financiero.
- **AD-IPR-001** Dashboard cartera IPR por fase del ciclo → AC: dado mi asignación, cuando accedo veo contadores por estado (Ingresada, Pre-admisible, En MDSF, Con RS, en CORE, en Ejecución, Cerrada) con filtros por mecanismo y comuna.
- **AD-IPR-002** Bandeja de postulaciones nuevas → AC: dado rol Analista, cuando accedo veo IPR sin asignar ordenadas por fecha y filtrables por mecanismo y municipio.
- **AD-IPR-003** Checklist de admisibilidad por mecanismo → AC: dado IPR+mecanismo, cuando proceso admisibilidad veo checklist dinámico según track (SNI, FRIL, Glosa06, etc.) y no puedo cerrar sin completar campos obligatorios.
- **AD-IPR-004** Registrar resultado de admisibilidad → AC: dado checklist completo, cuando registro resultado ADMISIBLE/CON OBS/INADMISIBLE el estado de la IPR cambia y la Unidad Formuladora es notificada.
- **AD-IPR-005** Enviar IPR a MDSF → AC: dado IPR admisible tipo SNI, cuando ejecuto envío se registra "Informar Postulación" en BIP y el estado cambia a "EN EVALUACIÓN MDSF".
- **AD-IPR-006** Monitorear estados RATE → AC: dado cartera en MDSF, cuando consulto veo semáforo RS/FI/OT/AD con días transcurridos y alertas de vencimiento.
- **AD-IPR-007** Alertas por IPR sin movimiento >30 días → AC: dado IPR en MDSF más de 30 días sin cambio de estado, cuando se detecta recibo alerta para gestionar con SEREMI/MDSF.
- **AD-IPR-008** Registrar observaciones FI/OT → AC: dado RATE FI/OT, cuando registro observaciones UF recibe notificación con detalle y plazo de 60 días para subsanar.
- **AD-IPR-009** Cartera con RS disponible para CORE → AC: dado período de sesión CORE, cuando filtro veo IPR con RS listas para votación.
- **AD-IPR-010** Generar carpeta CORE automática → AC: dada cartera seleccionada, cuando genero obtengo PDF consolidado con oficio, fichas técnicas y anexos.
- **AD-IPR-011** Registrar problema/nudo en ejecución → AC: dado IPR con problema, cuando registro defino tipo, impacto, responsable y creo compromiso asociado.
- **AD-IPR-012** Semáforos de ejecución → AC: dado cartera asignada, cuando veo dashboard los semáforos reflejan % físico vs financiero vs tiempo con reglas configurables.
- **AD-IPR-013** Tramitar modificaciones de IPR → AC: dada una solicitud (monto, plazo, ejecutor), cuando proceso el sistema determina si requiere nueva RS y/o aprobación CORE.
- **AD-IPR-014** Validar cierre técnico de IPR → AC: dada IPR terminada, cuando proceso cierre verifico acta de recepción, saldos y actualizo estado a "CERRADA" y cierre BIP.
- **AD-IPR-015** Exportar reportes para CGR/DIPRES → AC: dado parámetros de reporte, cuando ejecuto exportación obtengo Excel/PDF con formato requerido por organismo.
- **JD-DIPIR-001** Dashboard ejecutivo cartera IPR → AC: dado rol jefatura, cuando accedo veo total IPR, monto cartera, % ejecución, problemas críticos y tendencias.
- **JD-DIPIR-002** Distribución de carga de trabajo por analista → AC: dado equipo DIPIR, cuando consulto veo IPR asignadas por analista con métricas de tiempos.
- **JD-DIPIR-003** Tiempos promedio de tramitación por fase → AC: dado período analizado, cuando consulto veo días promedio en cada fase con comparativo histórico.
- **JD-DIPIR-004** Lista de problemas críticos escalados → AC: dado problemas con nivel crítico o escalados, cuando accedo veo lista priorizada con contexto para decisión.
- **JD-DIPIR-005** Preparar propuesta de priorización de cartera → AC: dada cartera con RS/RF, cuando preparo propuesta genero ranking con criterios (ERD, urgencia, monto, comuna).
- **JD-DIPIR-006** Generar informes de gestión divisional → AC: dado período, cuando genero informe obtengo documento con KPIs, logros, problemas y próximos pasos.
- **JD-DIPIR-007** Información consolidada para CDR → AC: dada sesión CDR, cuando preparo tengo tabla de IPR con alineamiento ERD y recomendación.

### Modelo de datos
`gore_inversion.iniciativa`, `gore_documental.documento/version_documento`, `gore_fsm.instancia_fsm/transicion`, `gore_evaluacion.resultado_rate`, `gore_gobernanza.sesion_core`, `gore_ejecucion.avance_obra/alerta_ipr/problema_ipr/compromiso_operativo`, `gore_financiero.convenio/cuota_transferencia/garantia`, `gore_integracion.sincronizacion`.

### Flujos/UI (IFML)
FE: Landing Track → Wizard → Recomendación → Checklist → Formulario+Adjuntos → Timeline → Convenio → Reporte Avance.  
AD: Bandeja → Checklist → Resultado → Envío MDSF → Semáforo RATE → Carpeta CORE → Dashboard Ejecución.  
JD: Dashboard ejecutivo → Carga analista → Tiempos → Problemas → Priorización → Reportes.

### APIs/Servicios sugeridos
POST `/ipr` · POST `/ipr/{id}/admisibilidad` · POST `/ipr/{id}/madsf/enviar` · GET `/ipr/{id}/estado` · POST `/ipr/{id}/avance` · POST `/ipr/{id}/problema` · POST `/ipr/{id}/modificacion` · GET `/ipr/dashboard`.

### Criterios de prueba
- RATE/MDSF >30d genera alerta.
- EP rechaza si avance físico < umbral vs monto.
- Suma cuotas = monto convenio.
- Timeline FSM registra transiciones y notificaciones.

### KPIs
% admisibilidad primera pasada; días por fase; % RS; tiempo a CORE; desviación físico/financiero; tiempo resolución problemas.

---

## 2. MÓDULO PRESUPUESTO — Gestión Financiera
**Dominio:** `gore_presupuesto`, `gore_financiero` · **Función:** Financiar · **Journeys:** J18, JX07  
**Resumen:** CDP, afectación, devengo/pago, modificaciones, proyección y sincronización SIGFE.

### User Stories enriquecidas
- **PD-PPTO-001** Emitir CDP con validación de saldo → AC: dada una solicitud de CDP, cuando proceso el sistema verifica disponibilidad en la asignación y emite o rechaza con fundamento.
- **PD-PPTO-002** Ver estado de afectación por iniciativa → AC: dado código IPR, cuando consulto veo pipeline financiero (preafectación, compromiso, devengo, pago) con montos en cada estado.
- **PD-PPTO-003** Programar pagos según reglas de devengo → AC: dado convenio y tipo de receptor, cuando programo pagos el sistema aplica la regla de devengo según normativa CGR.
- **PD-PPTO-004** Recibir alerta de glosas potencialmente infringidas → AC: dado un movimiento presupuestario, cuando viola Glosa 03/04/06 recibo alerta con explicación y alternativas.
- **PD-PPTO-005** Tramitar modificaciones presupuestarias con asistente → AC: dada necesidad de modificación, cuando ingreso parámetros el sistema indica tipo de acto requerido, visaciones y TdR.
- **PD-PPTO-006** Ver proyección de ejecución vs programa de caja → AC: dado mes/año, cuando consulto veo gráfico comparativo con alertas de desviación >5%.
- **PD-PPTO-007** Calcular deuda flotante al cierre anual → AC: dado cierre de ejercicio, cuando ejecuto cálculo obtengo monto de deuda flotante por programa/subtítulo.
- **PD-PPTO-008** Sincronizar movimientos con SIGFE → AC: dado período procesado, cuando sincronizo se valida consistencia y se reportan diferencias.
- **JD-DAF-001** Dashboard de ejecución presupuestaria mensual → AC: dado mes, cuando consulto veo % de ejecución por subtítulo/programa con semáforo y comparativo año anterior.
- **JD-DAF-002** Ver ejecutores con rendiciones vencidas → AC: dada fecha actual, cuando consulto veo lista de ejecutores con días de vencimiento y monto bloqueado (Art. 18 Res.30).
- **JD-DAF-003** Aprobar informes de rendición con FEA → AC: dado informe revisado por RTF, cuando apruebo firmo con FEA y UCR puede contabilizar en SIGFE.
- **JD-DAF-004** Ver proyección de deuda flotante durante el año → AC: dado punto del año, cuando consulto veo proyección de deuda flotante y su impacto en presupuesto siguiente.

### Modelo de datos
`gore_presupuesto.cdp/movimiento_presupuestario/asignacion`, `gore_financiero.cuota_transferencia/rendicion`, `gore_normativo.glosa`, `gore_integracion.sincronizacion`, `gore_indicadores.indicador/medicion`.

### Flujos/UI
PD: Solicitudes CDP → Pipeline afectación → Pagos → Modificaciones → Proyección.  
JD: Dashboard → Rendiciones vencidas → Aprobación FEA → Proyección deuda.

### APIs
POST `/presupuesto/cdp` · GET `/presupuesto/afectacion/{iprId}` · POST `/presupuesto/pagos` · POST `/presupuesto/modificaciones` · POST `/presupuesto/sigfe/sync`.

### Pruebas
CDP sin saldo rechaza; violación glosa alerta/bloqueo; pagos ≤ compromiso; diferencias SIGFE visibles.

### KPIs
% ejecución por subtítulo; tiempo emisión CDP; rechazos por glosa; deuda flotante; rendiciones vencidas/monto bloqueado.

---

## 3. MÓDULO CONVENIOS Y TRANSFERENCIAS
**Dominio:** `gore_financiero`, `gore_documental` · **Función:** Financiar + Ejecutar  
**Journeys:** J07, JX04  
**Resumen:** Generación y ciclo de convenios, cuotas, garantías, alertas, rendiciones SISREC/SIGFE.

### User Stories enriquecidas
- **PD-CONV-001** Generar convenios desde plantillas según tipo de ejecutor → AC: dada IPR aprobada y tipo de ejecutor, cuando genero convenio obtengo borrador con cláusulas apropiadas pre-llenadas.
- **PD-CONV-002** Ver lista de convenios por estado → AC: dado rol DAF, cuando consulto veo convenios con filtros por estado, fecha de vencimiento y ejecutor.
- **PD-CONV-003** Recibir alertas de convenios próximos a vencer → AC: dado convenio con fecha término cercana, cuando se detecta recibo alerta con acciones sugeridas (prórroga/cierre).
- **PD-CONV-004** Registrar cuotas de transferencia según calendario → AC: dado convenio vigente, cuando registro cuotas quedan programadas con fechas y condiciones de liberación.
- **PD-CONV-005** Controlar garantías de fiel cumplimiento → AC: dada una garantía asociada, cuando está próxima a vencer recibo alerta y puedo registrar renovación.
- **RTF-001** Crear proyectos/programas en SISREC y registrar transferencias → AC: dado convenio formalizado, cuando registro en SISREC entonces el ejecutor puede iniciar rendiciones.
- **RTF-002** Revisar rendiciones con respaldos técnicos y financieros → AC: dada una rendición, cuando reviso apruebo/observo cada transacción con fundamento y adjuntos.
- **RTF-003** Generar informe de aprobación para Jefe DAF → AC: dada rendición aprobada por RTF, cuando genero informe pasa a bandeja de Jefe DAF para firma FEA.
- **RTF-004** Coordinar regularización de observaciones con ejecutores → AC: dada rendición observada >15 días, cuando gestiono registro comunicaciones y fechas de seguimiento.
- **UCR-001** Contabilizar rendiciones aprobadas en SIGFE → AC: dado informe aprobado con FEA, cuando contabilizo registro en SIGFE y archivo expediente.
- **UCR-002** Ver dashboard de rendiciones pendientes por ejecutor → AC: dado rol UCR, cuando consulto veo ranking de ejecutores por mora con semáforo.
- **UCR-003** Generar alertas a ejecutores con rendición vencida → AC: dado ejecutor con rendición exigible pendiente, cuando se detecta se notifica y activa flag de bloqueo (Art. 18).

### Modelo de datos
`gore_financiero.convenio/estado_convenio/cuota_transferencia/garantia/rendicion`, `gore_integracion.sistema_externo/sincronizacion`, `gore_documental.documento/firma`.

### Flujos/UI
PD-CONV: IPR aprobada → Generar convenio → Estados → Cuotas → Garantías → Alertas.  
RTF: Registrar SISREC → Revisar rendiciones → Informe → Coordinar observaciones.  
UCR: Contabilizar SIGFE → Dashboard pendientes → Alertas bloqueo.

### APIs
POST `/convenios` · GET `/convenios` filtros · POST `/convenios/{id}/cuotas` · POST `/convenios/{id}/garantias` · POST `/rendiciones/{id}/revision` · POST `/rendiciones/{id}/contabilizar`.

### Pruebas
Suma cuotas = monto convenio; alertas 30/15/7; rendición observada >15d alerta/bloqueo; contabilizar requiere FEA.

### KPIs
Convenios en tiempo; tiempo elaboración→vigencia; % cuotas a tiempo; rendiciones observadas vs aprobadas; montos bloqueados Art.18.

---

## 4. MÓDULO EJECUCIÓN Y CRISIS
**Dominio:** `gore_ejecucion` · **Función:** Ejecutar · **Journeys:** J05, J06  
**Resumen:** Seguimiento ejecución, supervisión, compromisos, problemas, alertas y cierre.

### User Stories enriquecidas
- **SUP-001** Crear carpeta de seguimiento → AC: dada IPR asignada, cuando creo carpeta tengo espacio estructurado para visitas, informes, EP y comunicaciones.
- **SUP-002** Registrar visitas de terreno → AC: dada visita realizada, cuando registro adjunto fotos, notas y actualizo % avance estimado.
- **SUP-003** Revisar y validar informes de avance UT → AC: dado informe UT, cuando reviso apruebo/observo y actualizo estado en BIP.
- **SUP-004** Gestionar estados de pago → AC: dado EP presentado, cuando valido autorizo pago si avance físico corresponde al monto solicitado.
- **SUP-005** Alertar desviaciones relevantes → AC: dada desviación >10% en costo/plazo/calidad, cuando detecto genero alerta formal con recomendación.
- **SUP-006** Validar actas de recepción → AC: dada obra terminada, cuando valido recepción provisoria/definitiva autorizo último pago y cierre.
- **AR-001** Ver dashboard ejecutivo de cartera → AC: dado rol AR, cuando accedo veo total IPR activas, problemas, compromisos vencidos y alertas críticas con tendencias.
- **AR-002** Ver proyectos con nivel de alerta crítico → AC: dadas alertas activas, cuando filtro críticos veo lista con problema, responsable y días de antigüedad.
- **AR-003** Ver compromisos vencidos por división → AC: dados compromisos vencidos, cuando agrupo veo ranking de divisiones por mora con responsables.
- **AR-004** Crear compromiso durante reunión → AC: dada reunión de coordinación, cuando creo compromiso queda registrado con responsable, plazo e IPR vinculada.
- **AR-005** Ver historial de compromisos de una IPR → AC: dado código IPR, cuando consulto veo timeline de compromisos con estados y comentarios.
- **AR-006** Verificar compromisos completados → AC: dado compromiso en estado "Completado", cuando verifico lo cierro o devuelvo a "Pendiente" con comentario.
- **AR-007** Registrar problema detectado en entrevista → AC: dada entrevista, cuando registro problema selecciono tipo, impacto y creo compromiso de seguimiento.
- **AR-008** Generar resumen semanal para Gobernador → AC: dado período semanal, cuando genero obtengo PDF con tasa de cumplimiento, problemas y tendencias.
- **AR-009** Ver ranking de divisiones por tasa de cumplimiento → AC: dado período, cuando consulto veo ranking con métricas comparativas entre divisiones.
- **JD-001** Ver total de IPR, problemas y compromisos de mi división → AC: dada mi división, cuando accedo veo métricas agregadas de mi área.
- **JD-002** Ver encargados con métricas de compromisos → AC: dado mi equipo, cuando consulto veo compromisos pendientes/vencidos por persona con semáforo.
- **JD-003** Crear compromiso y asignar a encargado → AC: dada necesidad de acción, cuando creo compromiso asigno persona, plazo y prioridad.
- **JD-004** Reasignar compromiso entre encargados → AC: dado compromiso existente, cuando reasigno se notifica a ambos y se registra en historial.
- **JD-005** Registrar problema en IPR de mi división → AC: dada IPR con problema, cuando registro clasifico tipo, propongo solución y creo compromiso asociado.
- **JD-006** Cerrar problema con solución aplicada → AC: dado problema resuelto, cuando cierro documento solución, impacto y lección aprendida.
- **JD-007** Ver IPR compartidas y compromisos cruzados → AC: dada IPR interdivisional, cuando consulto veo responsables de cada división y compromisos asociados.
- **EO-001** Ver lista de compromisos con vencidos destacados → AC: dados mis compromisos, cuando accedo veo lista ordenada por fecha límite con semáforo y días restantes/vencidos.
- **EO-002** Marcar compromiso "En progreso" con comentarios → AC: dado compromiso asignado, cuando actualizo registro avance parcial con timestamp.
- **EO-003** Marcar compromiso "Completado" para verificación → AC: dado compromiso terminado, cuando completo pasa a bandeja de verificación del Jefe/AR con comentario obligatorio.
- **EO-004** Ver lista de IPR asignadas con alertas → AC: dadas mis IPR, cuando consulto veo cartera con semáforo y último avance reportado.
- **EO-005** Registrar informe de avance de IPR → AC: dada IPR en ejecución, cuando ingreso informe RTF es notificado y dashboard se actualiza.
- **EO-006** Registrar problema detectado en una IPR → AC: dado problema, cuando registro queda vinculado a la IPR y visible para jefatura.
- **EO-007** Ver ficha completa de una IPR → AC: dado código IPR, cuando consulto ficha veo convenios, cuotas, problemas e historial asociado.

### Modelo de datos
`gore_expediente.expediente`, `gore_ejecucion.avance_obra/estado_pago/alerta_ipr/problema_ipr/compromiso_operativo`, `gore_fsm.transicion`, `gore_eventos.evento`, `gore_inversion.iniciativa`.

### Flujos/UI
SUP: Bandeja → Carpeta → Visitas → EP → Alertas → Recepción.  
AR: Dashboard → Alertas críticas → Compromisos → Reportes.  
JD: División → Compromisos/Problemas → Asignar/Reasignar.  
EO: Mis compromisos → Avance/Problemas → Ficha IPR.

### APIs
POST `/ipr/{id}/carpeta` · POST `/ipr/{id}/avance` · POST `/ipr/{id}/estado-pago` · POST `/ipr/{id}/alerta` · POST `/compromisos` · PATCH `/compromisos/{id}`.

### Pruebas
EP rechaza si avance físico insuficiente; alerta crítica notifica AR/JD; compromiso “Completado” requiere comentario y verificación; timeline FSM actualizado.

### KPIs
% compromisos en plazo; tiempo resolución alertas; desviación físico/financiero; tiempo ciclo EP; problemas críticos abiertos.

---

## 5. MÓDULO CORE — Gobernanza y Fiscalización
**Dominio:** `gore_gobernanza` · **Función:** Coordinar · **Journey:** J13  
**Resumen:** Soporte sesiones CORE, votaciones, acuerdos y cumplimiento.

### User Stories enriquecidas
- **CR-001** Recibir carpeta digital de cartera para votación → AC: dada sesión CORE programada, cuando se publica carpeta recibo notificación con link a documentos digitales.
- **CR-002** Ver fichas resumen ejecutivo por IPR → AC: dada cartera CORE, cuando consulto IPR veo ficha 1 página con monto, ejecutor, beneficiarios, alineamiento ERD.
- **CR-003** Ver proyectos de mi provincia/circunscripción destacados → AC: dada mi circunscripción, cuando filtro veo cartera territorial con mapa y estadísticas por comuna.
- **CR-004** Ver mapa territorial de inversiones → AC: dada cartera regional, cuando accedo al mapa veo puntos geolocalizados con filtros por sector y estado.
- **CR-005** Ver dashboard de ejecución regional por comuna → AC: dado período, cuando consulto veo % ejecución por comuna con semáforo y ranking.
- **CR-006** Ver histórico de mis votaciones y acuerdos CORE → AC: dado mi perfil, cuando consulto historial veo votaciones por sesión, resultado y texto de acuerdo.
- **CR-007** Ver cumplimiento de acuerdos CORE → AC: dado un acuerdo, cuando consulto veo estado de cumplimiento con evidencia.
- **CR-008** Buscar IPR por código o nombre → AC: dado criterio de búsqueda, cuando busco obtengo resultados con link a ficha completa.
- **CR-009** Acceder a portal de transparencia (Glosa 16) → AC: dado rol CORE, cuando accedo veo información publicada según obligación legal.
- **CR-010** Exportar información a PDF/Excel → AC: dada cualquier vista, cuando exporto obtengo documento en formato seleccionado.
- **GR-001** Ver dashboard ejecutivo integrado con KPIs → AC: dado mi rol de Gobernador, cuando accedo veo panel unificado con indicadores ERD, ejecución presupuestaria y alertas críticas.
- **GR-002** Recibir alertas tempranas de desviaciones críticas → AC: dado evento crítico, cuando ocurre recibo notificación push con contexto y sugerencia de acción.
- **GR-003** Simular impacto de políticas en indicadores territoriales → AC: dado un escenario, cuando ejecuto simulación veo proyección de impacto en KPIs.
- **GR-004** Comparar indicadores entre comunas para priorizar inversiones → AC: dado conjunto de comunas, cuando comparo veo ranking con brechas territoriales.
- **GR-005** Firmar resoluciones y decretos con FEA → AC: dado acto preparado, cuando firmo queda registrado con FEA y pasa a siguiente etapa (DIPRES/CGR).
- **GR-006** Registrar audiencias, viajes y donativos (Ley de Lobby) → AC: dado evento de lobby, cuando registro queda en sistema para publicación en portal de transparencia.
- **GR-007** Ver estado de IPR críticas en War Room → AC: dada situación crítica, cuando accedo al War Room veo IPR críticas con contexto para decisión ejecutiva.

### Modelo de datos
`gore_gobernanza.sesion_core/acuerdo_core/votacion`, `gore_documental.documento/firma`, `gore_indicadores.indicador/meta`, `gore_territorial.comuna`, `gore_normativo.norma`.

### Flujos/UI
CR: Carpeta sesión → Fichas → Mapa/Ranking → Votar/Historial → Acuerdos → Exportar.  
GR: Dashboard → Alertas → Simulación/Comparar → Firmas → War Room.

### APIs
GET `/core/sesiones/{id}/carpeta` · GET `/core/ipr/{id}/ficha` · POST `/core/votaciones` · GET `/core/acuerdos/{id}/cumplimiento` · POST `/firmas`.

### Pruebas
Carpeta accesible sólo consejeros; voto con autenticación/timestamp; FEA obligatoria; vistas públicas no exponen datos reservados.

### KPIs
Tiempo publicación pre-sesión; % acuerdos en plazo; participación consejeros; brecha territorial inversión.

---

## 6. MÓDULO ADMINISTRACIÓN DEL SISTEMA
**Dominio:** `gore_seguridad`, `gore_actores` · **Función:** Transversal  
**Resumen:** Usuarios/roles/divisiones, importaciones, reglas de alerta, auditoría, backups.

### User Stories enriquecidas
- **AS-001** Crear y editar divisiones → AC: dada necesidad organizacional, cuando gestiono división queda registrada con nombre, descripción y jefe asignado.
- **AS-002** Crear usuarios con email, división y rol → AC: dado nuevo funcionario, cuando creo usuario queda habilitado con permisos según rol.
- **AS-003** Cambiar rol o división de un usuario → AC: dado usuario existente, cuando modifico se actualizan permisos y pertenencia automáticamente.
- **AS-004** Desactivar usuarios manteniendo historial → AC: dado usuario inactivo, cuando desactivo pierde acceso pero se mantiene registro histórico.
- **AS-005** Importar IPR masivamente desde Excel → AC: dado archivo Excel, cuando importo el sistema valida, reporta errores y carga registros correctos.
- **AS-006** Configurar reglas de alerta → AC: dado patrón a detectar, cuando configuro regla el sistema genera alertas automáticamente al cumplirse la condición.
- **AS-007** Ver logs de actividad del sistema → AC: dados criterios de filtro, cuando consulto logs veo actividad por usuario, acción y timestamp.
- **AS-008** Ver estado de backups y ejecutar backup manual → AC: dada necesidad de respaldo, cuando ejecuto backup se genera punto de restauración verificable.

### Modelo de datos
`gore_actores.persona/division/rol`, `gore_seguridad.permiso/log_auditoria`, `gore_inversion.iniciativa` (import), `gore_ejecucion.tipo_alerta_ipr`, `gore_integracion.sistema_externo` (backups).

### Flujos/UI
Divisiones → Usuarios/Roles → Reglas alerta → Logs → Backups; wizard de import IPR.

### APIs
POST `/admin/divisiones` · POST `/admin/usuarios` · PATCH `/admin/usuarios/{id}` · POST `/admin/import/ipr` · POST `/admin/alertas/reglas` · GET `/admin/logs`.

### Pruebas
Cambio rol revoca sesión y permisos; import idempotente con reporte de errores; regla dispara alerta al cumplirse; backup verificable.

### KPIs
Tiempo alta usuario; errores import; alertas activas; cobertura de logs; éxito/tiempo backup-restauración.

---

## 7. MÓDULO TERRITORIAL Y PLANIFICACIÓN
**Dominio:** `gore_territorial`, `gore_planificacion`, `gore_indicadores` · **Función:** Planificar · **Journeys:** J23, JX09  
**Resumen:** Brechas territoriales, alineamiento ERD, metas y ciclo ARI/PROPIR; autonomía regional.

### User Stories enriquecidas
- **DIPL-001** Ver brechas territoriales por comuna e indicador → AC: dado indicador y territorio, cuando consulto veo brecha vs meta regional con visualización geoespacial.
- **DIPL-002** Evaluar alineamiento de IPR con objetivos ERD → AC: dada IPR postulada, cuando evalúo veo mapeo a lineamientos ERD con score de alineamiento.
- **DIPL-003** Monitorear avance de metas ERD → AC: dado período, cuando consulto veo cumplimiento de metas con tendencia y proyección.
- **DIPL-004** Gestionar proceso ARI/PROPIR en Chileindica → AC: dado ciclo ARI, cuando proceso tengo herramientas para convocar, revisar y aprobar iniciativas sectoriales.
- **GORE-AUTO-01** Definir Política Regional propia → AC: dada necesidad regional, cuando promulgo política se crea instrumento normativo regional.
- **GORE-AUTO-02** Crear instrumentos de planificación específicos → AC: dada aprobación CORE, cuando configuro instrumento el sistema permite seguimiento de metas propias.

### Modelo de datos
`gore_territorial.brecha_territorial`, `gore_planificacion.objetivo_estrategico/instrumento_planificacion`, `gore_indicadores.meta/medicion`, `L2.Norma.Politica_Regional`, `L3.Planificacion.Instrumento_Propio`.

### Flujos/UI
Mapa brechas → Ranking → Alineamiento IPR → Metas/proyección → ARI/PROPIR; Política regional → Instrumentos propios → Seguimiento.

### APIs
GET `/territorio/brechas` · POST `/ipr/{id}/alineamiento-erd` · GET `/indicadores/metas` · POST `/ari/propir`.

### Pruebas
Brecha = meta − valor; alineamiento con score y rationale; alerta si meta < umbral; fases ARI registradas.

### KPIs
% IPR alineadas ERD; reducción brechas; cumplimiento metas; tiempo ciclo ARI/PROPIR.

---

## 8. MÓDULO CIES — Centro Integrado de Emergencia y Seguridad
**Dominio:** `gore_seguridad`, `gore_territorial` · **Función:** Ejecutar + Coordinar · **Journey:** J20  
**Resumen:** Monitoreo en tiempo real, incidentes, coordinación con enlaces y contingencias.

### User Stories enriquecidas
- **CIES-OP-01** Monitorear cámaras en tiempo real y detectar incidentes → AC: dado feed de cámaras, cuando detecto anomalía clasifico por prioridad y activo protocolo.
- **CIES-OP-02** Seguir trayectorias de vehículos/personas → AC: dado incidente activo, cuando sigo trayectoria veo mapa con movimientos y puedo alertar unidades.
- **CIES-SUP-01** Asumir gestión de incidentes críticos → AC: dado incidente crítico, cuando asumo tengo herramientas de coordinación con Carabineros/PDI/Bomberos.
- **CIES-SUP-02** Activar planes de contingencia → AC: dado evento mayor, cuando activo contingencia se ejecutan protocolos predefinidos.
- **CIES-ENL-01** Recibir alertas CIES y coordinar respuesta → AC: dada alerta CIES, cuando recibo veo contexto y puedo confirmar respuesta en terreno.

### Modelo de datos
`gore_seguridad.incidente/protocolo`, `gore_territorial.geolocalizacion`, `gore_integracion.sistema_externo`.

### Flujos/UI
Feeds → Detección → Gestión incidente → Tracking → Protocolos/Contingencia → Coordinación enlaces.

### APIs
POST `/incidentes` · PATCH `/incidentes/{id}` · POST `/incidentes/{id}/enlaces` · POST `/protocolos/{id}/activar`.

### Pruebas
Incidente crítico notifica enlaces; contingencia ejecuta checklist; tracking con historial.

### KPIs
Tiempo detección→asignación; tiempo respuesta; incidentes críticos resueltos; disponibilidad feeds.

---

## 9. MÓDULO IDE — Infraestructura de Datos Geoespaciales
**Dominio:** `gore_geoespacial`, `gore_territorial` · **Función:** Planificar · **Journey:** J21  
**Resumen:** Política geoespacial, modelado/publicación de capas, metadatos, federación IDE Chile.

### User Stories enriquecidas
- **IDE-01** Definir política de información geoespacial del GORE → AC: dado rol IDE, cuando defino política queda documentada y socializada.
- **IDE-02** Coordinar federación de catálogos con IDE Chile (CSW) → AC: dado catálogo local, cuando federo las capas aparecen en IDE Chile.
- **UGIT-01** Modelar datos y catálogo de objetos según ISO 19110 → AC: dada una capa nueva, cuando modelo cumple estándar ISO.
- **UGIT-02** Crear metadatos ISO 19115-1 (Perfil Chileno) → AC: dada capa modelada, cuando documento tiene metadatos completos.
- **UGIT-03** Publicar servicios WMS/WFS/WCS en Geonodo → AC: dada capa documentada, cuando publico queda disponible vía APIs OGC.
- **PFS-01** Validar contenido temático de capas sectoriales → AC: dada capa sectorial, cuando valido certifico calidad temática.

### Modelo de datos
`gore_geoespacial.capa/metadato/calidad`, `gore_integracion.api` (OGC/Geonodo), `gore_normativo.politica`.

### Flujos/UI
Política → Modelar capa → Metadatos → Publicar servicio → Federar CSW → Validación temática.

### APIs
POST `/ide/politica` · POST `/ide/capas` · POST `/ide/capas/{id}/metadatos` · POST `/ide/capas/{id}/publicar` · POST `/ide/catalogo/federar`.

### Pruebas
Metadatos pasan validador; publicación falla sin metadatos; federación muestra en IDE Chile; control de acceso aplicado.

### KPIs
Capas con metadatos completos; tiempo modelo→publicación; % capas federadas; incidencias de calidad.

---

## 10. MÓDULO TIC — Gobernanza y Transformación Digital
**Dominio:** `gore_tic`, `gore_seguridad` · **Función:** Coordinar + Normar · **Journeys:** J22, JX08  
**Resumen:** Gobierno TDE, interoperabilidad, privacidad, ciberseguridad, portafolio TIC.

### User Stories enriquecidas
- **CTD-01** Monitorear avance de implementación TDE → AC: dado plan TDE, cuando consulto veo % avance por componente.
- **CTD-02** Gestionar interoperabilidad con otros órganos → AC: dada necesidad de integración, cuando gestiono registro acuerdos en Red Estado.
- **DPO-01** Gestionar solicitudes de derechos ARCO → AC: dada solicitud ARCO, cuando proceso respondo en plazo legal según Ley 21.719.
- **DPO-02** Evaluar impacto de privacidad en proyectos → AC: dado proyecto nuevo, cuando evalúo emito informe de impacto y riesgos.
- **CISO-01** Monitorear estado de seguridad de sistemas → AC: dado panel de seguridad, cuando consulto veo alertas y cumplimiento de controles.
- **CISO-02** Gestionar incidentes de ciberseguridad → AC: dado incidente, cuando gestiono activo protocolo y registro acciones de contención.
- **PMOTIC-01** Mantener inventario de proyectos TIC → AC: dado portafolio TIC, cuando consulto veo estado, riesgos y dependencias de cada proyecto.
- **JPTIC-01** Gestionar proyecto TIC → AC: dado proyecto asignado, cuando gestiono tengo herramientas de gestión de equipo, cronograma y presupuesto.

### Modelo de datos
`gore_indicadores.indicador`, `gore_integracion.acuerdo`, `gore_normativo.norma`, `gore_seguridad.incidente/riesgo`, `gore_workflow.proyecto`.

### Flujos/UI
Plan TDE → Interoperabilidad → ARCO/PIA → Seguridad/Incidentes → PMO → Proyecto.

### APIs
GET `/tde/avance` · POST `/interoperabilidad/acuerdos` · POST `/privacidad/solicitudes` · POST `/privacidad/pia` · POST `/seguridad/incidentes` · GET `/pmo/proyectos`.

### Pruebas
ARCO fuera de plazo alerta; PIA con riesgo crítico bloquea; incidente registra protocolo completo.

### KPIs
% avance TDE; integraciones activas; tiempo respuesta ARCO; MTTR; % proyectos on-track.

---

## 11. MÓDULO CUMPLIMIENTO — Transparencia, Lobby y Probidad
**Dominio:** `gore_normativo`, `gore_documental` · **Función:** Normar · **Journeys:** J08, J11  
**Resumen:** Transparencia activa, solicitudes de información, lobby y sujetos pasivos.

### User Stories enriquecidas
- **TRANSP-01** Verificar actualización mensual de transparencia activa → AC: dado checklist TA, cuando verifico confirmo publicación de los 27 antecedentes obligatorios.
- **TRANSP-02** Gestionar solicitudes de acceso a información → AC: dada solicitud, cuando gestiono respondo en 20+10 días hábiles registrando el ciclo completo.
- **LOBBY-01** Verificar registros de audiencias de autoridades → AC: dado período, cuando verifico confirmo registros en leylobby.gob.cl.
- **LOBBY-02** Coordinar designación de sujetos pasivos → AC: dado cambio organizacional, cuando actualizo la lista de sujetos pasivos queda vigente.

### Modelo de datos
`gore_normativo.norma`, `gore_documental.solicitud`, `gore_actores.persona` (sujetos pasivos).

### Flujos/UI
Checklist TA → Solicitudes AI → Lobby/registros/sujetos pasivos → Alertas plazos.

### APIs
GET `/transparencia/checklist` · POST `/transparencia/solicitudes` · GET `/lobby/registros` · POST `/lobby/sujetos-pasivos`.

### Pruebas
Plazo AI vencido alerta roja; sujetos pasivos desactualizados bloquean publicación.

### KPIs
Cumplimiento TA mensual; tiempo respuesta AI; % registros lobby al día.

---

## 12. MÓDULO MUNICIPAL — Actores de Ejecución Local
**Dominio:** `gore_actores`, `gore_inversion` · **Función:** Ejecutar · **Journeys:** J05, J06, J14  
**Resumen:** Soporte municipal para formular, ejecutar y rendir.

### User Stories enriquecidas
- **UF-01** Consultar guías y requisitos por mecanismo → AC: dado mecanismo seleccionado, cuando consulto veo documentación requerida para postular.
- **UF-02** Determinar vía de financiamiento usando árbol de decisión → AC: dadas características del proyecto, cuando uso el wizard obtengo recomendación fundamentada de track.
- **UF-03** Verificar elegibilidad FRIL → AC: dado proyecto, cuando verifico conozco si califica FRIL y qué requisitos específicos aplican.
- **UTR-01** Coordinar reunión de inicio con GORE → AC: dado convenio firmado, cuando solicito reunión se coordina con supervisor GORE y se registra.
- **UTR-02** Reportar avance periódico a Supervisor GORE → AC: dado hito cumplido, cuando reporto supervisor es notificado y puede validar.
- **UTR-03** Presentar rendición final en SISREC → AC: dado proyecto terminado, cuando rindo RTF recibe para revisión y aprobación.

### Modelo de datos
`gore_documental.plantilla`, `codigo_track`, `gore_normativo.restriccion`, `gore_workflow.reunion`, `gore_ejecucion.avance_obra`, `gore_financiero.rendicion`.

### Flujos/UI
Guías/Wizard → Elegibilidad FRIL → Reunión inicio → Reportes avance → Rendición final SISREC.

### APIs
GET `/municipal/guias` · POST `/wizard/financiamiento` · POST `/reuniones` · POST `/rendiciones/final`.

### Pruebas
Wizard coherente; rendición final requiere cierre hitos; supervisor valida reportes.

### KPIs
Tasa admisibilidad municipal; tiempo convenio→inicio; cumplimiento reportes; tiempos rendición final.

---

## 13. MÓDULO GOBIERNO CENTRAL — Control y Evaluación
**Dominio:** `gore_integracion`, `gore_evaluacion` · **Función:** Financiar + Normar · **Journeys:** JX01, JX03  
**Resumen:** Interoperación con MDSF, DIPRES/SES, CGR, CPLT, TCP.

### User Stories enriquecidas
- **MDSF-01** Recibir postulación IDI del GORE → AC: dada IPR enviada, cuando recibo en MDSF inicia plazo de evaluación.
- **MDSF-02** Emitir RATE para comunicar evaluación → AC: dado análisis completado, cuando emito RATE (RS/FI/OT/AD) GORE es notificado.
- **DIPSES-01** Evaluar Formulario de Diseño MML de PPR Glosa 06 → AC: dado formulario recibido, cuando evalúo emito RF o solicito correcciones.
- **CGR-01** Verificar rendiciones en SISREC → AC: dado acceso a SISREC, cuando verifico puedo revisar transacciones y adjuntos para fiscalizar uso de fondos.
- **CGR-02** Fiscalizar oportunidad e integridad de DIP → AC: dado acceso a sistema DIP, cuando fiscalizo puedo detectar incumplimientos de probidad.
- **CPLT-01** Requerir información al GORE para resolver amparo → AC: dado amparo presentado, cuando requiero GORE debe responder en plazo legal.
- **TCP-01** Requerir expediente de licitación impugnada → AC: dado reclamo presentado, cuando requiero entonces GORE entrega antecedentes de licitación.

### Modelo de datos
`gore_evaluacion.evaluacion_mdsf/resultado_rate`, `gore_integracion.sincronizacion`, `gore_financiero.rendicion`, `gore_documental.expediente/solicitud`.

### Flujos/UI
Inbox requerimientos → RATE/RF → Notificación → Fiscalización CGR/SISREC → Respuestas CPLT/TCP.

### APIs
POST `/mdsf/rate` · POST `/ses/rf` · GET `/sisrec/rendiciones` · POST `/requerimientos`.

### Pruebas
RATE notifica y actualiza estado; requerimientos con plazo y alerta; acceso CGR auditado.

### KPIs
Tiempos RATE/RF; % requerimientos en plazo; hallazgos CGR; SLA CPLT/TCP.

---

## 14. MÓDULO SECTORIAL — Actores RIS Específicos
**Dominio:** `gore_evaluacion`, `gore_normativo` · **Función:** Planificar · **Journeys:** JX01  
**Resumen:** Revisión sectorial RIS por organismo (IND, CMN, MINCAP), emisión de pronunciamientos sectoriales y notificación al GORE.

### User Stories enriquecidas (por tipo de usuario)

#### Profesional IND
- **IND-01** Revisar proyectos de infraestructura deportiva  
  - AC: Dado un **proyecto deportivo** ingresado al RIS; Cuando el profesional IND revisa la ficha con antecedentes técnicos y normativos; Entonces **emite pronunciamiento técnico sectorial** (favorable/observado/no favorable) que queda registrado, versionado y trazable para el GORE.

#### Profesional CMN
- **CMN-01** Revisar proyectos en inmuebles patrimoniales  
  - AC: Dado un **proyecto en zona o inmueble patrimonial**; Cuando el profesional CMN revisa antecedentes y normativa de protección aplicable; Entonces **emite autorización o denegación fundada**, registrando observaciones y condiciones para la intervención.

#### Profesional MINCAP (Cultura)
- **CULTURA-01** Revisar iniciativas culturales FNDR  
  - AC: Dado un **proyecto cultural** financiado vía FNDR; Cuando el profesional MINCAP revisa la iniciativa; Entonces **valida coherencia con la política cultural sectorial**, registrando su pronunciamiento y recomendaciones.|

### Modelo de datos
`gore_evaluacion.evaluacion_sectorial` (IND/CMN/MINCAP), `gore_evaluacion.revision_sectorial`, `gore_normativo.criterio_sectorial`.

### Flujos/UI
Inbox sectorial (por organismo) → Seleccionar proyecto → Revisar antecedentes → Registrar pronunciamiento sectorial → Notificación al GORE.

### APIs
POST `/ris/revisiones` { iprId, organismo, resultado, observaciones }.

### Pruebas
- Cada revisión sectorial exige **resultado** y **fundamento**.  
- Notificación al GORE incluye organismo, resultado y plazo de respuesta (si aplica).

### KPIs
- Tiempo promedio de revisión sectorial por organismo.  
- % proyectos con observaciones sectoriales.  
- Cumplimiento de SLA de respuesta.

---

## 15. MÓDULO L0 PERSONAS — Gestión del Capital Humano
**Dominio:** `L0_Homeostasis.Gestion_Personas` · **Función:** Transversal (Homeostasis organizacional)  
**Journeys:** Ciclo de vida funcionario  
**Resumen:** Gestión de ausentismo, remuneraciones, calificaciones, selección, capacitación e interacción funcionario–GDP.

### User Stories enriquecidas (por tipo de usuario)

#### 15.1 Profesional GDP — Gestión de Personas
- **GDP-AUS-01** Gestionar feriado legal verificando saldo  
  - AC: Dado una solicitud de feriado legal; Cuando el profesional GDP consulta la **cuenta corriente de días**; Entonces puede **aprobar o rechazar** con fundamento y se actualiza el saldo del funcionario.
- **GDP-AUS-02** Registrar licencias médicas electrónicas  
  - AC: Dada una licencia IMED/Medipass; Cuando la registro; Entonces el **estado del funcionario** cambia (con/sin goce según resolución COMPIN/ISAPRE) y se contabiliza en ausentismo.
- **GDP-AUS-03** Gestionar permisos administrativos (máx. 6 días/año)  
  - AC: Dada una solicitud; Cuando verifico saldo; Entonces apruebo sólo si no supera el tope anual y registro consumo.
- **GDP-AUS-04** Tramitar comisiones de servicio/cometidos  
  - AC: Dado un requerimiento; Cuando tramito; Entonces se genera **resolución exenta**, se calcula viático (si corresponde) y se registra la ausencia.
- **GDP-AUS-05** Registrar accidentes de trabajo (DIAT) y coordinar Mutual  
  - AC: Dado un accidente notificado; Cuando registro; Entonces genero **DIAT**, derivo a Mutual y se marca como accidente laboral o de trayecto.
- **GDP-REM-01** Calcular liquidaciones mensuales  
  - AC: Dado un período; Cuando proceso; Entonces se generan liquidaciones con haberes, descuentos y líquido aplicando **Escala Única de Sueldos** y asignaciones.
- **GDP-REM-02** Generar planilla Previred  
  - AC: Dadas liquidaciones aprobadas; Cuando genero; Entonces obtengo archivo Previred con cotizaciones previsionales.
- **GDP-REM-03** Emitir certificados de renta  
  - AC: Dado un año tributario; Cuando genero; Entonces cada funcionario tiene certificado disponible para Operación Renta.
- **GDP-REM-04** Gestionar horas extraordinarias  
  - AC: Dadas autorizaciones Formularios N°1 y N°2; Cuando registro; Entonces acumulo tiempo compensado y lo dejo disponible para uso/pago.
- **GDP-CAL-01** Gestionar proceso de calificación anual  
  - AC: Dado el período calificatorio; Cuando coordino; Entonces se completan precalificaciones, Junta y cierre en el ciclo sept–nov.
- **GDP-CAL-02** Registrar precalificaciones de jefes directos  
  - AC: Dado un funcionario; Cuando su jefe directo precalifica; Entonces quedan notas por subfactor y comentarios, disponibles para la Junta.
- **GDP-CAL-03** Registrar anotaciones de mérito/demérito  
  - AC: Dado un evento relevante; Cuando registro anotación; Entonces queda en **hoja de vida** y se considera en calificación.
- **GDP-SEL-01** Gestionar concursos públicos  
  - AC: Dado un cargo vacante; Cuando proceso concurso; Entonces ejecuto fases (bases, postulación, evaluación, nombramiento) con trazabilidad.
- **GDP-SEL-02** Ejecutar programa de inducción  
  - AC: Dado un nuevo ingreso; Cuando activo inducción; Entonces se ejecutan fases de bienvenida, información institucional y formación en el cargo.
- **GDP-CAP-01** Gestionar Plan Anual de Capacitación  
  - AC: Dado un plan aprobado; Cuando gestiono; Entonces registro cursos, asistentes y certificados, y puedo medir cobertura.

#### 15.2 Funcionario GORE
- **FUNC-AUS-01** Solicitar feriado legal electrónicamente  
  - AC: Dado mi saldo de feriado; Cuando solicito; Entonces veo saldo disponible, envío solicitud a jefatura y queda en estado pendiente/aprobado.
- **FUNC-AUS-02** Solicitar permiso administrativo  
  - AC: Dado mi saldo de permisos; Cuando solicito; Entonces la jefatura recibe para autorización y el saldo se actualiza si se aprueba.
- **FUNC-REM-01** Ver mi liquidación de sueldo mensual  
  - AC: Dado un mes pagado; Cuando consulto; Entonces veo detalle de haberes y descuentos.
- **FUNC-CAP-01** Inscribirme en cursos del Plan de Capacitación  
  - AC: Dado el catálogo de cursos; Cuando me inscribo; Entonces queda registrada mi participación y se refleja en el plan.

### Modelo de datos
`L0.Ausentismo.feriado_legal/licencia_medica/permisos/comision_servicio/accidente_trabajo`, `L0.Remuneraciones.*`, `L0.Calificaciones.*`, `L0.Desarrollo_Personas.*`, además de `persona/rol/competencia/plan_capacitacion/evaluacion_desempeno/induccion`.

### Flujos/UI
Profesional GDP: Ausentismo → Remuneraciones → Calificaciones → Selección → Capacitación.  
Funcionario: Autoservicio de solicitudes (feriado/permiso), consulta de liquidaciones, inscripción a cursos.

### APIs
POST `/personas` · POST `/capacitacion/planes` · POST `/desempeno/evaluaciones` · POST `/induccion` · endpoints específicos de ausentismo y remuneraciones (feriados, licencias, permisos, DIAT, liquidaciones, Previred, horas extra).

### Pruebas
- Alta crea usuario y roles correctos; baja revoca accesos.  
- Tope de permisos administrativos (6 días/año) se respeta.  
- Procesos de calificación y capacitación registran todas las etapas.  
- Liquidaciones cuadran con reglas de remuneraciones.

### KPIs
- Tiempo de alta de funcionario; uso de feriados y permisos vs saldos; cobertura de calificaciones; % funcionarios con capacitación ejecutada.

---

## 16. MÓDULO L0 ACTIVOS — Gestión de Bienes y Servicios
**Dominio:** `L0_Homeostasis.Gestion_Activos_Servicios` · **Función:** Transversal (Homeostasis organizacional)  
**Journeys:** Ciclo de compras, Inventario, Activo fijo  
**Resumen:** Plan anual de compras, licitaciones, bodegas, activo fijo, mantención y flota vehicular.

### User Stories enriquecidas (por tipo de usuario)

#### 16.1 Profesional Abastecimiento (ABS)
- **ABS-COM-01** Plan Anual de Compras alineado a presupuesto  
  - AC: Dado un presupuesto aprobado; Cuando configuro el plan; Entonces obtengo un **calendario de compras** por programa/subtítulo.
- **ABS-COM-02** Tramitar solicitudes de compra verificando CDP  
  - AC: Dado un requerimiento; Cuando verifico CDP; Entonces puedo iniciar licitación o trato directo y se registra el compromiso.
- **ABS-COM-03** Publicar licitaciones en Mercado Público  
  - AC: Dado un proceso aprobado; Cuando publico; Entonces las **bases técnicas** quedan disponibles para proveedores.
- **ABS-COM-04** Evaluar ofertas y adjudicar  
  - AC: Dadas ofertas recibidas; Cuando evalúo; Entonces adjudico al mejor evaluado según criterios técnico–económicos y registro resolución.
- **ABS-COM-05** Emitir órdenes de compra  
  - AC: Dada una adjudicación; Cuando emito OC en Mercado Público; Entonces se compromete el gasto y el proveedor puede entregar.
- **ABS-COM-06** Gestionar contratos con hoja de vida y garantías  
  - AC: Dado un contrato vigente; Cuando gestiono; Entonces controlo hitos, garantías y alertas de vencimiento/renovación.

#### 16.2 Encargado de Bodega
- **ABS-BOD-01** Registrar ingresos por orden de compra  
  - AC: Dado un producto recepcionado; Cuando registro; Entonces el **stock** aumenta y se genera documento de ingreso.
- **ABS-BOD-02** Despachar solicitudes de consumo  
  - AC: Dada una solicitud aprobada; Cuando despacho; Entonces el stock disminuye y el receptor firma conformidad.
- **ABS-BOD-03** Toma de inventario físico  
  - AC: Dado un inventario planificado; Cuando ejecuto conteo; Entonces genero ajustes por diferencia y acta de inventario.

#### 16.3 Profesional Control Patrimonial
- **ABS-AF-01** Alta de bienes de activo fijo  
  - AC: Dado un bien recepcionado; Cuando doy alta; Entonces se codifica, se asigna responsable y se inicia depreciación.
- **ABS-AF-02** Traslado de bienes entre unidades  
  - AC: Dada una solicitud de traslado; Cuando proceso; Entonces cambio ubicación y responsable con acta respaldatoria.
- **ABS-AF-03** Baja de bienes por obsolescencia/deterioro/pérdida  
  - AC: Dado un bien inutilizable; Cuando tramito baja; Entonces genero resolución, actualizo inventario y registro causal.
- **ABS-AF-04** Inventario físico anual de activo fijo  
  - AC: Dado el período anual; Cuando ejecuto inventario; Entonces genero informe con diferencias y acciones correctivas.

#### 16.4 Profesional Servicios Generales
- **ABS-MAN-01** Órdenes de trabajo de mantención  
  - AC: Dado un activo con necesidad; Cuando genero OT; Entonces se asigna técnico, se ejecuta mantención y se registra resultado.

#### 16.5 Encargado de Flota
- **ABS-FLO-01** Gestionar solicitudes de uso de vehículos  
  - AC: Dada una solicitud; Cuando evalúo; Entonces asigno vehículo y conductor, registrando fechas y propósito.
- **ABS-FLO-02** Controlar kilometraje, combustible y mantenciones  
  - AC: Dado un vehículo asignado; Cuando registro uso; Entonces mantengo una **bitácora** actualizada para gestión de flota.

### Modelo de datos
`L0.Ciclo_Compras.*`, `L0.Bodegas.*`, `L0.Activo_Fijo.*`, `L0.Mantenimiento.*`, `L0.Flota_Vehicular.*`, además de `activo/contrato/garantia/mantencion/ubicacion/responsable`.

### Flujos/UI
Plan Anual de Compras → Procesos de compra (requerido → en_proceso → adjudicado → comprometido) → Bodega (ingreso/egreso/inventario) → Activo fijo (alta/traslado/baja/inventario) → Mantención → Flota vehicular.

### APIs
POST `/activos` · POST `/activos/{id}/mantenciones` · POST `/activos/{id}/baja` · endpoints de compras (planes, solicitudes, licitaciones, OC) y bodega.

### Pruebas
- Baja exige autorización y reflejo contable.  
- Mantención vencida genera alerta.  
- Stock e inventario físico se concilian.

### KPIs
- % mantenciones en plazo; activos con garantía vigente; precisión de inventario; rotación de stock; utilización de flota.

---

## 17. MÓDULO L0 BIENESTAR — Beneficios Funcionarios
**Dominio:** `L0_Homeostasis.Gestion_Bienestar` · **Función:** Transversal (Homeostasis organizacional)  
**Journeys:** Afiliación, Beneficios, Préstamos  
**Resumen:** Servicio de Bienestar: afiliaciones, grupo familiar, bonificaciones, subsidios, préstamos, convenios, SSO, autoservicio de socios.

### User Stories enriquecidas (por tipo de usuario)

#### 17.1 Profesional Bienestar (BIEN)
- **BIEN-AF-01** Gestionar afiliaciones de funcionarios  
  - AC: Dado un funcionario activo; Cuando afilio; Entonces queda como socio con descuento de cuota mensual en remuneraciones.
- **BIEN-AF-02** Gestionar grupo familiar de socios  
  - AC: Dado un socio activo; Cuando registro cargas; Entonces el grupo familiar queda habilitado para beneficios.
- **BIEN-BON-01** Procesar bonificación médica  
  - AC: Dado un gasto médico documentado; Cuando proceso; Entonces calculo bonificación según tope anual y liquido pago.
- **BIEN-SUB-01** Tramitar subsidios por eventos  
  - AC: Dado un evento (natalidad, matrimonio, fallecimiento, escolaridad); Cuando tramito; Entonces entrego subsidio según política.
- **BIEN-PRE-01** Evaluar y otorgar préstamos  
  - AC: Dada una solicitud; Cuando evalúo; Entonces verifico capacidad de endeudamiento y genero pagaré si corresponde.
- **BIEN-PRE-02** Descuento de cuotas en planilla  
  - AC: Dado un préstamo vigente; Cuando proceso el mes; Entonces se descuenta la cuota automáticamente en remuneraciones.
- **BIEN-CON-01** Administrar convenios con terceros  
  - AC: Dado un convenio suscrito; Cuando administro; Entonces socios pueden inscribirse y pagar vía descuento en planilla.
- **BIEN-SSO-01** Coordinar con Mutual de Seguridad  
  - AC: Dado un accidente laboral/trayecto; Cuando coordino; Entonces Mutual atiende al funcionario y se gestiona subsidio.
- **BIEN-SSO-02** Apoyar al CPHS en investigación de accidentes  
  - AC: Dado un accidente; Cuando investigo con CPHS; Entonces genero informe con recomendaciones de prevención.

#### 17.2 Socio Bienestar (Funcionario)
- **SOC-BON-01** Solicitar bonificación médica electrónicamente  
  - AC: Dado un gasto de salud; Cuando solicito adjuntando boletas/facturas; Entonces Bienestar procesa y paga según tope.
- **SOC-PRE-01** Solicitar préstamo  
  - AC: Dado mi saldo y capacidad; Cuando solicito; Entonces veo condiciones y presento solicitud para evaluación.
- **SOC-CTA-01** Ver mi cuenta corriente de socio  
  - AC: Dado mi perfil; Cuando consulto; Entonces veo beneficios otorgados, préstamos vigentes y saldos.

### Modelo de datos
`L0.Bienestar.*` (Afiliacion, Grupo_Familiar, Bonificaciones_Medicas, Subsidios, Prestamos, Convenios_Terceros, SSO.*), `beneficio/convocatoria/postulacion/asignacion/presupuesto_bienestar`, `L0.Bienestar.Cuenta_Corriente_Socio`.

### Flujos/UI
Afiliación → Registro grupo familiar → Beneficios (bonos/subsidios/préstamos) → Descuentos en remuneraciones → Cuenta corriente del socio.  
SSO: Registro accidente → Coordinación Mutual/CPHS → Cierre caso.

### APIs
POST `/bienestar/postulaciones` · POST `/bienestar/asignaciones` · POST `/bienestar/afiliaciones` · POST `/bienestar/prestamos` · GET `/bienestar/cuenta-corriente`.

### Pruebas
- Afiliación exige funcionario activo; grupo familiar consistente.  
- Bonificación y subsidios respetan topes y políticas.  
- Préstamos descuentan cuotas correctamente en planilla.  
- Cuenta corriente refleja saldos y movimientos históricos.

### KPIs
- Cantidad de socios activos; ejecución presupuestaria de bienestar; tiempos de respuesta a solicitudes; morosidad en préstamos.

---

## 18. MÓDULO L4 COMPETENCIAS — Transferencia de Competencias
**Dominio:** `L4_Competencias`, `gore_gobernanza` · **Función:** Normar + Planificar · **Journeys:** J10 Transferencia Competencias  
**Resumen:** Solicitud, evaluación y seguimiento de traspaso de competencias desde Gobierno Central al GORE.

### User Stories enriquecidas (por tipo de usuario)

#### 18.1 Autoridades y Planificación
- **GORE-COMP-01** Solicitar transferencia de competencia (Art. 114 CPR)  
  - AC: Dado un **estudio justificativo**; Cuando el Gobernador Regional firma la solicitud; Entonces se genera y envía oficio a Presidencia y SUBDERE, quedando registro del expediente de transferencia.
- **GORE-COMP-02** Aprobar solicitud de competencia en CORE  
  - AC: Dada una propuesta del Gobernador; Cuando el Consejero Regional vota favorablemente y se alcanza **mayoría absoluta**; Entonces se certifica el acuerdo CORE que habilita la solicitud formal.
- **GORE-COMP-03** Elaborar informe de capacidad financiera y administrativa  
  - AC: Dado un análisis interno; Cuando el Profesional DIPLADE elabora el informe; Entonces se genera un anexo técnico que acredita la aptitud del GORE para ejercer la competencia.
- **GORE-COMP-04** Monitorear estado de la solicitud en Comité Interministerial  
  - AC: Dada una solicitud enviada; Cuando el Jefe DIPLADE consulta; Entonces ve días transcurridos (plazo 6 meses) y la etapa en nivel central (en estudio, en Comité, resuelta), con alertas de vencimiento.

### Modelo de datos
`L4.Competencia.Solicitud`, `L4.Competencia.Informe_Capacidad`, `L4.Competencia.Transferencia`, `gore_gobernanza.acuerdo_core`.

### Flujos/UI
Estudio justificativo → Aprobación CORE → Envío solicitud → Comité Interministerial → Resultado y puesta en marcha de la competencia.

### APIs
POST `/competencias/planes` · POST `/competencias/solicitudes` · GET `/competencias/solicitudes/{id}` · PATCH `/competencias/planes/{id}`.

### Pruebas
- No se puede enviar solicitud sin acuerdo CORE y estudio justificativo.  
- Plazo de 6 meses del Comité Interministerial monitoreado con alertas.  
- Informes de capacidad se vinculan a la competencia correspondiente.

### KPIs
- Número de competencias solicitadas y transferidas; tiempo promedio de resolución; grado de cumplimiento de condiciones de capacidad.

---

## 19. MÓDULO Lω EVOLUCIÓN — Gestión del Cambio
**Dominio:** `Lomega_Evolucion`, `gore_tic` · **Función:** Transversal (Meta-Bucle) · **Journeys:** J23 Planificación GORE 4.0  
**Resumen:** Evolución del modelo ontológico, medición de deuda técnica categórica y migraciones entre versiones, como base del refactoring continuo del GORE OS.

### User Stories enriquecidas (por tipo de usuario)

#### 19.1 Gestión del Cambio y Deuda Técnica
- **GORE-EVO-01** Versionar esquema ontológico (v4.x)  
  - AC: Dado un cambio semántico en la ontología; Cuando el Administrador del Sistema registra una nueva versión; Entonces el sistema **versiona entidades afectadas** y mantiene trazabilidad entre versiones.
- **GORE-EVO-02** Visualizar métricas de Deuda Técnica Categórica  
  - AC: Dado un dashboard de evolución; Cuando el Encargado TDE consulta; Entonces ve **score de deuda técnica**, módulos/ontologías afectadas y prioridades de refactor.
- **GORE-EVO-03** Gestionar migraciones de datos entre versiones de esquema  
  - AC: Dada una actualización del modelo; Cuando el Administrador ejecuta una migración; Entonces los datos antiguos se adaptan al nuevo esquema con validación de integridad y plan de rollback.

### Modelo de datos
`Lomega.Version_Schema`, `Lomega.Deuda_Tecnica`, `Lomega.Migracion`, además de `roadmap/cambio/release/adopcion/issue`.

### Flujos/UI
Diseño de nueva versión ontológica → Registro versión → Plan de migración → Ejecución (prueba + producción) → Medición de deuda técnica y adopción.

### APIs
POST `/evolucion/roadmap` · POST `/evolucion/cambios` · POST `/evolucion/releases` · GET `/evolucion/adopcion` · POST `/evolucion/version-schema` · POST `/evolucion/migraciones`.

### Pruebas
- Toda migración debe tener **rollback plan** y validación de integridad.  
- Cambios en el esquema se reflejan en versiones y trazabilidad.  
- Métricas de deuda técnica se recalculan tras refactors.

### KPIs
- % roadmap de evolución cumplido; cantidad de migraciones exitosas sin rollback; variación del score de deuda técnica; adopción por rol; NPS interno.

---

## Anexo A. Matriz ampliada de trazabilidad

| Módulo           | Stories | Críticas | Altas  | Medias |
| ---------------- | ------- | -------- | ------ | ------ |
| IPR              | 32      | 22       | 8      | 2      |
| Presupuesto      | 12      | 8        | 4      | 0      |
| Convenios        | 12      | 8        | 4      | 0      |
| Ejecución/Crisis | 35      | 24       | 9      | 2      |
| CORE/Gobernanza  | 17      | 10       | 5      | 2      |
| Administración   | 8       | 1        | 6      | 1      |
| Territorial      | 4       | 1        | 3      | 0      |
| CIES             | 5       | 3        | 2      | 0      |
| IDE/GIS          | 6       | 0        | 6      | 0      |
| TIC/TDE          | 8       | 1        | 7      | 0      |
| Cumplimiento     | 4       | 1        | 2      | 1      |
| Municipal        | 6       | 3        | 3      | 0      |
| Gob. Central     | 7       | 4        | 3      | 0      |
| Sectorial        | 3       | 0        | 2      | 1      |
| **L0 Personas**  | **19**  | **6**    | **12** | **1**  |
| **L0 Activos**   | **16**  | **6**    | **10** | **0**  |
| **L0 Bienestar** | **12**  | **4**    | **8**  | **0**  |
| **L4 Comp.**     | **4**   | **2**    | **2**  | **0**  |
| **Lω Evol.**     | **3**   | **1**    | **1**  | **1**  |
| **TOTAL**        | **220** | **110**  | **94** | **12** |

---

## Anexo B. Matriz de usuarios del Gemelo Digital

### Esfera 1: Núcleo GORE (~250 usuarios)

| Rol                     | Cantidad | Criticidad | Módulos                |
| ----------------------- | -------- | ---------- | ---------------------- |
| Gobernador Regional     | 1        | Crítica    | CORE, IPR              |
| Consejeros Regionales   | 16       | Alta       | CORE                   |
| Administrador Regional  | 1        | Alta       | Ejecución              |
| Jefes de División       | 8        | Alta       | Todos                  |
| Analistas DIPIR         | ~15      | Crítica    | IPR                    |
| Supervisores Proyecto   | ~10      | Crítica    | Ejecución              |
| Profesionales DAF       | ~15      | Alta       | Presupuesto, Convenios |
| UCR                     | ~5       | Alta       | Convenios              |
| Control Interno         | ~5       | Alta       | Todos                  |
| CDR                     | ~10      | Alta       | IPR                    |
| Operadores CIES         | ~12      | Crítica    | CIES                   |
| Equipo UGIT             | ~5       | Alta       | IDE/GIS                |
| PMO TIC                 | ~3       | Alta       | TIC                    |
| Encargados Cumplimiento | ~4       | Alta       | Cumplimiento           |

### Esfera 2: Ecosistema Gubernamental (~200 usuarios)

| Actor                 | Cantidad | Criticidad | Módulos              |
| --------------------- | -------- | ---------- | -------------------- |
| MDSF Regional         | ~3       | Crítica    | IPR                  |
| DIPRES/SES            | ~5       | Alta       | IPR, Presupuesto     |
| CGR                   | ~5       | Crítica    | Todos                |
| Municipalidades (UF)  | ~42      | Crítica    | Municipal, IPR       |
| Municipalidades (UTR) | ~42      | Crítica    | Municipal, Ejecución |
| SEREMI                | ~20      | Media      | Territorial          |
| CPLT                  | ~3       | Alta       | Cumplimiento         |
| IND/CMN/MINCAP        | ~9       | Alta       | Sectorial            |

### Esfera 3: Ecosistema Regional (~506,000 usuarios)

| Actor      | Cantidad | Criticidad | Módulos       |
| ---------- | -------- | ---------- | ------------- |
| Ciudadanía | ~500,000 | Alta       | Transparencia |
| OSC        | ~1,000   | Media      | Municipal     |
| Empresas   | ~7,000   | Media      | IPR           |
| Academia   | ~500     | Media      | IDE/GIS       |

---

## Anexo C. Checklist de Coherencia Categórica

Antes de implementar cualquier módulo, verificar:

### Alineamiento Ontológico
- [ ] Entidades existen en `data-gore/tracks/ontology/modular`
- [ ] Morfismos (FKs) corresponden a funtores definidos en `20_morphisms/funtores.yaml`
- [ ] Invariantes están documentados en `50_verification/verificacion.yaml`

### Preservación de Estructura
- [ ] Límites: JOINs y FKs correctamente definidos en Drizzle
- [ ] Colímites: Discriminated unions modelados con Zod
- [ ] FSM: Estados y transiciones implementados en XState
- [ ] Adjunción: Schema Drizzle infiere tipos correctamente

### Type Safety
- [ ] Zod schemas para todas las entradas (clasificador Ω)
- [ ] Branded types para IDs (CodigoBIP, RUT, etc.)
- [ ] Result<T, E> para manejo de errores
- [ ] tRPC procedures con input/output tipados

### Verificación
- [ ] Tests unitarios para invariantes críticos
- [ ] Tests de integración para transiciones FSM
- [ ] Validación de morfismos en compile-time

---

> **Certificación**: Este documento representa el diseño del Sistema Operativo GORE v3.0.0 PHOENIX-CATEGORICAL  
> **Última actualización**: 2025-01-XX  
> **Stack**: Bun + Hono + tRPC + Drizzle + XState + PostgreSQL  
> **Ontología**: `data-gore/tracks/ontology/modular` v5.1.0
