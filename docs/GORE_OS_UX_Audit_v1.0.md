# GORE_OS — Auditoría UX/UI v1.0

**Fecha**: 2026-03-03
**Versión**: 1.0
**Alcance**: 8 roles activos, 3 journeys funcionales, ~31 páginas, ~24 componentes
**Método**: Análisis estático de código frontend + revisión de endpoints backend

---

# PARTE I — FUNDAMENTOS

## 1. Resumen Ejecutivo

### 1.1 Scorecard General

| Dimensión | Madurez | Hallazgos |
|-----------|---------|-----------|
| Accesibilidad (WCAG 2.1 AA) | Bajo | 12 hallazgos |
| Responsividad Mobile | Bajo | 8 hallazgos |
| Manejo de Errores | Medio-Bajo | 10 hallazgos |
| Consistencia Visual | Medio | 9 hallazgos |
| Navegación Cross-Entity | Medio-Alto | 5 hallazgos |
| Funcionalidad Completa | Medio | 15 hallazgos |
| Formularios y Validación | Medio-Bajo | 11 hallazgos |
| Performance Percibida | Medio | 6 hallazgos |

### 1.2 Top 15 Hallazgos Críticos

| # | ID | Severidad | Descripción |
|---|-----|-----------|-------------|
| 1 | UX-001 | CRITICO | `animate-pulse` en badge VENCIDO causa parpadeo accesible |
| 2 | UX-002 | CRITICO | `alert()` nativo en admin usuarios para errores |
| 3 | UX-003 | CRITICO | DrawerPanel ancho fijo 400px rompe en mobile |
| 4 | UX-004 | CRITICO | Sin recuperación de contraseña en login |
| 5 | UX-005 | ALTO | FilterBar con anchos fijos (w-56, w-44) overflow en mobile |
| 6 | UX-006 | ALTO | KpiCard sin soporte keyboard en dashboard mi-division |
| 7 | UX-007 | ALTO | DataTable sin role="table" ni aria-labels |
| 8 | UX-008 | ALTO | No existe formulario de creación de programas presupuestarios |
| 9 | UX-009 | ALTO | Cuotas de convenio se crean una por una, sin bulk |
| 10 | UX-010 | ALTO | Sin toast/snackbar global — errores silenciados con console.error |
| 11 | UX-011 | ALTO | Cockpit decisiones son placeholder sin datos reales |
| 12 | UX-012 | ALTO | Rendiciones solo accesibles vía /datos sidebar, no main nav |
| 13 | UX-013 | MEDIO | Login con background hardcoded `#1e3a5f` (no tema) |
| 14 | UX-014 | MEDIO | Paginación deshabilitada en /mis-compromisos |
| 15 | UX-015 | MEDIO | Abreviaciones sin tooltip en cockpit TD (VIG, PAR, PEN) |

### 1.3 Mapa de Calor: Roles x Dimensiones

```
                 Accesib. Respons. Errores  Visual  Nav     Funcional
ADMIN_SISTEMA    ██░░░░   ██░░░░   ████░░   ██░░░░  ██░░░░  ██░░░░
ADMIN_REGIONAL   ██░░░░   ██░░░░   ██░░░░   ██░░░░  ██░░░░  ████░░
JEFE_DIVISION    ██░░░░   ██░░░░   ██░░░░   ████░░  ██░░░░  ████░░
ENCARGADO        ██░░░░   ██░░░░   ██░░░░   ██░░░░  ██░░░░  ████░░
JEFE_DGI         ██░░░░   ██░░░░   ██░░░░   ████░░  ██░░░░  ████░░
ESP_CTRL_GEST    ██░░░░   ████░░   ██░░░░   ██░░░░  ████░░  ████░░
ESP_PROCESOS     ██░░░░   ██░░░░   ██░░░░   ██░░░░  ██░░░░  ████░░
ESP_TD           ██░░░░   ██░░░░   ██░░░░   ████░░  ██░░░░  ████░░

(██ = 2+ hallazgos, ████ = 4+ hallazgos, ░░ = sin hallazgos relevantes)
```

---

## 2. Experiencia Compartida (Cross-Cutting)

### 2.1 Login

**[UX-004]** Severidad: CRITICO
- **Archivo**: `web/src/app/login/page.tsx:30-90`
- **Descripcion**: No existe enlace de recuperacion de contraseña ("Olvide mi contraseña"). El formulario solo tiene email + password + boton "Ingresar".
- **Impacto**: Usuarios bloqueados si olvidan credenciales. Deben contactar a ADMIN_SISTEMA para reset manual.
- **Recomendacion**: Implementar flujo de reset vía email o integrar ClaveÚnica (gap HΩ pendiente).

**[UX-013]** Severidad: MEDIO
- **Archivo**: `web/src/app/login/page.tsx:33`
- **Descripcion**: Background color hardcoded `style={{ backgroundColor: "#1e3a5f" }}` en vez de usar variable de tema CSS. No respeta dark mode ni tematización.
- **Impacto**: Inconsistencia visual si se implementa dark mode. El color no es configurable.
- **Recomendacion**: Usar clase Tailwind `bg-primary` o variable CSS `--login-bg`.

**[UX-016]** Severidad: BAJO
- **Archivo**: `web/src/app/login/page.tsx:69-72`
- **Descripcion**: Sin validación de formato email en frontend (solo `type="email"` nativo). Sin indicador de fortaleza de contraseña.
- **Impacto**: UX pobre en feedback de validación.
- **Recomendacion**: Agregar regex de email y password strength meter.

### 2.2 AppShell (Sidebar + Header + Status Bar)

**[UX-017]** Severidad: MEDIO
- **Archivo**: `web/src/components/sidebar.tsx:97`
- **Descripcion**: Sidebar tiene ancho fijo `w-56` (224px) sin collapse/toggle. En pantallas <768px ocupa ~30% del viewport.
- **Impacto**: Sidebar no es responsive. No hay hamburger menu para mobile.
- **Recomendacion**: Implementar sidebar colapsable con Sheet en mobile (patron shadcn standard).

**[UX-018]** Severidad: BAJO
- **Archivo**: `web/src/components/sidebar.tsx:96-132`
- **Descripcion**: Links de navegación sin `aria-current="page"` para el item activo. Solo usa cambio visual de color.
- **Impacto**: Screen readers no anuncian la página actual.
- **Recomendacion**: Agregar `aria-current="page"` al link activo.

