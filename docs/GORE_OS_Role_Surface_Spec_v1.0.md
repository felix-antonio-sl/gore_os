# GORE_OS — Especificacion Rol x Superficie v1.0

**Fecha**: 2026-03-22 | **Sesion**: C60
**Objetivo**: Mapear cada rol a su superficie real de uso para fundamentar poda UX.
**Fuentes**: User Journeys v3.2, sidebar.tsx, command-center.tsx, security.py, scope.py, PageGuard en 60 page.tsx

> **Estado (verificado 2026-06-14):** las recomendaciones R1-R7 están IMPLEMENTADAS en código. Las rutas legacy (`/nuevo`, `/mi-division`, `/comite-td`, `/coordinacion/divisiones`, `/admin/*`, `/servicios/*`) son redirect stubs de compatibilidad; la creación ocurre en drawers. De 60 `page.tsx`: 39 navegables + 21 redirect stubs.

---

## Inventario de Paginas

60 `page.tsx` en `web/src/app/(app)/`. Agrupadas por dominio:

| # | Ruta | Dominio | Guard |
|---|------|---------|-------|
| 1 | /dashboard | Universal | — |
| 2 | /centro-de-mando | Comando | AR, GOB, ADMIN_SISTEMA, JEFE_DGI |
| 3 | /riesgos | Comando | — (write: DGI + AR + ADMIN) |
| 4 | /riesgos/[id] | Comando | — (write: DGI + AR + ADMIN) |
| 5 | /ipr | Gestion IPR | — |
| 6 | /ipr/nuevo | Gestion IPR | — (canCreate: ADMIN, AR, GOB, ANALISTA) |
| 7 | /ipr/[id] | Gestion IPR | — (scope.py: 3-tier) |
| 8 | /ipr/cartera | Gestion IPR | — (sidebar: ADMIN, AR, GOB, JEFE_DGI) |
| 9 | /compromisos | Gestion IPR | — (3 views por rol) |
| 10 | /compromisos/nuevo | Gestion IPR | — (canCreate: ADMIN, AR, JEFE_DIV) |
| 11 | /mis-compromisos | Mi Trabajo | — (sidebar: ANALISTA, RTF, JURIDICO, JEFE_UNIDAD) |
| 12 | /problemas | Gestion IPR | — |
| 13 | /problemas/nuevo | Gestion IPR | — (canCreate: ADMIN, AR, GOB, JEFE_DIV, JEFE_DEPTO, JEFE_UNIDAD, ANALISTA) |
| 14 | /alertas | Gestion IPR | — |
| 15 | /presupuesto | Finanzas | — (canEdit: ADMIN, AR) |
| 16 | /presupuesto/nuevo | Finanzas | — (canEdit: ADMIN, AR) |
| 17 | /presupuesto/ciclo | Finanzas | — (canEdit: ADMIN, AR, GOB, JEFE_DIV) |
| 18 | /convenios | Finanzas | — |
| 19 | /convenios/nuevo | Finanzas | — (canCreate: ADMIN, AR, GOB, JEFE_DIV, JEFE_DEPTO, ANALISTA, JURIDICO) |
| 20 | /actos | Institucional | — |
| 21 | /actos/nuevo | Institucional | — (canCreate: ADMIN, AR, GOB, JEFE_DIV, ANALISTA, JURIDICO) |
| 22 | /reuniones | Institucional | — (canCreate: ADMIN, AR, JEFE_DIV) |
| 23 | /reuniones/nueva | Institucional | — (canCreate: ADMIN, AR, JEFE_DIV) |
| 24 | /reuniones/[id] | Institucional | — |
| 25 | /core-sessions | Gobernanza CORE | — (manager: ADMIN, AR, GOB, SECRETARIO) |
| 26 | /core-sessions/nueva | Gobernanza CORE | — (manager: ADMIN, AR, GOB, SECRETARIO) |
| 27 | /core-sessions/[id] | Gobernanza CORE | — (votar: CONSEJERO; gestionar: managers) |
| 28 | /servicios | Cross-population | — |
| 29 | /servicios/solicitar | Cross-population | — |
| 30 | /servicios/[id] | Cross-population | — (manage: DGI) |
| 31 | /mi-division | Mi Trabajo | — (sidebar: JEFE_DIV, JEFE_DEPTO) |
| 32 | /aprobaciones | Mi Trabajo | JEFE_DEPARTAMENTO, ADMIN_SISTEMA |
| 33 | /datos | DGI Analisis | — |
| 34 | /informes | DGI Analisis | — |
| 35 | /informes/[id] | DGI Analisis | — |
| 36 | /cartera | DGI Monitoreo | — |
| 37 | /tablero | DGI Mejora | — (canEdit: DGI) |
| 38 | /tablero/[id] | DGI Mejora | — (canEdit: DGI) |
| 39 | /procesos | DGI Mejora | — (canCreate: DGI) |
| 40 | /procesos/[id] | DGI Mejora | — (canEdit: DGI) |
| 41 | /procesos/progreso | DGI Mejora | — |
| 42 | /cuellos-de-botella | DGI Mejora | — (canCreate: DGI) |
| 43 | /cuellos-de-botella/[id] | DGI Mejora | — (canEdit: DGI) |
| 44 | /coordinacion | DGI Coordinacion | — |
| 45 | /coordinacion/divisiones | DGI Coordinacion | — |
| 46 | /escalamiento | DGI Coordinacion | — (write: DGI + read: operativa) |
| 47 | /escalamiento/[id] | DGI Coordinacion | — |
| 48 | /comite-td | DGI Coordinacion | — |
| 49 | /calendario | DGI Coordinacion | — |
| 50 | /admin/usuarios | Admin | ADMIN_SISTEMA |
| 51 | /admin/usuarios/nuevo | Admin | ADMIN_SISTEMA |
| 52 | /admin/divisiones | Admin | ADMIN_SISTEMA |
| 53 | /admin/umbrales | Admin | ADMIN_SISTEMA |
| 54 | /admin/niveles-sni | Admin | ADMIN_SISTEMA |
| 55 | /admin/salud-datos | Admin | ADMIN_SISTEMA |
| 56 | /admin/financing-tracks | Admin | ADMIN_SISTEMA |
| 57 | /admin/slas | Admin | ADMIN_SISTEMA |
| 58 | /admin/auditoria | Admin | ADMIN_SISTEMA |

