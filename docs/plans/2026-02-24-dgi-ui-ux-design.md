# DGI UI/UX Design - GORE_OS Dashboard MVP

**Fecha**: 2026-02-24
**Versión**: 1.0
**Enfoque**: Cockpit por Rol (desktop-first, minimalista, funcional)
**Usuarios**: 4 funcionarios DGI (Jefe, Esp. Control Gestión, Esp. Procesos, Esp. TD)
**Dispositivo**: Desktop/laptop

---

## Principio de diseño

Cada elemento en pantalla es la respuesta a una pregunta que el funcionario se hace al llegar a su puesto. No hay elementos decorativos ni widgets "por si acaso". Cada componente está trazado a una User Story o un artículo del Manual Operacional DGI.

## Enfoque: Cockpit por Rol

Cada rol del DGI tiene su propia pantalla de inicio personalizada. El sistema detecta quién eres y te muestra TU cockpit. Navegación lateral mínima para acceder a las pantallas compartidas.

**Razón**: La necesidad humana de cada rol es distinta. El Especialista Control de Gestión abre el sistema para ver si los datos llegaron y qué indicadores están en rojo. El Especialista Procesos abre para ver en qué estado va su portfolio de levantamientos BPMN. Forzarlos al mismo canvas es anti-funcional.

---

## 1. Arquitectura de Navegación Global

### Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ GORE_OS  DGI                    [Buscar... Cmd+K]   bell(3)  Usuario ▾ │
├────────┬─────────────────────────────────────────────────────────────────┤
│        │                                                                 │
│ NAV    │              AREA DE CONTENIDO                                 │
│ ────   │              (Cockpit del rol activo o pantalla compartida)     │
│        │                                                                 │
│ Home   │                                                                 │
│ Alert  │                                                                 │
│ Board  │                                                                 │
│ Data   │                                                                 │
│ Report │                                                                 │
│        │                                                                 │
├────────┴─────────────────────────────────────────────────────────────────┤
│ Conectado │ Datos: hace N min │ Semana N / 2026                         │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5 items de navegación

| Nav | Derivado de | Necesidad que satisface |
|-----|------------|------------------------|
| **Home** | Manual Art.14 (4 tipos dashboard) | "Al llegar, qué veo?" - Cockpit personalizado por rol |
| **Alertas** | 11 US de alertas + Manual Art.16 (protocolo escalamiento) | "Qué requiere mi atención ahora?" |
| **Tablero** | Manual Art.22 (Kanban, WIP limits) + US-EJEC-EO-* | "En qué estado van nuestras iniciativas?" |
| **Datos** | US-BI-001-01 (acceso consolidado) + US-GEST-HG-003 (drill-down) | "Necesito investigar un dato" |
| **Informes** | Manual Art.15 (Flash/Semanal/Mensual/Temático) + 10 US de reportes | "Necesito generar un entregable" |

### Barra superior

- Logo GORE_OS + contexto "DGI"
- Búsqueda global (Cmd+K): busca en datos, alertas, informes, procesos
- Campana de notificaciones con badge (count de alertas no reconocidas)
- Menú usuario: nombre, rol, logout

### Barra inferior (status)

- Estado de conexión a base de datos
- Timestamp de última actualización de datos
- Semana actual del año

---

## 2. Cockpit Jefe/a DGI

**Pregunta que responde**: "Cómo está la institución ahora mismo y qué necesita mi decisión?"

**Derivado de**: US-GEST-SCG-001, US-GEST-SCG-003, US-GOB-001-02, US-GEST-PB-001, Manual Art.14 (Dashboard Ejecutivo)

### Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ COCKPIT JEFE DGI                                            Fecha      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  SEMÁFORO INSTITUCIONAL (5 dimensiones)                                │
│  [PRESUP.] [CARTERA IPR] [CONVENIOS] [TDE] [RIESGOS]                 │
│                                                                         │
├──────────────────────────────┬──────────────────────────────────────────┤
│ REQUIEREN MI DECISIÓN (N)    │ EQUIPO DGI HOY                          │
│ Lista priorizada de items    │ Estado actual de cada especialista       │
│ que esperan acción del Jefe  │                                         │
│ [Ver detalle] [Decidir]      │ PRÓXIMAS REUNIONES                     │
│                              │ Standup, Sync AR, Comité TD             │
├──────────────────────────────┴──────────────────────────────────────────┤
│ ALERTAS CRÍTICAS ACTIVAS (N)                                           │
│ Solo las ROJO, con acción disponible: [Escalar] [Activar playbook]    │
│                                                                         │
│ INFORME SEMANAL                                   [Generar borrador]   │
│ Estado: Pendiente/En progreso │ Entrega: Viernes 17:00                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### Componentes

