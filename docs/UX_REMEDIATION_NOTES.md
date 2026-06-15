# UX/UI Remediation Notes — GORE_OS

Registro de la remediación de los 89 hallazgos verificados de la auditoría UX/UI
(8 críticos, 34 mayores, 47 menores). Una entrada por archivo tocado: qué hallazgo,
qué cambió, cómo se verificó. Se actualiza por cluster; no se duplica.

Barra de aceptación: cero pantallas rotas · cero skeleton eterno · cero formato
`mm/dd/yyyy` · cero tilde faltante en superficie de usuario · cero acción destructiva
sin `ConfirmDialog` · dark mode con contraste AA · todo estado vacío con voz + CTA ·
todo error distinguible del vacío.

---

## Fase 0 — Átomos compartidos (hechos a mano, typecheck `tsc --noEmit` EXIT:0)

Estos son los puntos de apalancamiento: un cambio se propaga a decenas de sitios.
Se hacen una vez y los clusters los **consumen** (importan), nunca los editan.

| Archivo | Hallazgo | Cambio | Verificación |
|---|---|---|---|
| `web/src/components/status-badge.tsx` | 🔴 #3 dark mode + labels crudos RS/OT/ITF | `tone(color)` con mapa estático de clases light+dark (Tailwind exige literales); configs IPR/Acto a `{label,color}`; switch-cases outline migrados a `tone()`; códigos de evaluación ahora muestran la glosa de `_EVAL_LABELS` (RS→"Rec. Satisfactoria", OT→"Observado Técnicamente"…). | tsc EXIT:0 |
| `web/src/components/data-table.tsx` | 🔴 #6 error disfrazado de vacío + empty que miente | Props `error?`/`onRetry?`/`hasActiveFilters?`/`onClearFilters?`. Estado de error con icono ámbar + "No se pudieron cargar los datos / Reintentar"; vacío-con-filtros ("Sin coincidencias / Limpiar filtros") vs realmente-vacío; pager oculto en error/vacío. | tsc EXIT:0 |
| `web/src/lib/format.ts` | 🟠 números sin marco / UTM roto por compacto | `formatCLPExact`→"$67.294", `formatUTM` (alias), `formatMillones`→"$5.000 millones". `formatCLP` compacto queda solo para tiles. | tsc EXIT:0 |
| `web/src/components/date-field.tsx` (NUEVO) | 🟠 fecha gringa (37 inputs) | Input enmascarado `dd/mm/aaaa ⇄ yyyy-mm-dd`, sin deps nuevas (no había `react-day-picker`); rechaza fechas imposibles (31/02), valida `min`; hereda tokens (dark). Drop-in de `<input type="date">`. | tsc EXIT:0 |
| `web/src/components/clickable.tsx` (NUEVO) | 🟡 ~111 `<div onClick>` inaccesibles | Wrapper `role=button` + `tabIndex` + Enter/Space + focus ring. | tsc EXIT:0 |
| `web/src/components/drawer-panel.tsx` | 🟠 reversibilidad universal | Prop `isDirty?`; al cerrar con cambios → `ConfirmDialog` "Cambios sin guardar… Descartar / Seguir editando". Punto único que propaga a todos los drawers. | tsc EXIT:0 |
| `web/src/app/(app)/ipr/components/ipr-constants.ts` | 🟠 badges sin dark + tabs ciegas | Variantes `dark:` en `mechanismColors`/`mcdPhaseColors`; nuevo `PHASE_RELEVANT_TABS` para resaltar tabs por fase. | tsc EXIT:0 |
| `web/src/app/(app)/ipr/components/ipr-badges.tsx` (NUEVO) | 🟠 diseño: extraer MechanismBadge/PhaseBadge | `MechanismBadge`/`PhaseBadge` dark-aware, reemplazan los `Record` inline de `ipr/page.tsx`. | tsc EXIT:0 |

## Fase 0.5 — Cluster DGI dashboard (hecho a mano; mayor riesgo, acoplado)