**Total unicas**: 58 rutas (sin contar /login y /layout).

---

## Resumen

| # | Rol | Arquetipo | Poblacion | Journey | Pags Esenciales | Pags Secundarias | Pags Innecesarias |
|---|-----|-----------|-----------|---------|:---------------:|:----------------:|:-----------------:|
| 1 | ANALISTA | Ejecutor | op | J2 | 8 | 7 | 43 |
| 2 | RTF | Ejecutor | op | J3 | 4 | 5 | 49 |
| 3 | ASESOR_JURIDICO | Ejecutor | op | J4 | 5 | 5 | 48 |
| 4 | JEFE_DIVISION | Supervisor | op | J5+J6 | 10 | 7 | 41 |
| 5 | JEFE_DEPARTAMENTO | Supervisor | op | J15 | 8 | 7 | 43 |
| 6 | JEFE_UNIDAD | Supervisor | op | (J5 lite) | 6 | 5 | 47 |
| 7 | GOBERNADOR | Firmante+Estratega | op | J11+J12 | 8 | 8 | 42 |
| 8 | ADMIN_REGIONAL | Estratega+Firmante | op | J7 | 10 | 8 | 40 |
| 9 | ADMIN_SISTEMA | Configurador+Estratega | op | J16 | 17 | 10 | 31 |
| 10 | CONSEJERO_REGIONAL | Gobernanza CORE | op | J13 | 3 | 3 | 52 |
| 11 | SECRETARIO_EJECUTIVO | Gobernanza CORE | op | J14 | 4 | 4 | 50 |
| 12 | JEFE_DGI | Coordinador DGI | dgi | J10 | 16 | 4 | 38 |
| 13 | ESP_CONTROL_GESTION | Especialista DGI | dgi | J8 | 8 | 6 | 44 |
| 14 | ESP_PROCESOS | Especialista DGI | dgi | J9 | 8 | 6 | 44 |
| 15 | ESP_TD | Especialista DGI | dgi | (J9 variante) | 7 | 6 | 45 |

---

## 1. ANALISTA — Ejecutor

**Journey**: J2 "Formular IPR"
**Poblacion**: operativa
**Dashboard**: ModuleMyWork (task list) + ModuleFormulacion (pipeline F0-F2)
**Scope**: PERSONAL (assignee_id / formulator_id)
**Frecuencia**: diario

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | Pipeline formulacion + items pendientes | Diario |
| /ipr | Listar mis IPRs (auto-scope personal) | Diario |
| /ipr/nuevo | Crear nueva IPR | Semanal |
| /ipr/[id] | Completar satelites (partes, territorio, hitos, eval) | Diario |
| /compromisos | Ver mis compromisos (CompromisosWorkView) | Diario |
| /mis-compromisos | Lista agrupada por urgencia | Diario |
| /convenios | Consultar convenios vinculados a IPR | Semanal |
| /presupuesto | Verificar CDPs disponibles | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /problemas | Registrar problemas en IPR propios |
| /problemas/nuevo | Crear problema |
| /alertas | Ver alertas de mis IPRs |
| /actos | Consultar actos relacionados |
| /actos/nuevo | Crear borrador acto |
| /reuniones | Participar si convocado |
| /servicios | Solicitar servicios DGI |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /riesgos, /riesgos/[id] | Solo DGI + estrategas operan |
| /ipr/cartera | Solo estrategas / DGI |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /presupuesto/nuevo | Solo ADMIN, AR |
| /presupuesto/ciclo | Solo jefes/admin |
| /compromisos/nuevo | Solo ADMIN, AR, JEFE_DIV |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| /cartera | Solo DGI |
| /tablero, /tablero/[id] | Solo DGI |
| /procesos, /procesos/[id], /procesos/progreso | Solo DGI |
| /cuellos-de-botella (2 pags) | Solo DGI |
| /coordinacion (2 pags) | Solo DGI |
| /escalamiento (2 pags) | Solo DGI |
| /comite-td | Solo DGI |
| /calendario | Solo DGI |
| /datos | Solo DGI |
| /informes (2 pags) | Solo DGI |

---

## 2. RTF — Ejecutor

**Journey**: J3 "Revisar rendicion"
**Poblacion**: operativa
**Dashboard**: KPIs + AttentionStrip (sin modulo dedicado)
**Scope**: PERSONAL (assignee_id)
**Frecuencia**: diario (SLA 7 dias)

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | AttentionStrip items pendientes + KPIs | Diario |
| /mis-compromisos | Ver mis compromisos | Diario |
| /datos | Rendiciones tab: auto-filtro EN_REVISION_RTF, SLA visible | Diario |
| /ipr/[id] | Revisar contexto IPR de la rendicion | Diario |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /ipr | Buscar IPR especifica |
| /compromisos | Ver compromisos (CompromisosWorkView) |
| /convenios | Consultar convenio vinculado a rendicion |
| /alertas | Ver alertas relevantes |
| /servicios | Solicitar servicios DGI |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo estrategas |
| /riesgos (2 pags) | Solo DGI + estrategas |
| /ipr/nuevo | RTF no crea IPRs |
| /ipr/cartera | Solo estrategas / DGI |
| /presupuesto (3 pags) | No opera presupuesto |
| /actos (2 pags) | No firma ni visa actos |
| /problemas (2 pags) | No crea problemas |
| /reuniones (3 pags) | No convoca ni gestiona |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /convenios/nuevo | No crea convenios |
| /compromisos/nuevo | No crea compromisos |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 3. ASESOR_JURIDICO — Ejecutor

**Journey**: J4 "Visacion juridica"
**Poblacion**: operativa
**Dashboard**: ModuleJuridico (cola V.B. pendientes)
**Scope**: PERSONAL
**Frecuencia**: diario

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | ModuleJuridico — cola de V.B. pendientes | Diario |
| /actos | PendingQueue EN_REVISION + visar/devolver | Diario |
| /convenios | Auto-filtro EN_REVISION_JURIDICA | Diario |
| /mis-compromisos | Ver mis compromisos | Semanal |
| /ipr/[id] | Revisar contexto juridico de IPR | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /ipr | Buscar IPR especifica |
| /actos/nuevo | Crear borrador acto |
| /convenios/nuevo | Crear borrador convenio |
| /compromisos | Ver compromisos (CompromisosWorkView) |
| /servicios | Solicitar servicios DGI |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo estrategas |
| /riesgos (2 pags) | Solo DGI + estrategas |
| /ipr/nuevo | No crea IPRs |
| /ipr/cartera | Solo estrategas / DGI |
| /presupuesto (3 pags) | No opera presupuesto |
| /problemas (2 pags) | No crea problemas |
| /alertas | Consulta marginal |
| /reuniones (3 pags) | No convoca ni gestiona |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /compromisos/nuevo | No crea compromisos |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 4. JEFE_DIVISION — Supervisor