| Componente | US / Manual | Criterio de aceptación |
|---|---|---|
| Semáforo 5 dimensiones | US-GEST-SCG-001 | Panel KPIs; validación presupuestaria |
| Cola "Requieren decisión" | US-GEST-PB-001 | Max alert to AR; daily recovery dashboard |
| Alertas críticas | US-GOB-001-02 | Auto-alerts >15% financial variance o >30-day delays |
| Informe semanal | US-GEST-SCG-003 | PDF/Excel generator con progreso físico-financiero |
| Estado equipo | Manual Art.22 | Standup diario, visibilidad de WIP |

### Interacciones

- Click en semáforo → drill-down a indicadores de esa dimensión
- Click en "Decidir" → panel lateral con contexto + opciones + botones de acción
- Click en "Activar playbook" → checklist de recuperación (US-GEST-PB-001)
- Click en "Generar borrador" → auto-popula informe con datos actuales

---

## 3. Cockpit Especialista Control de Gestión

**Pregunta que responde**: "Llegaron los datos, qué indicadores están fuera de rango, y qué debo investigar?"

**Derivado de**: US-GEN-GESTION_MORA-001, US-FIN-PPTO-011, US-ANALPRES-001-02, US-NORM-CTRL-004, Manual Art.14-15

### Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ COCKPIT CONTROL DE GESTIÓN                                    Fecha    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ESTADO DE DATOS HOY (fuentes por división)                            │
│  [DAF OK] [DIPIR OK] [JURIDICA 2d] [DIPLADE OK] [DIDESOH Falta]      │
│                                                                         │
├──────────────────────────────┬──────────────────────────────────────────┤
│ INDICADORES EN ALERTA        │ TENDENCIAS (30 DÍAS)                    │
│ Lista ordenada por severidad │ Barras de progreso + flechas tendencia  │
│ ROJO primero, luego AMARILLO │ Cada indicador: valor, meta, dirección  │
│ [Investigar] por cada uno    │                                         │
│                              │ TIEMPOS DE CICLO                       │
│ Indicadores VERDE abajo      │ Convenio, Pago, Resolución vs meta     │
├──────────────────────────────┴──────────────────────────────────────────┤
│ MI COLA DE TRABAJO HOY                                                 │
│ Tabla: Prioridad │ Tarea │ Estado │ Plazo                              │
│ (derivada del checklist diario del Manual Art.15)                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Componentes

| Componente | US / Manual | Criterio |
|---|---|---|
| Estado de datos | Manual Art.15 | "Validar recepción de datos, ejecutar calidad" |
| Indicadores en alerta | US-FIN-PPTO-011 | "Alertas visuales cuando desfase >5%" |
| Tendencias 30d | US-GEST-HG-003 | "Historical performance comparison" |
| Tiempos de ciclo | Diagnóstico DGI | "Días promedio convenio, pago, resolución" |
| Cola de trabajo | Manual Art.15 | Checklist diario del rol |

### Interacciones

- Click en fuente con warning → detalle: último dato, fecha, contacto proveedor
- Click en "Investigar" → panel de análisis: 5-Porqués o Ishikawa
- Click en indicador → drill-down: Agregado → División → Proyecto → Transacción
- Click en tendencia → gráfico expandido 12 meses + línea de meta

---

## 4. Cockpit Especialista Procesos

**Pregunta que responde**: "En qué estado van mis proyectos de mejora y qué tengo que hacer hoy?"

**Derivado de**: Manual Art.18-20 (Levantamiento, Oportunidades, Automatización), US-GEN-GESTION_CTD-001

### Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ COCKPIT PROCESOS                                              Fecha    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PORTFOLIO DE MEJORA (N activos)                       Meta anual: 5   │
│  Kanban DMAIC:                                                         │
│  DEFINE-MEASURE (WIP<=2) │ ANALYZE-IMPROVE (WIP<=3) │ VERIFY (WIP<=2) │
│  Cards con: nombre, división, día N/total, barra progreso              │
│                                                                         │
├──────────────────────────────┬──────────────────────────────────────────┤
│ HOY                          │ MODELOS BPMN RECIENTES                  │
│ Agenda de entrevistas        │ Lista de procesos modelados             │
│ con división, proceso,       │ Estado: Borrador/Revisión/Validado      │
│ fase DMAIC actual            │ Versión actual                          │
│ [Abrir ficha proceso]        │ Total levantados vs meta anual (8)     │
│                              │ [Ver biblioteca completa]               │
└──────────────────────────────┴──────────────────────────────────────────┘
```

### Componentes

| Componente | US / Manual | Criterio |
|---|---|---|
| Kanban DMAIC | Manual Art.22 | "Backlog→Design(D-M-A)→Implementation(I)→Verification(C)→Completed" con WIP limits |
| Cards con progreso | Manual Art.19 | "Timeline projections for targets" |
| Agenda entrevistas | Manual Art.18 | "Levantamiento requiere entrevistas estructuradas" |
| Biblioteca BPMN | Manual Art.18 | "BPMN v1.0 con anotaciones → validado → publicado" |
| Meta anual | Hoja de Ruta | "5 mejoras implementadas, 8 procesos levantados al año" |

### Interacciones

- Drag & drop cards entre columnas (con validación de WIP limits - bloquea si se excede)
- Click en card → ficha proyecto DMAIC (Charter, métricas baseline, BPMN, oportunidades)
- Click en "Abrir modelo" → visor BPMN con pools/lanes/gates
- Click en entrevista → formulario de levantamiento pre-cargado

---

## 5. Cockpit Especialista Transformación Digital

**Pregunta que responde**: "Cómo vamos con el cumplimiento Ley 21.180 y qué sistemas necesitan atención?"

**Derivado de**: US-TDE-AVANCE-002, US-TDE-SEG-001, US-TDE-ADMIN-006, Manual Art.25-27

### Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ COCKPIT TRANSFORMACIÓN DIGITAL                                Fecha    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CUMPLIMIENTO LEY 21.180                              Meta 2027: 80%  │
│  5 barras: Digitalización, Expediente, Firma, Notificaciones, Interop │
│  Velocidad actual vs requerida │ Meses restantes │ Estado semáforo    │
│                                                                         │
├──────────────────────────────┬──────────────────────────────────────────┤
│ DECRETOS (DS7-DS12)          │ BASE DE CONOCIMIENTO                    │
│ Checklist por decreto:       │ Pendientes publicación: N               │
│ Vigente / Parcial / Pend.    │ Últimas actualizadas: N                │
│ [Ver matriz completa]        │ Total artefactos: N                    │
│                              │ [Gestionar KB]                          │
├──────────────────────────────┼──────────────────────────────────────────┤
│ ALERTAS NORMATIVAS           │ COMITÉ TD                               │
│ Alertas 3 meses antes de     │ Próxima sesión: fecha                  │
│ vencimiento hitos legales    │ Estado agenda: Borrador/Listo          │
│ (US-TDE-AVANCE-002)         │ Actas pendientes: N                    │
│                              │ Acuerdos abiertos: N                   │
│                              │ [Preparar sesión]                      │
└──────────────────────────────┴──────────────────────────────────────────┘
```

### Componentes

| Componente | US / Manual | Criterio |
|---|---|---|
| Barras cumplimiento | US-TDE-AVANCE-002 | "Dashboard de % trámites con interoperabilidad activa" |
| Velocidad/brecha | Diagnóstico DGI | "TARGET 2027: 80%, ACTUAL: 39%, BRECHA: -41pp" |
| Matriz DS7-DS12 | US-TDE-SEG-001 | "Mapeo controles implementados vs exigidos" |
| KB management | Manual Art.25-27 | "Curaduría KB, publicación, versionado" |
| Alertas normativas | US-TDE-AVANCE-002 | "Alertas preventivas 3 meses antes del vencimiento" |
| Comité TD | Manual | "Secretaría técnica: agenda, acta, seguimiento" |

### Interacciones

- Click en barra de cumplimiento → lista de procesos con estado de digitalización
- Click en decreto → detalle con controles requeridos vs implementados
- Click en "Gestionar KB" → lista de artefactos con filtros, curaduría
- Click en "Preparar sesión" → formulario de agenda + auto-pull de status

---