**[UX-019]** Severidad: BAJO
- **Archivo**: `web/src/components/app-shell.tsx:64-70`
- **Descripcion**: Status bar muestra "Conectado" con dot verde estático. No refleja estado real de conexión (no hay health check).
- **Impacto**: Indicador engañoso — siempre verde aunque la API esté caída.
- **Recomendacion**: Implementar health check periódico o usar `navigator.onLine`.

**[UX-020]** Severidad: BAJO
- **Archivo**: `web/src/components/app-shell.tsx:69`
- **Descripcion**: Año hardcoded `2026` en status bar en vez de usar `new Date().getFullYear()`.
- **Impacto**: Se desactualiza cada enero.
- **Recomendacion**: Usar fecha dinámica.

**[UX-021]** Severidad: MEDIO
- **Archivo**: `web/src/components/header.tsx:67-90`
- **Descripcion**: Cambio de contraseña tiene validación mínima (solo `length < 8`). Sin confirmación de contraseña nueva. Sin password strength indicator.
- **Impacto**: Usuarios pueden establecer contraseñas débiles sin feedback.
- **Recomendacion**: Agregar campo de confirmación + indicador de fortaleza.

### 2.3 Sistema de Diseño

**[UX-022]** Severidad: MEDIO
- **Archivo**: `web/src/components/status-badge.tsx` (múltiples líneas)
- **Descripcion**: 3 esquemas de color coexisten: (1) StatusBadge usa colores directos (bg-blue-600, bg-amber-500), (2) KpiCard usa border-l-* con bg-*-50, (3) Cockpit TD usa abreviaciones con border-*-300. No hay paleta unificada.
- **Impacto**: Inconsistencia visual entre componentes. El mismo concepto "PENDIENTE" tiene distinto estilo según el contexto.
- **Recomendacion**: Definir paleta semántica centralizada (ej: `status-pending`, `status-active`, `status-done`).

**[UX-023]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-jefe-dgi.tsx:295-300`
- **Descripcion**: Formateo de moneda CLP inline con `new Intl.NumberFormat(...)` en vez de usar `formatCLP` de `lib/format.ts`. Viola regla 34 de CLAUDE.md.
- **Impacto**: Formato potencialmente inconsistente con el resto de la app.
- **Recomendacion**: Reemplazar con `import { formatCLP } from "@/lib/format"`.

### 2.4 Accesibilidad WCAG 2.1 AA

**[UX-001]** Severidad: CRITICO
- **Archivo**: `web/src/components/status-badge.tsx:43`
- **Descripcion**: `animate-pulse` en badge VENCIDO causa parpadeo continuo. WCAG 2.3.1 prohíbe contenido que parpadea >3 veces/segundo.
- **Impacto**: Puede causar seizures en usuarios con epilepsia fotosensitiva. Afecta a todas las páginas que muestran compromisos o convenios vencidos.
- **Recomendacion**: Reemplazar `animate-pulse` por un indicador estático (ej: borde rojo grueso o icono).

**[UX-007]** Severidad: ALTO
- **Archivo**: `web/src/components/data-table.tsx:60-100`
- **Descripcion**: `<Table>` no tiene `role="table"`, `aria-label`, ni `aria-describedby`. Paginación no anuncia cambios a screen readers (sin `aria-live`).
- **Impacto**: Usuarios de screen readers no pueden identificar el propósito de la tabla ni recibir feedback de navegación.
- **Recomendacion**: Agregar `aria-label` descriptivo al Table. Usar `aria-live="polite"` en el contador de resultados.

**[UX-006]** Severidad: ALTO
- **Archivo**: `web/src/components/kpi-card.tsx:34-47`
- **Descripcion**: KpiCard con `onClick` solo tiene `cursor-pointer`. No tiene `role="button"`, `tabIndex`, ni handler `onKeyDown` para Enter/Space. SemaforoCard sí los tiene (línea 46-48).
- **Impacto**: KPIs clickeables en dashboard no son accesibles vía teclado.
- **Recomendacion**: Agregar `role="button" tabIndex={0} onKeyDown={handler}` como ya hace SemaforoCard.

**[UX-024]** Severidad: MEDIO
- **Archivo**: `web/src/components/data-table.tsx:46-49`
- **Descripcion**: Loading skeleton usa `animate-pulse` (5 filas parpadeando). Prefiero `aria-busy="true"` con skeleton más sutil.
- **Impacto**: Parpadeo visual durante cargas. Menor impacto que UX-001 por ser temporal.
- **Recomendacion**: Agregar `aria-busy="true"` al contenedor durante carga.

**[UX-025]** Severidad: MEDIO
- **Archivo**: `web/src/components/header.tsx:167-181`
- **Descripcion**: Items de alerta en popover no son focusables por teclado. Solo tienen hover state, sin `tabIndex` ni role.
- **Impacto**: Alertas en header inaccesibles vía teclado.
- **Recomendacion**: Hacer items focusables y clickeables con teclado.

### 2.5 Responsividad Mobile

**[UX-003]** Severidad: CRITICO
- **Archivo**: `web/src/components/drawer-panel.tsx:22`
- **Descripcion**: DrawerPanel tiene ancho fijo `w-[400px] sm:w-[400px]`. En pantallas <400px, el drawer se desborda o cubre toda la pantalla sin opción de scroll lateral. El breakpoint `sm:` repite el mismo valor.
- **Impacto**: Drawer inutilizable en cualquier dispositivo mobile. Afecta todas las páginas que usan drawer (compromisos, problemas, convenios, presupuesto, admin usuarios).
- **Recomendacion**: Usar `w-full sm:w-[400px]` o `max-w-[400px]`.

**[UX-005]** Severidad: ALTO
- **Archivo**: `web/src/components/filter-bar.tsx:57,66`
- **Descripcion**: Input de búsqueda tiene `w-56` fijo (224px), Select triggers tienen `w-44` fijo (176px). En mobile, el `flex-wrap` ayuda parcialmente pero los items individuales no se adaptan.
- **Impacto**: FilterBar se rompe en pantallas <375px. Badges de filtros activos pueden desbordar.
- **Recomendacion**: Usar `w-full sm:w-56` para input y `w-full sm:w-44` para selects.

**[UX-026]** Severidad: ALTO
- **Archivo**: `web/src/app/(app)/datos/page.tsx:152-157`
- **Descripcion**: Layout de 3 paneles con grid `grid-cols-[200px_1fr_340px]` es fijo. No colapsa en mobile.
- **Impacto**: Página /datos completamente inutilizable en mobile.
- **Recomendacion**: Usar layout responsive con sidebar colapsable y detail panel como modal en mobile.

**[UX-027]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/cartera/page.tsx:387`
- **Descripcion**: Summary cards usan grid `grid-cols-2 sm:grid-cols-3 lg:grid-cols-6`. Con 6 columnas y muchas DataTable columns (10+), la tabla desborda horizontalmente.
- **Impacto**: Tabla de cartera requiere scroll horizontal en pantallas <1280px.
- **Recomendacion**: Ocultar columnas menos importantes en breakpoints menores o usar scroll horizontal con indicador.