| Archivo | Hallazgo | Cambio | Verificación |
|---|---|---|---|
| `web/src/app/(app)/dashboard/page.tsx` | 🔴 #1 skeleton eterno + 🔴 #2 cockpits muertos | Ruteo por población: `dgi → <DgiCockpitRouter/>`, operativa → `<CommandCenter/>`. Monta los ~1.181 líneas de cockpits vivos (verificado `/api/dgi/cockpit` 200 con datos para los 4 roles DGI) y da a los 3 especialistas su cockpit real en vez del skeleton roto. | curl 200 × 4 roles; tsc EXIT:0 |
| `web/src/app/(app)/dashboard/components/command-center.tsx` | 🔴 #1 (defensivo) | Línea 104 `DGI_KPI_ROLES`→`DGI_TEAM_ROLES` (la constante ya existía sin usar): `ModuleDgiTeam` solo para JEFE_DGI. | tsc EXIT:0 |
| `web/src/app/(app)/dashboard/components/module-dgi-team.tsx` | 🔴 #1 carga real vs campo ausente | Estado `loading` explícito; resuelto-sin-datos → empty honesto "Sin actividad del equipo por ahora", nunca skeleton infinito. | tsc EXIT:0 |

## Fase 1 — Clusters de propagación (Workflow `wf_3edd9e31-a0f`, completado)

8 clusters, archivos disjuntos, cada uno con verificador de contexto fresco. **Gate global `tsc --noEmit` EXIT:0** (los 8 + fundaciones compilan limpio). Veredictos:

| Cluster | Cierre | Evidencia clave (verificador fresco) |
|---|---|---|
| **admin** | ✅ total | #7 ConfirmDialog desactivar usuario + umbral/SNI; UTM→`formatCLPExact`; hint "Mínimo 8" al crear; `loadError`+Reintentar en 4 tabs; "Restablecer contraseña"; "ID Sujeto" = `tipo#prefijo`+tooltip; DateField en auditoría; tildes 0 residuales |
| **ipr_detail** | ⚠️ casi | #8 Información General siempre con "—" (`formatMillones`); jerga "Mover a la siguiente etapa"/"Confirmar avance"; tabs por fase (punto • vía `PHASE_RELEVANT_TABS`); empties con voz; stepper móvil; MechanismBadge/PhaseBadge. **Residual:** línea de gates con códigos crudos F3→F4 → corregido a mano |
| **ipr_listforms** | ⚠️ casi | #4 ComboboxAsync responsable (`/api/catalogs/users?search=`); drawer DateField+isDirty+toast+validación inline; ipr/page tabla→tarjetas `<md`+badges compartidos; nuevo isDirty+toast. **Residual:** 3 tildes en cartera → barrido |
| **ops_lists** | ✅ total | #6 `loadError`+Reintentar en convenios/actos/presupuesto/+8; hasActiveFilters+Limpiar; DateField rangos alertas/convenios (min=desde); presupuesto `formatMillones`/`formatCLPExact` + columna Programa muerta eliminada; convenios Receptor line-clamp; ConfirmDialog en anular/cerrar; tildes |
| **coordinacion** | ✅ total | #5 emptyTitle/Description + `decisionsError`+onRetry; 38 literales tildados + toasts; 3 DateField; isDirty en 2 drawers |
| **dgi_gov** | ⚠️ casi | DataTable error/retry/filters en 4 listas; accents por dominio (cartera→cyan, servicios→teal, informes→cyan); EmptyState con voz. **Residual:** escalamiento `amber`→`orange` (orange no existía en accents) → corregido a mano; KPI "meta" diferido (backend no expone target) |
| **dgi_data** | ⚠️ casi | tablero doble-vacío resuelto; cuellos `tableError`+EmptyState+accent; calendario DateField+accent; datos/procesos error+filters+isDirty. **Residuales:** 4 tildes ([id] pages) → barrido; "filtro de rol 7/15" no existe en el archivo (superficie inexistente, diferido honesto) |
| **shell_a11y** | ✅ total | skip-link "Saltar al contenido"+`#main-content`; aria-label "Buscar"; ⌘K/Ctrl K por plataforma; sheet "Cerrar"; Clickable; toques ≥44px; gore-mark `#F88F3F`; centro-de-mando rose→indigo+cards dark; "Testing" padding; login contraste `/25`; tildes dev |

## Fase 2 — Residuales (hechos a mano + agente de barrido)