## 6. Pantallas Compartidas

### 6A. Centro de Alertas

**Derivado de**: 11 US de alertas + Manual Art.16 (protocolo escalamiento 4 niveles)

**Layout**: Filtros por nivel (Crítico/Alto/Medio/Bajo) + lista de alertas activas + historial de resueltas + exportar CSV.

**Ciclo de vida**: Generada → Reconocida → En Investigación → Acción Iniciada → Resuelta → Cerrada

**Reglas de generación** (de las US):

| Dominio | AMARILLO | ROJO | US |
|---|---|---|---|
| Presupuesto | desfase >5% | desfase >15% | US-FIN-PPTO-011 |
| IPR | atraso >2 semanas | atraso >4 semanas | US-GOB-001-02 |
| Convenio | <30 días para vencer | <7 días para vencer | Manual |
| TDE | vel. actual < requerida | brecha >20pp | US-TDE-AVANCE-002 |
| Datos | 1-2 fuentes faltantes | 3+ fuentes faltantes | Manual Art.15 |

**Acciones por nivel** (Manual Art.16):

| Nivel | SLA respuesta | Acción |
|---|---|---|
| Crítico | 4 horas | Jefe DGI → puede escalar a AR |
| Alto | 24 horas | Especialista → Jefe DGI si no resuelve |
| Medio | 72 horas | Especialista → informe semanal |
| Bajo | Informativo | Solo registro |

### 6B. Tablero Kanban (Iniciativas DGI)

**Derivado de**: Manual Art.22 (Gestión Visual, WIP limits explícitos)

**Columnas**: BACKLOG │ EN CURSO (WIP=5) │ REVISIÓN (WIP=2) │ COMPLETADO

**Card**: Nombre iniciativa, responsable (especialista), día N de M, barra progreso

**Interacciones**: Drag & drop con WIP enforcement, click para detalle, filtro por responsable

### 6C. Explorador de Datos

**Derivado de**: US-BI-001-01 + US-GEST-HG-003

**Layout**: Panel izquierdo con dominios (IPR, Presupuesto, Convenios, Organizaciones, Personas, Territorio, Eventos, Rendiciones) + tabla filtrable a la derecha + panel lateral de detalle al hacer click en fila.

**Capacidades**: Filtros multi-dimensión, ordenamiento, búsqueda full-text, exportar CSV/Excel, drill-down a timeline de eventos por registro.

### 6D. Generador de Informes

**Derivado de**: Manual Art.15 + US-GEST-SCG-003 + US-EJEC-AR-006

**4 tipos** (del Manual):

| Tipo | Frecuencia | Destinatario | Trigger |
|---|---|---|---|
| Flash | Inmediato | AR | Alerta crítica |
| Semanal | Viernes 17:00 | AR | Calendario |
| Mensual | Día 5 del mes | AR + Gobernador | Calendario |
| Temático | A pedido | Solicitante | Manual |

**Estructura del informe semanal** (Manual Art.15):
1. Resumen ejecutivo (semáforo + logros + alertas)
2. Tabla de indicadores (meta, real, tendencia, % cumplimiento)
3. Alertas activas (nivel, descripción, responsable, acción)
4. Avance de iniciativas DGI
5. Decisiones requeridas por AR (con opciones + recomendación)
6. Prioridades próxima semana

**Auto-población**: El sistema pre-llena con datos actuales. El usuario revisa, agrega comentarios cualitativos, y exporta.

---

## 7. Patrones de Interacción Transversales

### 7.1 Drill-down (US-GEST-HG-003)

Click en KPI agregado → indicadores por división → proyectos individuales → eventos/transacciones. Breadcrumb de retorno siempre visible.

### 7.2 Panel lateral (US-EJEC-EO-006)

Click en cualquier fila de tabla → panel deslizante desde la derecha con:
- Timeline completa (Quién, Qué, Cuándo)
- Documentos adjuntos
- Acciones disponibles (aprobar, escalar, completar)

### 7.3 Semáforo consistente

En toda la aplicación:
- VERDE: valor >= meta
- AMARILLO: valor < meta * 0.9
- ROJO: valor < meta * 0.8

### 7.4 Exportar

Desde cualquier tabla o dashboard:
- CSV (datos crudos)
- Excel (con formato)
- PDF (para presentaciones)
- PNG/SVG (mapas y gráficos)