**Journey**: J5 "Estado de mi division" + J6 "Crisis/Alerta"
**Poblacion**: operativa
**Dashboard**: ModuleMyTeam (avatares, carga, drill-down)
**Scope**: DIVISION (sponsor_division_id)
**Frecuencia**: diario (check rapido), semanal (revision profunda)

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | ModuleMyTeam — avatares, carga equipo | Diario |
| /ipr | Lista auto-scope division + strip contextual | Diario |
| /ipr/[id] | Detalle IPR, asignar responsable, gestionar satelites | Diario |
| /ipr/cartera | Portfolio salud ROJO/AMARILLO/VERDE | Semanal |
| /compromisos | CompromisosTeamView — KPIs + verificar inline | Diario |
| /compromisos/nuevo | Crear compromiso y asignar | Semanal |
| /mi-division | KPIs division + equipo | Diario |
| /problemas | Registrar problemas IPR | Semanal |
| /alertas | Evaluar alertas CRITICO | Diario |
| /reuniones | Convocar reunion de crisis | Mensual |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /problemas/nuevo | Crear problema |
| /reuniones/nueva | Crear reunion |
| /reuniones/[id] | Ver detalle reunion |
| /presupuesto | Consultar presupuesto division |
| /presupuesto/ciclo | Gestionar ciclo presupuestario (canEdit) |
| /convenios | Consultar convenios division |
| /actos | Consultar actos |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /riesgos (2 pags) | Solo DGI + estrategas operan |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES |
| /ipr/nuevo | Solo ADMIN, AR, GOB, ANALISTA |
| /presupuesto/nuevo | Solo ADMIN, AR |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 5. JEFE_DEPARTAMENTO — Supervisor

**Journey**: J15 "Aprobar CDPs y rendiciones"
**Poblacion**: operativa
**Dashboard**: ModuleMyTeam (avatares, carga equipo)
**Scope**: DIVISION (sponsor_division_id)
**Frecuencia**: diario

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | ModuleMyTeam — estado equipo | Diario |
| /aprobaciones | Aprobar rendiciones VISADA_RTF + CDPs | Diario |
| /compromisos | CompromisosTeamView — verificar compromisos | Diario |
| /mi-division | KPIs division + equipo | Diario |
| /presupuesto | Verificar CDPs, emision | Semanal |
| /convenios | Cuotas, Art. 18 verificacion rendiciones | Semanal |
| /ipr | Lista auto-scope division | Semanal |
| /ipr/[id] | Detalle IPR, asignar, gestionar satelites | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /problemas | Registrar problemas |
| /problemas/nuevo | Crear problema |
| /alertas | Ver alertas division |
| /actos | Consultar actos |
| /reuniones | Participar en reuniones |
| /convenios/nuevo | Crear convenio |
| /servicios | Solicitar servicios DGI |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /riesgos (2 pags) | Solo DGI + estrategas |
| /ipr/nuevo | No crea IPRs |
| /ipr/cartera | Solo estrategas / DGI |
| /presupuesto/nuevo | Solo ADMIN, AR |
| /presupuesto/ciclo | Solo ADMIN, AR, GOB (canEdit limite) |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /compromisos/nuevo | Solo ADMIN, AR, JEFE_DIV |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 6. JEFE_UNIDAD — Supervisor

**Journey**: J5 variante a menor escala (unidad vs division)
**Poblacion**: operativa
**Dashboard**: ModuleMyTeam (mismo componente que JEFE_DIV)
**Scope**: DIVISION (comparte tier con JEFE_DIV y JEFE_DEPTO)
**Frecuencia**: diario
**Nota**: Agrupa con JEFE_DIVISION en TEAM_ROLES. Misma ModuleMyTeam. Sin journey diferenciado.

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | ModuleMyTeam — estado equipo | Diario |
| /compromisos | CompromisosListView (ni WorkView ni TeamView) | Diario |
| /mis-compromisos | Mis compromisos personales | Diario |
| /ipr | Listar IPRs de su unidad | Semanal |
| /ipr/[id] | Detalle IPR, crear compromisos | Semanal |
| /problemas | Registrar problemas | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /problemas/nuevo | Crear problema |
| /alertas | Ver alertas |
| /presupuesto | Consultar presupuesto |
| /convenios | Consultar convenios |
| /servicios | Solicitar servicios DGI |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /riesgos (2 pags) | Solo DGI + estrategas |
| /ipr/nuevo | No crea IPRs |
| /ipr/cartera | Solo estrategas / DGI |
| /presupuesto/nuevo, /presupuesto/ciclo | Solo ADMIN, AR |
| /mi-division | Solo JEFE_DIV, JEFE_DEPTO (sidebar) |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /actos (2 pags) | No participa en cadena de actos |
| /convenios/nuevo | No crea convenios |
| /compromisos/nuevo | Solo ADMIN, AR, JEFE_DIV |
| /reuniones (3 pags) | No convoca ni gestiona |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 7. GOBERNADOR — Firmante + Estratega

**Journey**: J11 "Cola de firma" + J12 "Presidir CORE"
**Poblacion**: operativa
**Dashboard**: Centro de Mando (KPIs institucionales + AttentionStrip)
**Scope**: GLOBAL
**Frecuencia**: 2-3 sesiones/semana

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | KPIs institucionales + AttentionStrip firma | Diario |
| /centro-de-mando | 6 KPIs + timeline institucional | Semanal |
| /actos | PendingQueue VISADO — cola de firma | 2-3x/semana |
| /core-sessions | Card proxima sesion | 2-4x/mes |
| /core-sessions/[id] | Presidir sesion, iniciar/finalizar, votacion | 2-4x/mes |
| /ipr | Vista panoramica | Semanal |
| /ipr/[id] | Contexto para firmar (editable) | Semanal |
| /ipr/cartera | Portfolio divisional | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /riesgos | Vista de riesgos institucionales |
| /compromisos | Vista lista generica |
| /convenios | Contexto para firmas |
| /presupuesto | Vista panoramica |
| /presupuesto/ciclo | Parametros ciclo (canEdit) |
| /alertas | Alertas criticas |
| /reuniones | Reuniones de crisis |
| /escalamiento | Visibilidad escalamientos |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /presupuesto/nuevo | Delegado a ADMIN, AR |
| /problemas (2 pags) | Nivel demasiado operativo |
| /compromisos/nuevo | Delegado a jefes |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 8. ADMIN_REGIONAL — Estratega + Firmante