| Archivo | Residual | Cambio |
|---|---|---|
| `components/page-header.tsx` | `orange`/`amber` faltaban en `ACCENT_BORDER` | añadidos (habilita accent literal del spec) |
| `app/(app)/escalamiento/page.tsx` | accent `amber` colisiona con alertas | → `orange` (≠ rose=riesgos, ≠ amber=alertas) |
| `app/(app)/ipr/components/ipr-transition-panel.tsx` | "Gates para F3 → F4:" (códigos crudos + jerga EN) | → "Requisitos para pasar de {fase} a {fase}:" con glosa |
| (agente de barrido) | 18 inputs `type="date"` sin migrar + 7 tildes | → `<DateField>` en 10 archivos + tildes en cartera/cuellos/tablero |

## Fase 3 — Lo que la re-captura visual atrapó (y la revisión de código perdió)

La comparación de capturas **antes/después** reveló dos cosas que ningún verificador de contexto fresco detectó por leer solo el código:

| Archivo | Hallazgo | Causa raíz real | Cambio |
|---|---|---|---|
| `app/(app)/coordinacion/page.tsx:985` | 🔴 **#5 cuerpo en blanco — NO era el empty-state** | `useTabParam("decisiones")` pasa el tab por defecto como **nombre del parámetro** (`paramName`), no como `defaultValue`. La firma es `useTabParam(paramName="tab", defaultValue="")`. Sin `?tab=` en la URL → `value=""` → `<Tabs>` no matchea ningún `<TabsContent>` → cuerpo vacío. El copy del empty-state era irrelevante: la tabla nunca llegaba a renderizar. | `useTabParam("tab", "decisiones")`. Único misuse en el repo (las otras 3 llamadas son correctas). |
| `components/sidebar.tsx:301` | 🟡 "esting" (la "T" tapada) | El indicador de dev de Next.js (círculo "N", `position:fixed` bottom-left, **solo en dev**) solapa el link "Testing" del sidebar. El verificador apuntó al título de la página `/dev/testing`, no al link del sidebar. | `pb-1`→`pb-12` en el bloque `{devMode && ...}` (dev-only, sin impacto en producción). |

**Lección:** los verificadores de contexto fresco confirmaron que el copy del empty-state existía (cierto) y declararon #5 cerrado — pero "código presente" ≠ "pantalla funciona". La evidencia de runtime (capturas + endpoints 200 con cuerpo vacío) fue la que expuso el bug del `useTabParam`. **La verificación visual no es opcional para hallazgos de "pantalla rota".**

## Gate de verificación (evidencia)

| Gate | Resultado | Nota |
|---|---|---|
| `tsc --noEmit` (contenedor) | **EXIT:0** | type-check limpio en todo el grafo, tras los 8 clusters + barridos + fixes finales |
| `npm run build` (`next build`) | **EXIT:0** — "✓ Compiled successfully in 20.5s", 56/56 páginas | bundle de producción + prerender OK; Next 16 no corre ESLint durante build |
| `npm run lint` (`next lint`) | **EXIT:1 — 16 errores PRE-EXISTENTES** | reglas estrictas `react-hooks/purity` (Date.now en render) y `set-state-in-effect` (fetch-on-mount), sobre patrones ubicuos del codebase. Probado pre-existente: `deadline-cell.tsx:12` y `filter-bar.tsx:61` NO se tocaron esta sesión. No es regresión; no gatea el build. Fuera de alcance (refactor aparte). |
| Re-captura `audit-capture.mjs` | **49/49 OK, 0 FAIL** | sin error-overlays; criticales #1/#3/#5/#7 + login confirmados visualmente contra `audit-shots-baseline/` |

**Diferidos honestos (requieren backend, no frontend):** KPI "· meta 90%" (el backend no expone el target); "Mi Trabajo agrupa por ipr_codigo_bip" (requiere JOIN en `dashboard/action-items`). **N/A (superficie inexistente):** filtro de rol "7/15" en tablero (no existe tal control); sub-hallazgo de diálogo de deprecación en tab-config (ese flujo no existe). **Fuera de alcance UI:** descripciones de `core.financial_threshold` sin tilde ("Toma de Razon CGR") son datos de BD, no literales JSX — corregirlas es migración de datos.