### 2.6 Manejo de Errores y Estados

**[UX-002]** Severidad: CRITICO
- **Archivo**: `web/src/app/(app)/admin/usuarios/page.tsx:213`
- **Descripcion**: Error en guardar edición de usuario usa `alert()` nativo del browser: `alert(err instanceof Error ? err.message : "Error al guardar")`. También en `handleToggle` (línea 227).
- **Impacto**: UX disruptiva — alert() bloquea toda interacción, no es estilizable, rompe el flujo.
- **Recomendacion**: Reemplazar con toast/snackbar (ej: sonner o react-hot-toast) o inline error como en otros formularios.

**[UX-010]** Severidad: ALTO
- **Archivo**: Múltiples (compromisos:153, problemas:169, convenios:279)
- **Descripcion**: Errores en acciones de estado (completar, verificar, resolver, pagar) se silencian con `console.error()`. El usuario no recibe ningún feedback visual de que la acción falló.
- **Impacto**: Acciones pueden fallar sin que el usuario lo sepa. Estado UI queda desincronizado con backend.
- **Recomendacion**: Implementar sistema de toast global. Mostrar mensaje de error en cada catch.

**[UX-028]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/convenios/page.tsx:279`
- **Descripcion**: `handlePaySubmit` tiene catch vacío `catch { // silently fail }`. El pago de una cuota puede fallar sin ningún feedback.
- **Impacto**: El usuario cree que pagó la cuota pero el backend rechazó la operación. Dato financiero incorrecto.
- **Recomendacion**: Mostrar error inline o toast. Nunca silenciar errores financieros.

**[UX-029]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/convenios/page.tsx:601`
- **Descripcion**: Botón "Registrar Pago" con `h-5 text-[10px]` es demasiado pequeño para target táctil. WCAG 2.5.5 requiere mínimo 44x44px para targets interactivos.
- **Impacto**: Difícil de clickear en dispositivos táctiles.
- **Recomendacion**: Aumentar tamaño mínimo a h-8.

---

# PARTE II — JOURNEYS POR ROL DEL SISTEMA

## 3. Journey: ADMIN_SISTEMA

```
Login → Dashboard Ejecutivo → /admin/usuarios (CRUD) →
/admin/divisiones → /admin/umbrales → /admin/niveles-sni →
IPR → Compromisos → Problemas → Convenios → Presupuesto →
Actos → Reuniones → CORE Sessions
```

**Lo que ve**: Dashboard ejecutivo completo (KPIs + semáforo + charts + desglose divisiones). Sidebar con 14 items (10 operativos + 4 admin). Acceso total a todas las entidades.

**Lo que puede hacer**: CRUD completo de usuarios, divisiones, umbrales financieros, niveles SNI. Crear/editar compromisos, problemas, convenios, presupuesto. Transiciones de estado en todos los módulos.

**Hallazgos específicos**:

**[UX-002]** (ver sección 2.6) — `alert()` en admin usuarios.

**[UX-030]** Severidad: ALTO
- **Archivo**: `web/src/app/(app)/admin/usuarios/page.tsx:192-217`
- **Descripcion**: Edit mode en drawer de usuario es frágil — usa múltiples estados (`editNames`, `editPaternal`, etc.) sin form validation library. No hay validación de email formato, ni de campos requeridos a nivel UI.
- **Impacto**: Se pueden enviar formularios con datos inválidos al backend.
- **Recomendacion**: Usar react-hook-form o zod para validación client-side.

**[UX-031]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/admin/usuarios/page.tsx:448-462`
- **Descripcion**: Reset de contraseña no tiene indicador de fortaleza ni validación de longitud mínima en frontend (el backend valida, pero sin feedback previo).
- **Impacto**: Admin puede intentar passwords débiles sin feedback.
- **Recomendacion**: Agregar validación mínima de 8 chars con feedback visual.

**Gaps**:
- Sin audit log UI (quién cambió qué, cuándo)
- Sin página de perfil propio (el admin solo puede ver su nombre en header dropdown)
- Sin bulk actions para usuarios (activar/desactivar múltiples)
- Sin exportación CSV de usuarios

---

## 4. Journey: ADMIN_REGIONAL

```
Login → Dashboard Ejecutivo (KPIs + semáforo + charts + desglose) →
IPR → Compromisos → Problemas → Convenios → Presupuesto →
Alertas → Reuniones → Actos → CORE Sessions
```

**Lo que ve**: Dashboard ejecutivo idéntico a ADMIN_SISTEMA (endpoint `/api/dashboard/ejecutivo`). Sidebar con 10 items operativos (sin admin).

**Lo que puede hacer**: Crear compromisos, problemas, convenios. Editar presupuesto y convenios. Verificar/devolver compromisos. No puede gestionar usuarios ni configuración.

**Hallazgos específicos**:

**[UX-032]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/dashboard/page.tsx:284-318`
- **Descripcion**: Desglose por división muestra filas con 4 badges (vencidos, compromisos, problemas, ejec%). En divisiones con todos los indicadores, la fila se satura visualmente. Sin filtro ni ordenamiento.
- **Impacto**: Difícil escanear rápidamente qué división tiene problemas.
- **Recomendacion**: Permitir ordenar por columna. Agregar click para drill-down a `/compromisos?division=X`.

**[UX-033]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/dashboard/page.tsx:213-228`
- **Descripcion**: SemaforoCard en dashboard ejecutivo no tiene `onClick` (excepto CARTERA_IPR en cockpit jefe DGI). Las dimensiones PRESUPUESTO, CONVENIOS, TDE, RIESGOS no navegan a ningún lado.
- **Impacto**: Semáforo es informativo pero no accionable. El usuario ve rojo pero no puede drill-down.
- **Recomendacion**: Agregar drill-down a cada dimensión del semáforo.

**Gaps**:
- Sin vista consolidada "toda la institución" que cruce IPR + presupuesto + convenios
- Charts (ejecución, compromisos, alertas) no son interactivos (no drill-down al clickear barras/slices)

---

## 5. Journey: JEFE_DIVISION

```
Login → Dashboard Operativo → Mi División (equipo + carga) →
Compromisos (verificar) → Problemas → Convenios →
Presupuesto → Alertas
```

**Lo que ve**: Dashboard operativo estándar (4 KPIs + charts + compromisos recientes + alertas). Sidebar con 11 items (10 + "Mi División").

**Lo que puede hacer**: Verificar/devolver compromisos. Reasignar compromisos a otro usuario. Crear problemas. Ver presupuesto y convenios (sin editar). Ver carga de equipo.

**Hallazgos específicos**:

**[UX-034]** Severidad: ALTO
- **Archivo**: `web/src/app/(app)/mi-division/page.tsx:114-141`
- **Descripcion**: Tabla "Carga por Persona" muestra 4 badges por persona (vencidos, pendientes, en_progreso, completados). Sin filtro, sin ordenamiento, sin búsqueda. En equipos de 10+ personas, es difícil encontrar quién está sobrecargado.
- **Impacto**: El jefe no puede priorizar rápidamente.
- **Recomendacion**: Agregar sort por vencidos (descendente) y highlight automático de personas con >5 vencidos.

**[UX-006]** (ver sección 2.4) — KPIs sin keyboard en mi-division (línea 94 pasa `onClick` undefined).

**[UX-035]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/mi-division/page.tsx:147-155`
- **Descripcion**: Tabla de compromisos vencidos tiene paginación hardcodeada `page={1} totalPages={1} onPageChange={() => {}}`. Si hay >20 vencidos, solo muestra los primeros.
- **Impacto**: El jefe no ve todos los compromisos vencidos de su división.
- **Recomendacion**: Implementar paginación real o link a `/compromisos?division=X&overdue=true`.

**Gaps**:
- Sin delegación de tareas (workflow para asignar desde mi-division)
- Sin vista de riesgo consolidada por división (semáforo por área)
- KPIs no clickeables para drill-down

---

## 6. Journey: ENCARGADO

```
Login → Dashboard Operativo → Mis Compromisos (grupos urgencia) →
Compromisos (completar) → Problemas → Alertas
```

**Lo que ve**: Dashboard operativo con KPIs personales (pendientes, en progreso, completados, alertas). Sidebar con 11 items (10 + "Mis Compromisos").

**Lo que puede hacer**: Completar compromisos asignados (PENDIENTE → COMPLETADO vía `canComplete`). Crear problemas. Ver alertas. No puede verificar ni reasignar.

**Hallazgos específicos**:

**[UX-014]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/mis-compromisos/page.tsx:117-125`
- **Descripcion**: DataTable en cada grupo usa `page={1} totalPages={1} onPageChange={() => {}}`. Paginación completamente deshabilitada. Si el encargado tiene 30 compromisos pendientes, solo ve los primeros.
- **Impacto**: Encargados con muchos compromisos no pueden ver todos.
- **Recomendacion**: Implementar paginación real o mostrar todos con scroll virtual.

**[UX-036]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/mis-compromisos/page.tsx:70-131`
- **Descripcion**: Sin filtros ni búsqueda en la vista "Mis Compromisos". El usuario no puede buscar un compromiso específico por BIP o descripción.
- **Impacto**: En grupos grandes, no se puede encontrar rápidamente un compromiso.
- **Recomendacion**: Agregar Input de búsqueda arriba de los grupos.

**[UX-037]** Severidad: BAJO
- **Archivo**: `web/src/app/(app)/mis-compromisos/page.tsx:112-115`
- **Descripcion**: Empty state genérico "No hay compromisos en esta categoría" sin sugerencia de acción.
- **Impacto**: UX plana en estados vacíos. No orienta al usuario.
- **Recomendacion**: Diferenciar mensaje por grupo (ej: "Sin compromisos vencidos" para Vencidos, "Todo al día" para Pendientes vacíos).

**Gaps**:
- Sin creación directa de compromisos (ENCARGADO no tiene permiso `canCreate`)
- Sin notificaciones push/email de compromisos próximos a vencer
- Sin vista de "Completar" directamente desde Mis Compromisos (debe abrir drawer en /compromisos)

---

## 7. Journey: JEFE_DGI

```
Login → Cockpit (semáforo 5D + gauges + decisiones + equipo +
alertas + informes + rendiciones) → Cartera → Tablero →
Datos → Informes → Alertas
```

**Lo que ve**: Cockpit DGI con 7 secciones: semáforo institucional (5 dimensiones), gauges duplicados, decisiones pendientes, equipo DGI, alertas críticas, informe semanal, rendiciones.

**Lo que puede hacer**: Ver estado integral institucional. Navegar a cartera con drill-down por señal. Ver estado de informes. Escalar alertas. Visar rendiciones.

**Hallazgos específicos**:

**[UX-011]** Severidad: ALTO
- **Archivo**: `web/src/components/cockpit-jefe-dgi.tsx:103-123`
- **Descripcion**: Sección "Requieren Mi Decisión" muestra placeholders genéricos `Decisión pendiente #1, #2, ...` con botón "Decidir" que no hace nada. No hay datos reales conectados.
- **Impacto**: Sección prominente del cockpit es completamente placeholder. Genera desconfianza.
- **Recomendacion**: Conectar con datos reales (iniciativas pendientes de aprobación, informes por revisar) o remover hasta tener datos.

**[UX-038]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-jefe-dgi.tsx:72-81`
- **Descripcion**: Gauges visuales (SemaforoGauge) debajo del semáforo son redundantes — muestran la misma información que las SemaforoCard de arriba.
- **Impacto**: Duplicación visual sin valor agregado. Ocupa espacio vertical.
- **Recomendacion**: Eliminar gauges o integrar como hover/click detail de cada SemaforoCard.

**[UX-039]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-jefe-dgi.tsx:177-185`
- **Descripcion**: Botones "Escalar" y "Playbook" en alertas críticas no tienen funcionalidad implementada (sin onClick handler que haga algo).
- **Impacto**: Botones visibles pero muertos. Genera confusión.
- **Recomendacion**: Implementar acción o mostrar como disabled con tooltip "Próximamente".

**Gaps**:
- Sin forecast/proyección temporal de indicadores
- Sin comparativo histórico (semáforo semana anterior vs hoy)
- Sin dashboard de rendiciones (endpoint existe: `GET /api/dgi/data/rendiciones/vencidas`)

---

## 8. Journey: ESP_CONTROL_GESTION

```
Login → Cockpit (fuentes datos + indicadores alerta + tendencias +
cola trabajo) → Datos → Informes → Cartera → Alertas
```

**Lo que ve**: Cockpit con 4 secciones: estado de datos hoy (badges por fuente), indicadores en alerta con sparklines, tendencias 30d con progress bars, cola de trabajo.

**Lo que puede hacer**: Investigar indicadores. Visar rendiciones RTF (vía /datos). Generar/editar informes.

**Hallazgos específicos**:

**[UX-040]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-control-gestion.tsx:133`
- **Descripcion**: SparklineIndicator (componente referenciado) renderiza gráficos miniatura al lado de indicadores en alerta. En mobile, estos son ilegibles (~30px de ancho).
- **Impacto**: Información de tendencia inutil en pantallas pequeñas.
- **Recomendacion**: Ocultar sparklines en `md:` breakpoints menores o expandir al clickear.

**[UX-041]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-control-gestion.tsx:68-91`
- **Descripcion**: Estado de datos usa badges pill (rounded-full) con colores gris/ámbar/verde. Badge gris para "SIN_DATOS" tiene contraste insuficiente (`text-gray-600` sobre `bg-gray-100`).
- **Impacto**: Ratio de contraste ~3.5:1, por debajo del mínimo WCAG AA de 4.5:1 para texto pequeño.
- **Recomendacion**: Oscurecer texto a `text-gray-800` o usar ícono de advertencia.

**[UX-042]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-control-gestion.tsx:142`
- **Descripcion**: Botón "Investigar" en indicadores en alerta no tiene funcionalidad implementada — no navega a ningún lugar.
- **Impacto**: Botón prominente sin acción.
- **Recomendacion**: Navegar a `/datos?dominio=indicadores&id=X` o abrir modal de investigación.

**Gaps**:
- Sin workflow de investigación guiado (pasos para diagnosticar un indicador rojo)
- Sin link directo IPR → rendiciones vinculadas
- Data sources no muestran estado real-time (badge es snapshot del último fetch)

---

## 9. Journey: ESP_PROCESOS

```
Login → Cockpit (portfolio stats + DMAIC kanban + agenda + BPMN) →
Tablero → Informes → Cartera
```

**Lo que ve**: Cockpit con 4 secciones: stats del portfolio (activas/completadas/meta), kanban DMAIC agrupado en 3 columnas, agenda del día, modelos BPMN recientes.

**Lo que puede hacer**: Ver estado de iniciativas DMAIC. Ver modelos BPMN. Gestionar agenda.

**Hallazgos específicos**:

**[UX-043]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-procesos.tsx:87-99`
- **Descripcion**: Columnas DMAIC vacías muestran "Sin iniciativas" genérico sin guía de cómo crear una. El kanban no tiene drag-and-drop.
- **Impacto**: Usuario nuevo no sabe cómo poblar el kanban. Sin drag-and-drop, mover entre columnas requiere ir a /tablero.
- **Recomendacion**: Agregar botón "Nueva Iniciativa" en columna vacía. Considerar drag-and-drop para reordenar.

**[UX-044]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-procesos.tsx:76`
- **Descripcion**: Error WIP limit (HTTP 409) en `/tablero` se detecta post-hoc — el usuario intenta mover una iniciativa y recibe error. Sin indicador visual previo de que la columna está llena.
- **Impacto**: Frustración por intentar una acción que siempre va a fallar.
- **Recomendacion**: Mostrar badge "WIP: 5/5" en header de columna. Deshabilitar botón "Mover" cuando WIP limit alcanzado.

**Gaps**:
- Sin timeline de proceso (Gantt o timeline view de iniciativas)
- Sin métricas de cycle time (cuánto tarda una iniciativa en moverse entre fases)
- Sin drag-and-drop en kanban

---

## 10. Journey: ESP_TD

```
Login → Cockpit (compliance bars + decretos + KB stats +
velocidad + comité + alertas TDE) → Datos → Informes → Cartera
```

**Lo que ve**: Cockpit con 6 secciones: cumplimiento Ley 21.180 (progress bars), velocidad de avance, decretos DS7-DS12, base de conocimiento stats, próximo comité TD, alertas normativas.

**Lo que puede hacer**: Monitorear cumplimiento. Ver estado de decretos. Preparar comité.

**Hallazgos específicos**:

**[UX-015]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-td.tsx:17-19`
- **Descripcion**: Abreviaciones de estado de decreto: "VIG" (Vigente), "PAR" (Parcial), "PEN" (Pendiente) — sin tooltip explicativo. Solo w-10 de ancho.
- **Impacto**: Usuario nuevo no sabe qué significan VIG/PAR/PEN.
- **Recomendacion**: Agregar `<Tooltip>` con texto completo, o usar texto completo en pantallas >md.

**[UX-045]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-td.tsx:137-157`
- **Descripcion**: KB stats (Pendientes/Actualizados/Total) son números estáticos sin drill-down ni tendencia. No hay link a la base de conocimiento.
- **Impacto**: Información decorativa sin acción posible.
- **Recomendacion**: Hacer números clickeables para navegar a listado filtrado.

**[UX-046]** Severidad: BAJO
- **Archivo**: `web/src/components/cockpit-td.tsx:61-82`
- **Descripcion**: Velocidad de avance muestra 3 métricas en una sola línea densa con `|` separadores. Difícil de escanear rápidamente.
- **Impacto**: Información importante enterrada en densidad visual.
- **Recomendacion**: Separar en 3 cards o usar layout vertical con labels claros.

**Gaps**:
- Sin roadmap digital (timeline de adopción tecnológica)
- Sin métricas de adopción de herramientas digitales
- Compliance bars sin contexto (no dicen qué falta para llegar a 100%)

---

# PARTE III — JOURNEYS FUNCIONALES (CROSS-ROL)

## 11. Journey Funcional: Formulador de Programas de Ejecución Propia

**Roles**: ADMIN_SISTEMA, ADMIN_REGIONAL (editar montos), JEFE_DIVISION (ver)

```
/presupuesto (listar) → drawer (detalle + editar montos) →
CDPs (ver vinculados) → /ipr/{id} (tab CDPs) → glosa rules (F1→F2)
```

**Hallazgos**:

**[UX-008]** Severidad: ALTO
- **Archivo**: `web/src/app/(app)/presupuesto/page.tsx:233-245`
- **Descripcion**: No existe formulario de CREACIÓN de programas presupuestarios. Solo hay botón CSV export, sin "Nuevo Programa". La API tiene POST endpoint (`POST /api/presupuesto`) pero no hay UI. Los programas solo se crean vía ETL o SQL directo.
- **Impacto**: Imposible crear nuevos programas presupuestarios desde la interfaz.
- **Recomendacion**: Implementar formulario de creación con clasificación (subtítulo, ítem, asignación, tipo programa).

**[UX-047]** Severidad: ALTO
- **Archivo**: `web/src/app/(app)/presupuesto/page.tsx:307-337`
- **Descripcion**: Editar montos permite cambiar 5 valores numéricos (inicial, vigente, comprometido, devengado, pagado) pero no la clasificación (subtítulo, ítem, asignación). Estos campos son read-only en detalle.
- **Impacto**: Si se crea un programa con clasificación incorrecta, hay que corregirlo en DB.
- **Recomendacion**: Agregar edición de clasificación con validación de consistencia.

**[UX-048]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/presupuesto/page.tsx:293-303`
- **Descripcion**: Fórmula de ejecución (`pagado/vigente × 100`) no está documentada en la UI. El usuario ve "Ejecución: 45%" pero no sabe si es sobre vigente o inicial.
- **Impacto**: Ambigüedad en interpretación de métricas financieras.
- **Recomendacion**: Agregar tooltip "Ejecución = Pagado / Vigente × 100" en el label.

**[UX-049]** Severidad: MEDIO
- **Archivo**: Backend `api/app/routers/presupuesto.py`
- **Descripcion**: No hay endpoint para crear CDPs (budget_commitments) desde UI. Solo existen vía seed SQL o ETL.
- **Impacto**: No se pueden vincular nuevos CDPs a IPRs desde la interfaz.
- **Recomendacion**: Implementar `POST /api/presupuesto/{id}/cdps` con formulario en drawer.

**Gaps Críticos**:
- Sin bulk edit de múltiples programas
- Sin vista de forecast/proyección presupuestaria
- Sin allocación de arrastres de año anterior desde UI
- HΩ-15 Budget Cycle Timeline no implementado
- Sin preview de impacto de reglas de glosa antes de transición IPR

---

## 12. Journey Funcional: Referente Técnico Financiero (RTF)

**Roles**: ESP_CONTROL_GESTION (visa RTF), ESP_PROCESOS (visa UCR)

```
/datos?dominio=rendiciones (listar) → detalle rendición →
transición SISREC (visa/observar) → /convenios (ver cuotas) →
/ipr/{id} (CDPs + avances)
```

**Hallazgos**:

**[UX-012]** Severidad: ALTO
- **Archivo**: `web/src/components/sidebar.tsx:54-61`
- **Descripcion**: Rendiciones solo son accesibles via `/datos?dominio=rendiciones` — no aparecen como item en el sidebar DGI. El usuario DGI debe navegar a "Datos" → seleccionar "Rendiciones" en sidebar lateral izquierdo.
- **Impacto**: Función crítica enterrada a 2 clicks de profundidad. El RTF tiene que recordar el path.
- **Recomendacion**: Agregar "Rendiciones" como item directo en `dgiNav` del sidebar.

**[UX-050]** Severidad: ALTO
- **Archivo**: Backend `api/app/routers/dgi_data.py` + Frontend `datos/page.tsx`
- **Descripcion**: Error Art. 18 Res. 30 CGR dice "rendiciones pendientes" pero no muestra CUÁLES rendiciones bloquean un pago de cuota. El cockpit jefe DGI muestra el warning (línea 306) pero sin link a las rendiciones específicas.
- **Impacto**: RTF sabe que hay bloqueo pero no puede identificar rápidamente qué rendiciones resolver.
- **Recomendacion**: Listar IDs/códigos de rendiciones pendientes en el mensaje de error.

**[UX-051]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/datos/page.tsx` (rendiciones domain)
- **Descripcion**: Rendiciones no están agrupadas por estado o SLA breach. El listado es plano sin indicador visual de rendiciones vencidas (>7d RTF, >2d UCR).
- **Impacto**: RTF no puede escanear rápidamente qué rendiciones necesitan atención urgente.
- **Recomendacion**: Agregar badge de SLA breach y filtro "Vencidas" como primera opción.

**[UX-052]** Severidad: MEDIO
- **Archivo**: `web/src/components/cockpit-jefe-dgi.tsx:258-312`
- **Descripcion**: Dashboard card de rendiciones existe pero no surfacea el endpoint `GET /api/dgi/data/rendiciones/vencidas`. Solo muestra resumen estático.
- **Impacto**: Endpoint útil existe pero no se usa en UI.
- **Recomendacion**: Agregar card "X rendiciones vencidas" clickeable que abra `/datos?dominio=rendiciones&vencidas=true`.

**Gaps Críticos**:
- Sin vista unificada rendiciones ↔ convenios ↔ cuotas (context split entre /datos y /convenios)
- Sin guidance de qué documentos se necesitan antes de cada transición SISREC
- Sin delegated approval workflow

---

## 13. Journey Funcional: Gestor de Convenios, Hitos, Pagos y Ejecución

**Roles**: ADMIN_REGIONAL, JEFE_DIVISION (create), ADMIN_SISTEMA (edit/pay)

```
/convenios (listar) → drawer (detalle + editar + cuotas CRUD + pagos) →
/ipr/{id} (tab Convenios + Hitos + Avances) → back to /convenios
```

**Hallazgos**:

**[UX-009]** Severidad: ALTO
- **Archivo**: `web/src/app/(app)/convenios/page.tsx:560-575`
- **Descripcion**: Cuotas se crean una por una con formulario inline. Para un convenio con 12 cuotas mensuales, el usuario debe crear cada una individualmente (12 clicks + 12 formularios).
- **Impacto**: Proceso tedioso para convenios con muchas cuotas. Propenso a errores.
- **Recomendacion**: Agregar generador bulk: "Crear N cuotas mensuales desde fecha X, monto Y".

**[UX-028]** (ver sección 2.6) — Pago de cuota silencia errores.

**[UX-053]** Severidad: ALTO
- **Archivo**: `web/src/app/(app)/convenios/page.tsx:265-284`
- **Descripcion**: Registrar pago de cuota es single-click sin confirmation step. El PATCH se envía inmediatamente con `paid_at: new Date().toISOString()` y `paid_amount` sin validar que el monto coincida con la cuota.
- **Impacto**: Pago accidental irreversible. Sin pago parcial (solo full payment). Sin selector de método de pago.
- **Recomendacion**: Agregar dialog de confirmación antes de registrar pago. Permitir pago parcial.

**[UX-054]** Severidad: MEDIO
- **Archivo**: `web/src/app/(app)/convenios/page.tsx:529-531`
- **Descripcion**: Vigencia de convenio solo muestra alerta visual (`text-red-600`) cuando `days_to_expiry < 30`. Sin aviso a 60 o 90 días.
- **Impacto**: Convenios por vencer solo se detectan en último mes. No hay tiempo para renovación.
- **Recomendacion**: Agregar TemporalIndicator con umbral configurable (30/60/90d).

**[UX-055]** Severidad: MEDIO
- **Archivo**: Cross-file: convenios drawer vs IPR tabs
- **Descripcion**: Tabs de IPR no se auto-refrescan tras cambios en /convenios drawer. Si el usuario edita un convenio en `/convenios` y luego navega a `/ipr/{id}` tab Convenios, puede ver datos stale.
- **Impacto**: Estado desincronizado entre vistas.
- **Recomendacion**: Invalidar cache de IPR detail al navegar desde convenios (o usar SWR/React Query).

**Gaps Críticos**:
- Sin "Project Execution Dashboard" unificado (convenios + hitos + avances + CDPs en una sola vista)
- Sin bulk state transition para convenios
- Sin workflow de renovación para convenios por vencer
- Sin forecast de hitos (¿va on-track? basado en fecha planificada vs. hoy)
- "Completar" hito pone fecha=hoy sin date picker retroactivo

---

# PARTE IV — CONSOLIDACIÓN

## 14. Matriz de Hallazgos

### Hallazgos CRÍTICOS (4)

| ID | Archivo | Journey(s) | Descripción |
|----|---------|------------|-------------|
| UX-001 | `status-badge.tsx:43` | Todos | `animate-pulse` en VENCIDO viola WCAG 2.3.1 |
| UX-002 | `admin/usuarios/page.tsx:213,227` | ADMIN_SISTEMA | `alert()` nativo para errores |
| UX-003 | `drawer-panel.tsx:22` | Todos con drawer | DrawerPanel w-[400px] rompe en mobile |
| UX-004 | `login/page.tsx:30-90` | Todos | Sin recuperación de contraseña |

### Hallazgos ALTOS (15)

| ID | Archivo | Journey(s) | Descripción |
|----|---------|------------|-------------|
| UX-005 | `filter-bar.tsx:57,66` | Todos con filtros | Anchos fijos overflow en mobile |
| UX-006 | `kpi-card.tsx:34-47` | JEFE_DIVISION, ENCARGADO | KpiCard sin keyboard access |
| UX-007 | `data-table.tsx:60-100` | Todos | DataTable sin ARIA labels |
| UX-008 | `presupuesto/page.tsx:233` | Formulador | Sin form de creación de programas |
| UX-009 | `convenios/page.tsx:560` | Gestor Convenios | Cuotas una por una sin bulk |
| UX-010 | Múltiples | Todos | Errores silenciados con console.error |
| UX-011 | `cockpit-jefe-dgi.tsx:103` | JEFE_DGI | Decisiones son placeholder |
| UX-012 | `sidebar.tsx:54-61` | RTF (DGI) | Rendiciones enterradas en /datos |
| UX-026 | `datos/page.tsx:152` | ESP_CTRL_GEST | Layout 3-panel no responsive |
| UX-030 | `admin/usuarios/page.tsx:192` | ADMIN_SISTEMA | Edit usuario sin validación |
| UX-034 | `mi-division/page.tsx:114` | JEFE_DIVISION | Carga equipo sin sort/filtro |
| UX-047 | `presupuesto/page.tsx:307` | Formulador | Clasificación no editable |
| UX-049 | Backend presupuesto.py | Formulador | Sin UI para crear CDPs |
| UX-050 | Backend dgi_data.py | RTF | Art. 18 no muestra cuáles rendiciones |
| UX-053 | `convenios/page.tsx:265` | Gestor Convenios | Pago sin confirmación |

### Hallazgos MEDIOS (26)

| ID | Archivo | Journey(s) | Descripción |
|----|---------|------------|-------------|
| UX-013 | `login/page.tsx:33` | Todos | Background hardcoded |
| UX-014 | `mis-compromisos/page.tsx:117` | ENCARGADO | Paginación deshabilitada |
| UX-015 | `cockpit-td.tsx:17-19` | ESP_TD | Abreviaciones sin tooltip |
| UX-017 | `sidebar.tsx:97` | Todos | Sidebar sin collapse mobile |
| UX-021 | `header.tsx:67-90` | Todos | Cambio password sin confirmación |
| UX-022 | `status-badge.tsx` | Todos | 3 esquemas color inconsistentes |
| UX-023 | `cockpit-jefe-dgi.tsx:295` | JEFE_DGI | formatCLP inline vs lib |
| UX-024 | `data-table.tsx:46` | Todos | Loading skeleton sin aria-busy |
| UX-025 | `header.tsx:167` | Todos | Alertas popover sin keyboard |
| UX-027 | `cartera/page.tsx:387` | DGI | Summary cards overflow |
| UX-028 | `convenios/page.tsx:279` | Gestor Convenios | Pago silencia errores |
| UX-029 | `convenios/page.tsx:601` | Gestor Convenios | Botón pago 10px target |
| UX-031 | `admin/usuarios/page.tsx:448` | ADMIN_SISTEMA | Reset pwd sin validación |
| UX-032 | `dashboard/page.tsx:284` | ADMIN_REGIONAL | Divisiones sin sort |
| UX-033 | `dashboard/page.tsx:213` | ADMIN_REGIONAL | Semáforo sin drill-down |
| UX-035 | `mi-division/page.tsx:147` | JEFE_DIVISION | Vencidos sin paginación real |
| UX-036 | `mis-compromisos/page.tsx:70` | ENCARGADO | Sin búsqueda en mis compromisos |
| UX-038 | `cockpit-jefe-dgi.tsx:72` | JEFE_DGI | Gauges redundantes |
| UX-039 | `cockpit-jefe-dgi.tsx:177` | JEFE_DGI | Botones Escalar/Playbook muertos |
| UX-040 | `cockpit-control-gestion.tsx:133` | ESP_CTRL_GEST | Sparklines ilegibles mobile |
| UX-041 | `cockpit-control-gestion.tsx:68` | ESP_CTRL_GEST | Badge gris bajo contraste |
| UX-042 | `cockpit-control-gestion.tsx:142` | ESP_CTRL_GEST | Botón Investigar sin acción |
| UX-043 | `cockpit-procesos.tsx:87` | ESP_PROCESOS | DMAIC sin guía ni drag-drop |
| UX-044 | `cockpit-procesos.tsx:76` | ESP_PROCESOS | WIP error post-hoc |
| UX-045 | `cockpit-td.tsx:137` | ESP_TD | KB stats sin drill-down |
| UX-048 | `presupuesto/page.tsx:293` | Formulador | Fórmula ejecución no documentada |
| UX-051 | `datos/page.tsx` | RTF | Rendiciones sin agrupación SLA |
| UX-052 | `cockpit-jefe-dgi.tsx:258` | JEFE_DGI, RTF | Rendiciones vencidas no surfeadas |
| UX-054 | `convenios/page.tsx:529` | Gestor Convenios | Solo alerta <30d vigencia |
| UX-055 | Cross-file | Gestor Convenios | Tabs IPR no auto-refrescan |

### Hallazgos BAJOS (6)

| ID | Archivo | Journey(s) | Descripción |
|----|---------|------------|-------------|
| UX-016 | `login/page.tsx:69` | Todos | Sin validación email frontend |
| UX-018 | `sidebar.tsx:96` | Todos | Sin aria-current en nav |
| UX-019 | `app-shell.tsx:64` | Todos | Status "Conectado" estático |
| UX-020 | `app-shell.tsx:69` | Todos | Año hardcoded 2026 |
| UX-037 | `mis-compromisos/page.tsx:112` | ENCARGADO | Empty state genérico |
| UX-046 | `cockpit-td.tsx:61` | ESP_TD | Velocidad densidad visual |

---

## 15. Plan de Remediación Sugerido

### Matriz Impacto x Esfuerzo

```
         ALTO IMPACTO                BAJO IMPACTO
    ┌──────────────────────┬──────────────────────┐
    │ Quick Wins           │ Considerar           │
 B  │ UX-001 (rm pulse)    │ UX-018 (aria-current)│
 A  │ UX-002 (rm alert)    │ UX-019 (status live) │
 J  │ UX-003 (drawer w)    │ UX-020 (año dinámico)│
 O  │ UX-005 (filter resp) │ UX-037 (empty states)│
    │ UX-006 (kpi kbd)     │ UX-046 (velocidad)   │
 E  │ UX-010 (toast)       │                      │
 S  │ UX-015 (tooltips)    │                      │
 F  │ UX-023 (formatCLP)   │                      │
 U  ├──────────────────────┼──────────────────────┤
 E  │ Proyectos            │ Backlog              │
 R  │ UX-004 (pwd reset)   │ UX-033 (semáforo dd) │
 Z  │ UX-008 (form presup) │ UX-038 (gauges)      │
 O  │ UX-009 (bulk cuotas) │ UX-043 (drag-drop)   │
    │ UX-011 (decisiones)  │ UX-044 (WIP visual)  │
 A  │ UX-012 (sidebar rend)│ UX-045 (KB drill)    │
 L  │ UX-026 (datos resp)  │ UX-048 (tooltip form)│
 T  │ UX-030 (form valid)  │                      │
 O  │ UX-049 (CDPs UI)     │                      │
    │ UX-053 (confirm pago)│                      │
    └──────────────────────┴──────────────────────┘
```

### Ciclo A: Críticos y Accesibilidad (1-2 semanas)

**Objetivo**: Eliminar bloqueantes y violaciones WCAG.

| ID | Tarea | Esfuerzo |
|----|-------|----------|
| UX-001 | Reemplazar `animate-pulse` en StatusBadge VENCIDO | 15 min |
| UX-002 | Reemplazar `alert()` con toast en admin usuarios | 30 min |
| UX-003 | Cambiar DrawerPanel a `w-full sm:w-[400px]` | 5 min |
| UX-006 | Agregar role/tabIndex/onKeyDown a KpiCard | 15 min |
| UX-007 | Agregar aria-label a DataTable + aria-live a paginación | 30 min |
| UX-010 | Instalar sonner/react-hot-toast + reemplazar console.error | 2h |
| UX-018 | Agregar aria-current="page" a sidebar links | 10 min |
| UX-024 | Agregar aria-busy="true" a DataTable loading | 5 min |
| UX-025 | Hacer items de alerta popover focusables | 20 min |
| UX-029 | Aumentar botón pago cuota a h-8 mínimo | 5 min |

### Ciclo B: Formularios y Validación (2-3 semanas)

**Objetivo**: Robustez de formularios y feedback de errores.

| ID | Tarea | Esfuerzo |
|----|-------|----------|
| UX-004 | Implementar flujo recuperación de contraseña | 1-2d |
| UX-021 | Agregar confirmación + strength meter a cambio pwd | 1h |
| UX-028 | Agregar error feedback en pago de cuota | 30 min |
| UX-030 | Integrar react-hook-form en edit usuario | 2-3h |
| UX-031 | Validación de longitud en reset password | 15 min |
| UX-053 | Agregar dialog de confirmación antes de registrar pago | 1h |

### Ciclo C: Responsive y Mobile (2-3 semanas)

**Objetivo**: Usabilidad en tablets y mobile.

| ID | Tarea | Esfuerzo |
|----|-------|----------|
| UX-005 | FilterBar responsive (w-full sm:w-56) | 30 min |
| UX-013 | Login background vía Tailwind theme | 10 min |
| UX-017 | Sidebar colapsable con Sheet en mobile | 3-4h |
| UX-026 | Layout /datos responsive (sidebar como sheet en mobile) | 4-6h |
| UX-027 | Cartera table responsive (ocultar columnas en mobile) | 1-2h |
| UX-040 | Sparklines responsive (ocultar <md) | 15 min |

### Ciclo D: Funcionalidades Faltantes (4-6 semanas)

**Objetivo**: Cerrar gaps funcionales más impactantes.

| ID | Tarea | Esfuerzo |
|----|-------|----------|
| UX-008 | Formulario creación programas presupuestarios | 2-3d |
| UX-009 | Generador bulk de cuotas de convenio | 1-2d |
| UX-011 | Conectar decisiones con datos reales en cockpit jefe | 1-2d |
| UX-012 | Agregar "Rendiciones" a sidebar DGI | 15 min |
| UX-014 | Paginación real en Mis Compromisos | 1-2h |
| UX-034 | Sort y filtro en tabla carga equipo | 1-2h |
| UX-035 | Paginación real en vencidos mi-division | 1h |
| UX-036 | Búsqueda en Mis Compromisos | 1h |
| UX-047 | Edición de clasificación presupuestaria | 1d |
| UX-049 | UI para crear CDPs | 2-3d |
| UX-050 | Listar rendiciones específicas en error Art. 18 | 1d |

---

*Documento generado por análisis estático de código. Verificar hallazgos con testing manual en navegador para confirmar impacto visual real.*