**Journey**: J7 "Panorama institucional"
**Poblacion**: operativa
**Dashboard**: Centro de Mando (KPIs 5 dimensiones + AttentionStrip escalamientos)
**Scope**: GLOBAL
**Frecuencia**: diario (AR), semanal (panorama profundo)

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | KPIs institucionales + AttentionStrip | Diario |
| /centro-de-mando | 6 KPIs + timeline | Diario |
| /ipr | Vista panoramica todas divisiones | Diario |
| /ipr/[id] | Detalle IPR (editable, asignar) | Diario |
| /ipr/cartera | Portfolio divisional | Semanal |
| /actos | PendingQueue VISADO — firmar | Diario |
| /compromisos | Vista lista generica, verificar | Semanal |
| /presupuesto | Gestion presupuestaria (canEdit) | Semanal |
| /presupuesto/nuevo | Crear programa presupuestario | Mensual |
| /riesgos | Riesgos institucionales (write) | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /presupuesto/ciclo | Ciclo presupuestario (canEdit) |
| /convenios | Convenios institucionales |
| /convenios/nuevo | Crear convenio |
| /problemas | Vista de problemas |
| /alertas | Alertas criticas |
| /reuniones | Convocar reuniones |
| /core-sessions | Gestionar sesiones CORE (manager) |
| /escalamiento | Decidir escalamientos nivel 3 |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 9. ADMIN_SISTEMA — Configurador + Estratega

**Journey**: J16 "Dia de mantenimiento" (+ acceso total operativa)
**Poblacion**: operativa
**Dashboard**: Centro de Mando (KPIs + AttentionStrip)
**Scope**: GLOBAL
**Frecuencia**: 5-15 creaciones usuario/mes + ajustes mensuales

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | KPIs institucionales + AttentionStrip | Diario |
| /centro-de-mando | 6 KPIs + timeline | Semanal |
| /admin/usuarios | CRUD usuarios + roles + divisiones | Semanal |
| /admin/usuarios/nuevo | Crear usuario | Semanal |
| /admin/divisiones | Gestionar divisiones | Mensual |
| /admin/umbrales | Ajustar umbrales financieros | Mensual |
| /admin/niveles-sni | Niveles SNI | Mensual |
| /admin/salud-datos | Calidad de datos | Semanal |
| /admin/financing-tracks | Vias de financiamiento | Mensual |
| /admin/slas | Monitoreo SLA (12 indicadores) | Semanal |
| /admin/auditoria | Audit trail txn.event | Semanal |
| /ipr | Vista panoramica | Semanal |
| /ipr/[id] | Detalle IPR (editable) | Semanal |
| /ipr/cartera | Portfolio divisional | Semanal |
| /presupuesto | Gestion presupuestaria (canEdit) | Semanal |
| /presupuesto/nuevo | Crear programa | Mensual |
| /aprobaciones | Acceso por PageGuard | Eventual |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /presupuesto/ciclo | Ciclo presupuestario |
| /compromisos | Vista lista generica |
| /convenios | Convenios (canEdit) |
| /actos | Actos (canCreate, firma) |
| /problemas | Vista de problemas |
| /alertas | Alertas institucionales |
| /reuniones | Gestionar reuniones |
| /core-sessions | Gestionar CORE (manager) |
| /riesgos | Riesgos (write) |
| /servicios | Catalogo servicios |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES |
| Todas las DGI (17 pags) | Poblacion DGI |