### 7.5 Notificaciones

Badge en campana → lista desplegable → click abre el contexto de la alerta directamente. No interrumpe el flujo de trabajo actual.

### 7.6 Búsqueda global (Cmd+K)

Busca en: datos, alertas, informes, procesos BPMN, artefactos KB. Resultados agrupados por tipo.

---

## 8. Mapeo completo US → Pantalla

| User Story | Pantalla | Componente |
|---|---|---|
| US-GEST-SCG-001 | Jefe: Semáforo | Panel KPIs 5 dimensiones |
| US-GEST-SCG-003 | Informes | Generador mensual/semanal |
| US-GEST-HG-002 | Jefe: Alertas | Configuración umbrales |
| US-GEST-HG-003 | Datos | Drill-down dimensional |
| US-GOB-001-02 | Jefe: Alertas críticas | Auto-alertas >15% desfase |
| US-GEST-PB-001 | Jefe: Playbook | Checklist recuperación |
| US-GEN-GESTION_MORA-001 | Alertas | Push a jefaturas por mora |
| US-FIN-PPTO-011 | CG: Indicadores | Proyección vs programa caja |
| US-ANALPRES-001-02 | CG: Indicadores | Alertas marcos por agotar |
| US-NORM-CTRL-004 | Alertas | Hallazgos + PAC a Gobernador |
| US-GEN-GESTION_CTD-001 | TD: Cumplimiento | Madurez digital por div. |
| US-TDE-AVANCE-002 | TD: Cumplimiento | Dashboard interoperabilidad |
| US-TDE-SEG-001 | TD: Decretos | Mapeo controles DS7 |
| US-TDE-ADMIN-006 | Alertas: Config | Motor reglas + triggers |
| US-BI-001-01 | Datos | Acceso consolidado transaccional |
| US-GOB-CORE-004 | Datos | Mapa inversiones con filtros |
| US-GOB-CORE-007 | Datos | Cumplimiento acuerdos CORE |
| US-FIN-IPR-011 | Datos/Informes | Formulario avance físico-financiero |
| US-EJEC-AR-006 | Informes | Resumen semanal PDF Gobernador |
| US-EJEC-EO-003 | Datos: Panel lateral | Completar + validar compromiso |
| US-EJEC-EO-005 | Datos: Panel lateral | Solicitar extensión plazo |
| US-EJEC-EO-006 | Datos: Panel lateral | Timeline historial cambios |
| US-FIN-PPTO-006 | Datos | Emisión CDP con validación saldo |

---

## 9. Fuera de alcance MVP

Estos componentes aparecen en las US pero no son necesarios para el Dashboard v1 del DGI:

- Visor cartográfico/mapa (US-GOB-CORE-004) - Phase 2
- Integración SIGFE API - Phase 2
- Integración GESDOC/SGDOC - Phase 2
- Integración CGR/SIAPER (US-NORM-ACTO-003) - Phase 3
- Firma electrónica avanzada - Phase 2
- ClaveÚnica SSO (US-TDE-AUTH-001) - Phase 2
- Motor de reglas configurable (US-TDE-ADMIN-006) - Phase 2 (hardcoded en MVP)
- Visor/editor BPMN integrado - Phase 2 (link a herramienta externa en MVP)
- IA Agent monitoring - Phase 3

---

## 10. Stack técnico propuesto

- **Frontend**: Next.js 14+ (App Router, Server Components)
- **UI Kit**: Tailwind CSS + shadcn/ui (minimalista, sin overhead)
- **Gráficos**: Recharts (simple, React-native)
- **Backend**: FastAPI (Python, ya alineado con stack GORE_OS)
- **Base de datos**: PostgreSQL 16 (existente, 71 tablas)
- **Autenticación**: NextAuth.js (email/password para MVP, ClaveÚnica en Phase 2)

---

## Trazabilidad de fuentes

- Manual Operacional DGI v1.0 (`diagnostico_dgi/fuentes/manual_operacional_dgi.md`)
- 819 User Stories (`goreos/model/stories/`)
- 86 Procesos BPMN (`goreos/model/processes/`)
- Diagnóstico DGI completo (`diagnostico_dgi/`)
- Hoja de Ruta DGI (`diagnostico_dgi/fuentes/`)
- GOREOS ERD v3 (`goreos/model/model_goreos/docs/GOREOS_ERD_v3.md`)