**Nota**: ADMIN_SISTEMA tiene la superficie mas amplia justificada por su rol de super-usuario. Las 9 paginas /admin/* son exclusivas de este rol.

---

## 10. CONSEJERO_REGIONAL — Gobernanza CORE

**Journey**: J13 "Votar en CORE"
**Poblacion**: operativa
**Dashboard**: KPIs institucionales (PANORAMA_ROLES)
**Scope**: GLOBAL (lectura)
**Frecuencia**: 2-4 sesiones/mes

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | KPIs institucionales | 2-4x/mes |
| /core-sessions | Card proxima sesion | 2-4x/mes |
| /core-sessions/[id] | Votar (botones SI/NO/ABSTENCION) | 2-4x/mes |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /ipr | Consultar IPRs para votar informado |
| /ipr/[id] | Revisar contexto de IPR en agenda |
| /presupuesto | Consultar cifras presupuestarias |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /riesgos (2 pags) | Solo DGI + estrategas operan |
| /ipr/nuevo | No crea IPRs |
| /ipr/cartera | Solo estrategas / DGI |
| /compromisos (2 pags) | No opera compromisos |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /problemas (2 pags) | No opera problemas |
| /alertas | No opera alertas |
| /presupuesto/nuevo, /presupuesto/ciclo | Solo admin/jefes |
| /convenios (2 pags) | No opera convenios |
| /actos (2 pags) | No firma ni visa |
| /reuniones (3 pags) | No convoca ni gestiona |
| /core-sessions/nueva | Solo managers |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 11. SECRETARIO_EJECUTIVO — Gobernanza CORE

**Journey**: J14 "Preparar CORE"
**Poblacion**: operativa
**Dashboard**: KPIs institucionales (PANORAMA_ROLES)
**Scope**: GLOBAL (lectura)
**Frecuencia**: 2-4 sesiones/mes + preparacion semanal

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | KPIs institucionales | Semanal |
| /core-sessions | Card proxima sesion, guia preparacion | Semanal |
| /core-sessions/nueva | Crear sesion + temas + quorum | 2-4x/mes |
| /core-sessions/[id] | Gestionar sesion, iniciar/finalizar | 2-4x/mes |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /ipr | Consultar IPRs para agenda CORE |
| /ipr/[id] | Revisar contexto IPR |
| /actos | Consultar actos para agenda |
| /presupuesto | Consultar cifras |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /riesgos (2 pags) | Solo DGI + estrategas |
| /ipr/nuevo | No crea IPRs |
| /ipr/cartera | Solo estrategas / DGI |
| /compromisos (2 pags) | No opera compromisos |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /problemas (2 pags) | No opera problemas |
| /alertas | Consulta marginal |
| /presupuesto/nuevo, /presupuesto/ciclo | Solo admin/jefes |
| /convenios (2 pags) | No opera convenios |
| /actos/nuevo | No crea actos |
| /reuniones (3 pags) | Opera via CORE, no reuniones generales |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |
| Todas las DGI (17 pags) | Poblacion DGI |

---

## 12. JEFE_DGI — Coordinador DGI

**Journey**: J10 "Coordinacion semanal"
**Poblacion**: dgi
**Dashboard**: ModuleDgiTeam + DGI KPIs
**Scope**: GLOBAL
**Frecuencia**: diario
**Nota**: Unico rol que usa TODAS las paginas DGI en un ciclo regular.

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | ModuleDgiTeam + DGI KPIs | Diario |
| /centro-de-mando | 6 KPIs + timeline (PageGuard incluye JEFE_DGI) | Diario |
| /cartera | Cartera IPR + health signal | Diario |
| /ipr/cartera | Cartera divisional (sidebar: si) | Semanal |
| /tablero | Kanban iniciativas — standups lunes | Semanal |
| /procesos | Catalogo procesos | Semanal |
| /procesos/progreso | Dashboard progreso | Semanal |
| /coordinacion | AR prep + decisions | Semanal |
| /coordinacion/divisiones | Matriz interacciones | Semanal |
| /escalamiento | Protocolo 4 niveles + FSM | Semanal |
| /servicios | Catalogo servicios, gestionar requests | Semanal |
| /comite-td | Sesiones COMITE-TD | Semanal |
| /calendario | Calendario consolidado 5 fuentes | Semanal |
| /datos | Indicadores + rendiciones | Diario |
| /informes | Reportes semanales | Semanal |
| /riesgos | Riesgos institucionales (write) | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /cuellos-de-botella | Deteccion automatica |
| /alertas | Alertas institucionales |
| /tablero/[id] | DMAIC detalle |
| /procesos/[id] | Detalle proceso |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /compromisos (2 pags) | Operativa — DGI observa, no controla |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES operativa |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO operativa |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /presupuesto (3 pags) | No opera presupuesto |
| /convenios (2 pags) | No opera convenios |
| /actos (2 pags) | No firma ni visa |
| /problemas (2 pags) | No opera problemas |
| /reuniones (3 pags) | Opera via comite-td |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /ipr/nuevo | No crea IPRs |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |

---

## 13. ESP_CONTROL_GESTION — Especialista DGI

**Journey**: J8 "Monitoreo diario"
**Poblacion**: dgi
**Dashboard**: DGI KPIs + cockpit CG
**Scope**: GLOBAL (lectura transversal)
**Frecuencia**: diario

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | DGI KPIs + cockpit CG | Diario |
| /datos | Indicadores VIGENTE, filtros dimension, rendiciones SLA | Diario |
| /cartera | Cartera IPR health | Diario |
| /informes | Documentar en reporte semanal | Semanal |
| /riesgos | Riesgos (write) | Semanal |
| /tablero | Kanban iniciativas | Semanal |
| /cuellos-de-botella | Deteccion automatica | Semanal |
| /alertas | Alertas institucionales | Diario |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /procesos | Catalogo procesos |
| /escalamiento | Visibilidad escalamientos |
| /servicios | Catalogo + requests |
| /tablero/[id] | DMAIC detalle |
| /calendario | Calendario consolidado |
| /ipr/cartera | Cartera divisional |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /coordinacion (2 pags) | Solo JEFE_DGI coordina AR |
| /comite-td | Gestionado por JEFE_DGI |
| /compromisos (2 pags) | Operativa |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES operativa |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /presupuesto (3 pags) | No opera presupuesto |
| /convenios (2 pags) | No opera convenios |
| /actos (2 pags) | No firma ni visa |
| /problemas (2 pags) | No opera problemas |
| /reuniones (3 pags) | Opera via DGI |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /ipr/nuevo | No crea IPRs |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |

---

## 14. ESP_PROCESOS — Especialista DGI

**Journey**: J9 "Mejora de procesos"
**Poblacion**: dgi
**Dashboard**: DGI KPIs + cockpit procesos
**Scope**: GLOBAL (lectura transversal)
**Frecuencia**: diario/semanal

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | DGI KPIs + cockpit procesos | Diario |
| /procesos | Catalogo procesos (canCreate, FSM 6-state) | Diario |
| /procesos/[id] | Detalle: actores, reglas, metricas, dolores, oportunidades | Diario |
| /procesos/progreso | Dashboard progreso | Semanal |
| /tablero | Kanban iniciativas (canEdit) | Diario |
| /tablero/[id] | DMAIC stepper 5 fases | Semanal |
| /cuellos-de-botella | Deteccion automatica (canCreate) | Semanal |
| /cuellos-de-botella/[id] | Investigacion FSM 6-state | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /datos | Indicadores para analisis |
| /cartera | Cartera IPR health |
| /informes | Documentar hallazgos |
| /riesgos | Riesgos (write) |
| /servicios | Catalogo + requests |
| /calendario | Calendario consolidado |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /coordinacion (2 pags) | Solo JEFE_DGI coordina AR |
| /comite-td | Gestionado por JEFE_DGI |
| /escalamiento (2 pags) | Solo JEFE_DGI gestiona |
| /compromisos (2 pags) | Operativa |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES operativa |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /presupuesto (3 pags) | No opera presupuesto |
| /convenios (2 pags) | No opera convenios |
| /actos (2 pags) | No firma ni visa |
| /problemas (2 pags) | No opera problemas |
| /reuniones (3 pags) | Opera via DGI |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /ipr/nuevo | No crea IPRs |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |

---

## 15. ESP_TD — Especialista DGI

**Journey**: Variante de J9 orientada a transformacion digital
**Poblacion**: dgi
**Dashboard**: DGI KPIs (velocity TDE, Ley 21.180 plazos)
**Scope**: GLOBAL (lectura transversal)
**Frecuencia**: diario/semanal
**Foco**: Cuellos de botella, metricas Lean, digitalizacion

### Superficie Esencial

| Pagina | Accion | Frecuencia |
|--------|--------|------------|
| /dashboard | DGI KPIs + cockpit TD (velocity, Ley 21.180) | Diario |
| /cuellos-de-botella | Deteccion automatica 3 queries (canCreate) | Diario |
| /cuellos-de-botella/[id] | Investigacion FSM 6-state (canEdit) | Semanal |
| /tablero | Kanban iniciativas (canEdit) | Semanal |
| /tablero/[id] | DMAIC + lean metrics | Semanal |
| /procesos | Catalogo procesos | Semanal |
| /procesos/[id] | Detalle procesos (canEdit) | Semanal |

### Superficie Secundaria

| Pagina | Motivo |
|--------|--------|
| /datos | Indicadores TDE |
| /cartera | Cartera IPR health |
| /informes | Documentar hallazgos |
| /riesgos | Riesgos (write) |
| /servicios | Catalogo + requests |
| /calendario | Calendario consolidado |

### Superficie Innecesaria

| Pagina | Razon |
|--------|-------|
| /centro-de-mando | Solo AR, GOB, ADMIN, JEFE_DGI |
| /coordinacion (2 pags) | Solo JEFE_DGI coordina AR |
| /comite-td | Gestionado por JEFE_DGI (aunque participa) |
| /escalamiento (2 pags) | Solo JEFE_DGI gestiona |
| /procesos/progreso | Mas relevante para ESP_PROCESOS |
| /compromisos (2 pags) | Operativa |
| /mis-compromisos | Solo PERSONAL_SCOPE_ROLES operativa |
| /mi-division | Solo JEFE_DIV / JEFE_DEPTO |
| /aprobaciones | Solo JEFE_DEPARTAMENTO |
| /presupuesto (3 pags) | No opera presupuesto |
| /convenios (2 pags) | No opera convenios |
| /actos (2 pags) | No firma ni visa |
| /problemas (2 pags) | No opera problemas |
| /reuniones (3 pags) | Opera via DGI |
| /core-sessions (3 pags) | Solo gobernanza CORE |
| /ipr/nuevo | No crea IPRs |
| /admin/* (9 pags) | Solo ADMIN_SISTEMA |

---

## Matriz Rol x Pagina

Leyenda: **E** = Esencial | **S** = Secundaria | **-** = Innecesaria

Abreviaciones de roles:
- AN = ANALISTA, RT = RTF, AJ = ASESOR_JURIDICO
- JD = JEFE_DIVISION, JP = JEFE_DEPARTAMENTO, JU = JEFE_UNIDAD
- GO = GOBERNADOR, AR = ADMIN_REGIONAL, AS = ADMIN_SISTEMA
- CR = CONSEJERO_REGIONAL, SE = SECRETARIO_EJECUTIVO
- JG = JEFE_DGI, CG = ESP_CONTROL_GESTION, PR = ESP_PROCESOS, TD = ESP_TD

| Pagina | AN | RT | AJ | JD | JP | JU | GO | AR | AS | CR | SE | JG | CG | PR | TD |
|--------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| /dashboard | E | E | E | E | E | E | E | E | E | E | E | E | E | E | E |
| /centro-de-mando | - | - | - | - | - | - | E | E | E | - | - | E | - | - | - |
| /riesgos | - | - | - | - | - | - | S | S | S | - | - | E | E | S | S |
| /ipr | E | S | S | E | S | E | E | E | E | S | S | - | - | - | - |
| /ipr/nuevo | E | - | - | - | - | - | S | S | S | - | - | - | - | - | - |
| /ipr/[id] | E | E | E | E | E | E | E | E | E | S | S | - | - | - | - |
| /ipr/cartera | - | - | - | E | - | - | E | E | E | - | - | S | S | - | - |
| /compromisos | E | S | S | E | E | S | S | S | S | - | - | - | - | - | - |
| /compromisos/nuevo | - | - | - | E | - | - | - | - | - | - | - | - | - | - | - |
| /mis-compromisos | E | E | E | - | - | E | - | - | - | - | - | - | - | - | - |
| /problemas | S | - | - | E | S | E | - | S | S | - | - | - | - | - | - |
| /problemas/nuevo | S | - | - | S | S | S | - | - | - | - | - | - | - | - | - |
| /alertas | S | S | - | E | S | S | S | S | S | - | - | S | E | - | - |
| /presupuesto | E | - | - | S | E | S | S | E | E | S | S | - | - | - | - |
| /presupuesto/nuevo | - | - | - | - | - | - | - | E | E | - | - | - | - | - | - |
| /presupuesto/ciclo | - | - | - | S | - | - | S | S | S | - | - | - | - | - | - |
| /convenios | E | S | E | S | E | S | S | S | S | - | - | - | - | - | - |
| /convenios/nuevo | - | - | S | - | S | - | - | S | S | - | - | - | - | - | - |
| /actos | S | - | E | S | S | - | E | E | S | - | S | - | - | - | - |
| /actos/nuevo | S | - | S | - | - | - | - | - | - | - | - | - | - | - | - |
| /reuniones | S | - | - | E | S | - | S | S | S | - | - | - | - | - | - |
| /reuniones/nueva | - | - | - | S | - | - | - | S | S | - | - | - | - | - | - |
| /reuniones/[id] | - | - | - | S | - | - | - | - | - | - | - | - | - | - | - |
| /core-sessions | - | - | - | - | - | - | E | S | S | E | E | - | - | - | - |
| /core-sessions/nueva | - | - | - | - | - | - | - | - | - | - | E | - | - | - | - |
| /core-sessions/[id] | - | - | - | - | - | - | E | - | - | E | E | - | - | - | - |
| /servicios | S | S | S | - | S | S | - | - | S | - | - | E | S | S | S |
| /servicios/solicitar | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| /servicios/[id] | - | - | - | - | - | - | - | - | - | - | - | E | - | - | - |
| /mi-division | - | - | - | E | E | - | - | - | - | - | - | - | - | - | - |
| /aprobaciones | - | - | - | - | E | - | - | - | E | - | - | - | - | - | - |
| /cartera | - | - | - | - | - | - | - | - | - | - | - | E | E | - | - |
| /datos | - | E | - | - | - | - | - | - | - | - | - | E | E | S | S |
| /informes | - | - | - | - | - | - | - | - | - | - | - | E | E | S | S |
| /tablero | - | - | - | - | - | - | - | - | - | - | - | E | E | E | E |
| /tablero/[id] | - | - | - | - | - | - | - | - | - | - | - | S | S | E | E |
| /procesos | - | - | - | - | - | - | - | - | - | - | - | E | S | E | E |
| /procesos/[id] | - | - | - | - | - | - | - | - | - | - | - | S | - | E | E |
| /procesos/progreso | - | - | - | - | - | - | - | - | - | - | - | E | - | E | - |
| /cuellos-de-botella | - | - | - | - | - | - | - | - | - | - | - | S | E | E | E |
| /cuellos-de-botella/[id] | - | - | - | - | - | - | - | - | - | - | - | - | - | S | E |
| /coordinacion | - | - | - | - | - | - | - | - | - | - | - | E | - | - | - |
| /coordinacion/divisiones | - | - | - | - | - | - | - | - | - | - | - | E | - | - | - |
| /escalamiento | - | - | - | - | - | - | S | S | - | - | - | E | S | - | - |
| /escalamiento/[id] | - | - | - | - | - | - | - | - | - | - | - | E | - | - | - |
| /comite-td | - | - | - | - | - | - | - | - | - | - | - | E | - | - | - |
| /calendario | - | - | - | - | - | - | - | - | - | - | - | E | S | S | S |
| /admin/* (9 pags) | - | - | - | - | - | - | - | - | E | - | - | - | - | - | - |

### Conteo por Rol

| Rol | Esenciales | Secundarias | Innecesarias | Sidebar Items |
|-----|:----------:|:-----------:|:------------:|:-------------:|
| ANALISTA | 8 | 7 | 43 | 14 |
| RTF | 4 | 5 | 49 | 14 |
| ASESOR_JURIDICO | 5 | 5 | 48 | 15 |
| JEFE_DIVISION | 10 | 7 | 41 | 17 |
| JEFE_DEPARTAMENTO | 8 | 7 | 43 | 15 |
| JEFE_UNIDAD | 6 | 5 | 47 | 14 |
| GOBERNADOR | 8 | 8 | 42 | 16 |
| ADMIN_REGIONAL | 10 | 8 | 40 | 16 |
| ADMIN_SISTEMA | 17 | 10 | 31 | 25 |
| CONSEJERO_REGIONAL | 3 | 3 | 52 | 13 |
| SECRETARIO_EJECUTIVO | 4 | 4 | 50 | 13 |
| JEFE_DGI | 16 | 4 | 38 | 19 |
| ESP_CONTROL_GESTION | 8 | 6 | 44 | 17 |
| ESP_PROCESOS | 8 | 6 | 44 | 17 |
| ESP_TD | 7 | 6 | 45 | 17 |

---

## Analisis de Poda

### Paginas con <3 roles esenciales (candidatas a consolidar)

| Pagina | Roles Esenciales | Recomendacion |
|--------|-----------------|---------------|
| /aprobaciones | JEFE_DEPARTAMENTO, ADMIN_SISTEMA (2) | Mover a tab en /mi-division o drawer en /dashboard |
| /mi-division | JEFE_DIVISION, JEFE_DEPARTAMENTO (2) | Mover datos a /dashboard ModuleMyTeam |
| /compromisos/nuevo | JEFE_DIVISION (1) | Drawer en /compromisos |
| /presupuesto/nuevo | ADMIN_REGIONAL, ADMIN_SISTEMA (2) | Drawer en /presupuesto |
| /core-sessions/nueva | SECRETARIO_EJECUTIVO (1) | Drawer en /core-sessions |
| /coordinacion/divisiones | JEFE_DGI (1) | Tab en /coordinacion |
| /comite-td | JEFE_DGI (1) | Tab en /coordinacion o /calendario |
| /procesos/progreso | JEFE_DGI, ESP_PROCESOS (2) | Tab en /procesos |
| /cartera | JEFE_DGI, ESP_CONTROL_GESTION (2) | Ya duplica /ipr/cartera — consolidar |
| /servicios/solicitar | Ninguno esencial (transversal) | Drawer en /servicios |
| /servicios/[id] | JEFE_DGI (1) | Drawer en /servicios |

### Paginas /nuevo eliminables (usar drawers)

| Pagina /nuevo | Roles que crean | Estado actual | Recomendacion |
|---------------|----------------|---------------|---------------|
| /compromisos/nuevo | ADMIN, AR, JEFE_DIV | Pagina separada | Drawer en /compromisos |
| /problemas/nuevo | 7 roles | Pagina separada | Drawer en /problemas |
| /convenios/nuevo | 7 roles | Pagina separada | Drawer en /convenios |
| /actos/nuevo | 6 roles | Pagina separada | Drawer en /actos |
| /reuniones/nueva | ADMIN, AR, JEFE_DIV | Pagina separada | Drawer en /reuniones |
| /core-sessions/nueva | 4 managers | Pagina separada | Drawer en /core-sessions |
| /presupuesto/nuevo | ADMIN, AR | Pagina separada | Drawer en /presupuesto |
| /admin/usuarios/nuevo | ADMIN_SISTEMA | Pagina separada | Drawer en /admin/usuarios |
| /ipr/nuevo | 4 roles | Pagina separada | **Mantener** — formulario complejo |

**Ahorro potencial**: 8 paginas eliminables (-14% del total).

### Roles con superficie excesiva vs uso real

| Rol | Sidebar Items | Esenciales | Exceso | Nota |
|-----|:------------:|:---------:|:------:|------|
| CONSEJERO_REGIONAL | 13 | 3 | 10 | 77% del sidebar es innecesario |
| SECRETARIO_EJECUTIVO | 13 | 4 | 9 | 69% del sidebar es innecesario |
| RTF | 14 | 4 | 10 | 71% del sidebar es innecesario |
| ASESOR_JURIDICO | 15 | 5 | 10 | 67% del sidebar es innecesario |
| JEFE_UNIDAD | 14 | 6 | 8 | 57% del sidebar es innecesario |
| ANALISTA | 14 | 8 | 6 | 43% del sidebar es innecesario |
| JEFE_DEPARTAMENTO | 15 | 8 | 7 | 47% del sidebar es innecesario |
| JEFE_DIVISION | 17 | 10 | 7 | 41% del sidebar es innecesario |
| GOBERNADOR | 16 | 8 | 8 | 50% del sidebar es innecesario |
| ADMIN_REGIONAL | 16 | 10 | 6 | 38% del sidebar es innecesario |
| ADMIN_SISTEMA | 25 | 17 | 8 | 32% (justificado por rol super-admin) |
| JEFE_DGI | 19 | 16 | 3 | 16% (justificado — usa todo DGI) |
| ESP_CONTROL_GESTION | 17 | 8 | 9 | 53% del sidebar es innecesario |
| ESP_PROCESOS | 17 | 8 | 9 | 53% del sidebar es innecesario |
| ESP_TD | 17 | 7 | 10 | 59% del sidebar es innecesario |

### Sidebar actual vs sidebar ideal

**Operativa — todos los roles ven**:
- Inicio
- Gestion IPR: IPR, Compromisos, Problemas, Alertas (4 items fijos)
- Finanzas: Presupuesto, Ciclo Ppto, Convenios (3 items fijos)
- Institucional: Actos, Reuniones, Sesiones CORE, Servicios (4 items fijos)

**Problema**: CONSEJERO_REGIONAL ve 13 items del sidebar pero solo usa 3. RTF ve 14 pero solo usa 4.

**DGI — todos los roles DGI ven**:
- Home
- Monitoreo: Centro Mando, Cartera, Cartera Div, Alertas, Rendiciones, Riesgos (6 items)
- Mejora Continua: Tablero, Procesos, Progreso, Cuellos Botella (4 items)
- Coordinacion: Coordinacion, Escalamiento, Servicios, Comite TD, Calendario (5 items)
- Analisis: Datos, Informes (2 items)

**Problema**: ESP_TD ve 17 items pero no necesita Coordinacion ni Centro de Mando.

---

## Recomendaciones de Poda

### R1. Sidebar dinamico por rol (Prioridad ALTA)

Implementar sidebar con 3 niveles de visibilidad por rol:

```
Nivel 1 (siempre visible): Paginas esenciales del rol
Nivel 2 (colapsible "Mas"): Paginas secundarias
Nivel 3 (oculto): Paginas innecesarias — no en sidebar
```

**Impacto estimado**:
- CONSEJERO_REGIONAL: de 13 a 3+3 items (54% reduccion visual)
- RTF: de 14 a 4+5 items (36% reduccion)
- ANALISTA: de 14 a 8+7 items (visualmente organizado)

**Implementacion**: Extender la logica condicional existente en sidebar.tsx (showComando, showCarteraDiv, etc.) con un mapa completo `ROLE_NAV_CONFIG`.

### R2. Consolidacion de paginas /nuevo (Prioridad MEDIA)

Eliminar 8 paginas /nuevo reemplazandolas por drawers en la pagina lista. Mantener solo /ipr/nuevo (formulario complejo).

**Ahorro**: 8 rutas, 8 archivos page.tsx, ~1,600 lineas estimadas.

### R3. Consolidar /mi-division + /aprobaciones en dashboard (Prioridad MEDIA)

- /mi-division ya duplica datos de ModuleMyTeam. Absorber en dashboard.
- /aprobaciones solo la usa JEFE_DEPARTAMENTO. Mover a tab en dashboard o drawer.

**Ahorro**: 2 rutas.

### R4. Admin consolidable con tabs (Prioridad BAJA)

Las 8 paginas /admin/* son usadas solo por ADMIN_SISTEMA. Considerar consolidar en 1 pagina con tabs:
- Tab Usuarios (+ nuevo inline)
- Tab Divisiones
- Tab Configuracion (umbrales + niveles SNI + financing tracks)
- Tab Monitoreo (SLAs + salud datos)
- Tab Auditoria

**Ahorro**: 8 rutas -> 1 ruta con 5 tabs.

### R5. DGI: consolidar /cartera con /ipr/cartera (Prioridad BAJA)

Ambas muestran portfolios de IPR con health signals. Diferenciar por perspectiva (DGI vs Division) usando tabs o filtros en una sola pagina.

### R6. DGI coordinacion: absorber /comite-td y /coordinacion/divisiones (Prioridad BAJA)

- /comite-td -> tab en /coordinacion
- /coordinacion/divisiones -> tab en /coordinacion

**Ahorro**: 2 rutas.

### R7. Servicios: absorber /servicios/solicitar y /servicios/[id] (Prioridad BAJA)

- /servicios/solicitar -> drawer en /servicios
- /servicios/[id] -> drawer en /servicios

**Ahorro**: 2 rutas.

---

## Resumen de Impacto

| Recomendacion | Paginas eliminadas | Complejidad | Prioridad |
|---------------|:-----------------:|:-----------:|:---------:|
| R1. Sidebar dinamico | 0 (reorganiza) | Media | ALTA |
| R2. Drawers /nuevo | 8 | Media | MEDIA |
| R3. Absorber mi-div + aprob | 2 | Baja | MEDIA |
| R4. Admin tabs | 7 | Media | BAJA |
| R5. Cartera unificada | 1 | Baja | BAJA |
| R6. Coordinacion tabs | 2 | Baja | BAJA |
| R7. Servicios drawers | 2 | Baja | BAJA |
| **Total** | **22** | | |

**De 58 rutas a 36 rutas** (-38% de superficie navegable).
**Sidebar items promedio**: de 15.4 a ~8.5 por rol (-45%).

---

## Apendice: Fuentes de Datos

| Fuente | Ubicacion | Datos Extraidos |
|--------|----------|----------------|
| User Journeys v3.2 | `docs/GORE_OS_User_Journeys_v3.0.md` | 17 journeys, 8 arquetipos, acciones por rol |
| Sidebar | `web/src/components/sidebar.tsx` | Nav items por poblacion, flags condicionales |
| Command Center | `web/src/app/(app)/dashboard/components/command-center.tsx` | Modulos por rol |
| Security | `api/app/core/security.py` | OPERATIONAL_ROLES, DGI_ROLES, PERSONAL_SCOPE_ROLES |
| Scope | `api/app/core/scope.py` | GLOBAL/DIVISION/PERSONAL tiers |
| PageGuard | 10 archivos page.tsx | allowedRoles constraints |
| Role checks | 15+ archivos page.tsx | canCreate, canEdit, isFirmante, isJefe |
