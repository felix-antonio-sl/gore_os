# Ejecutor Journey-First — Design Spec

> Fase 1 de la reorganización UX por journey. Cubre el arquetipo Ejecutor (ENCARGADO + ANALISTA), ~60% del uso diario.

## Problema

El sistema está organizado por entidad (/ipr, /compromisos, /convenios). El ENCARGADO debe navegar a listas genéricas, filtrar "lo mío", y buscar su trabajo. El ANALISTA debe descubrir qué satélites completar por prueba y error. Ambos pierden tiempo en orientación antes de actuar.

## Solución

El Dashboard se convierte en el punto de trabajo primario. Cada sub-perfil del Ejecutor aterriza en un módulo dedicado que responde "¿qué tengo que hacer?" sin navegación previa.

## Diseño

### Componente 1: ModuleMyWork (ENCARGADO)

**Reemplaza**: ModuleMyProgress actual (que muestra progress bar + lista plana de items).

**Concepto**: Task list tipo Todoist agrupada por IPR.

**Estructura**:
- Header: "Mi Trabajo" + conteo completadas/total
- Progress bar (completadas / total)
- Secciones colapsables por IPR:
  - Header: codigo_bip + nombre + fase badge + conteo tareas
  - Auto-expandido si tiene items urgentes (VENCIDO o HOY)
  - Auto-colapsado si solo tiene items FUTURO
  - Dentro: items ordenados por urgencia (overdue → today → this_week → future)
- Cada item: dot urgencia + descripción + deadline relativo + click arrow
- Footer: "Al día" (verde) cuando lista vacía
- Link "Ver todos" → /compromisos

**Datos**: endpoint `GET /api/dashboard/action-items` existente (9 fuentes).
Agrupación client-side por campo `ipr_id` de cada ActionItem (ya existe en compromisos, alertas). Items sin ipr_id van en sección "General".

**Interacción**: Click en item → `router.push(item.action_route)` (deep link existente, e.g. `/ipr/{id}?tab=compromisos`).

**Props**:
```typescript
// No props — fetches own data
// Uses existing ActionItemsResponse + groups by ipr_id
```

**Rol gate**: Renderizar cuando `role_code === "ENCARGADO"`.

### Componente 2: ModuleFormulacion (ANALISTA)

**Reemplaza**: ModuleMyProgress cuando el rol es ANALISTA.

**Concepto**: Pipeline de formulación F0→F2 con checklist contextual por fase.

**Estructura**:
- Header: "Mis IPRs en Formulación" + conteo IPRs activas
- Secciones por fase (F0, F1, F2):
  - Label de fase + conteo de IPRs en esa fase
  - Cards por IPR:
    - Header: codigo_bip + nombre + días en fase (color: green ≤30d, amber ≤90d, red >90d)
    - Checklist contextual (varía por fase):
      - F0: Mecanismo, Partes, Territorio, Hitos
      - F1: Items admisibilidad (X/Y verificados)
      - F2: Evaluación asignada, resultado registrado
    - Acción sugerida (texto): "Completar territorio y hitos para avanzar a F1" o "Sin acción requerida (esperando evaluador externo)"
  - Click card → `/ipr/{id}?tab=partes` (o tab más relevante para lo que falta)

**Datos**: Nuevo endpoint `GET /api/ipr/mis-formulaciones`

```typescript
interface FormulacionIPR {
  id: string;
  codigo_bip: string;
  name: string;
  phase: string;           // F0, F1, F2
  days_in_phase: number;
  // Satellite counts
  has_mechanism: boolean;
  partes_count: number;
  territorio_count: number;
  hitos_count: number;
  evaluaciones_count: number;
  // Admissibility (F1)
  admisibilidad_total: number;
  admisibilidad_verified: number;
  // Evaluation (F2)
  eval_assigned: boolean;
  eval_result: string | null;
  // Suggested action
  suggested_action: string;
  suggested_tab: string;    // "partes", "territorio", "admisibilidad", etc.
}

// Response
interface MisFormulacionesResponse {
  total: number;
  by_phase: {
    F0: FormulacionIPR[];
    F1: FormulacionIPR[];
    F2: FormulacionIPR[];
  };
}
```

**Backend**: SQL query que filtra IPRs por `assignee_id = current_user` AND fase F0-F2, con subquery CTE para conteos de satélites (reutilizar patrón del endpoint readiness). `suggested_action` computada server-side basada en qué falta.

**Rol gate**: Renderizar cuando `role_code === "ANALISTA"`.

### Integración en CommandCenter

```typescript
// command-center.tsx — conditional module section
{role === "ENCARGADO" && <ModuleMyWork />}
{role === "ANALISTA" && <ModuleFormulacion />}
// Los demás roles mantienen sus módulos actuales
```

ModuleMyProgress se elimina — reemplazado por los dos nuevos módulos.

### Cambios a AttentionStrip

Para ENCARGADO: AttentionStrip sigue mostrando los items más urgentes (top 5). ModuleMyWork muestra la lista completa agrupada. No hay duplicación porque AttentionStrip es "lo urgente AHORA" y ModuleMyWork es "todo mi trabajo".

Para ANALISTA: AttentionStrip muestra alertas/compromisos urgentes. ModuleFormulacion muestra el pipeline de formulación. Son vistas complementarias.

### Qué NO cambia

- Rutas: 0 nuevas rutas. Dashboard se adapta por rol.
- `/ipr/{id}`: permanece como superficie de trabajo (tabs, transitions, track).
- `/compromisos`, `/problemas`, etc.: permanecen para vista global y supervisores.
- Otros módulos: ModuleMyTeam, ModuleJuridico, ModuleDgiTeam, ModuleKpis — sin cambios.
- Backend action-items: ya tiene las 9 fuentes necesarias.

### Archivos a crear/modificar

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `dashboard/components/module-my-work.tsx` | CREAR | Task list agrupada por IPR |
| `dashboard/components/module-formulacion.tsx` | CREAR | Pipeline F0-F2 con checklists |
| `dashboard/components/command-center.tsx` | MODIFICAR | Routing: ENCARGADO→MyWork, ANALISTA→Formulacion |
| `dashboard/components/module-my-progress.tsx` | ELIMINAR | Reemplazado por los dos nuevos |
| `api/app/routers/ipr.py` | MODIFICAR | Nuevo endpoint `GET /mis-formulaciones` |
| `api/app/schemas/ipr.py` | MODIFICAR | Agregar FormulacionIPR + MisFormulacionesResponse |
| `web/src/types/index.ts` | MODIFICAR | Agregar FormulacionIPR + MisFormulacionesResponse types |

### Estimación

- Backend: 1 nuevo endpoint (~80 líneas, CTE query + computed suggested_action)
- Frontend: 2 componentes nuevos (~120 líneas cada uno), 1 componente eliminado, 1 modificación menor
- Tests: 1 nuevo test module (test_formulacion.py, ~3 tests)
- Total: ~400 líneas nuevas, ~60 eliminadas

## Decisiones de diseño

1. **Task list > Kanban**: ENCARGADO no "mueve" items entre columnas — completa tareas y pasan a done. Kanban es para DGI initiatives.
2. **Agrupado por IPR > por tipo**: Da contexto de proyecto. "Para esta IPR tengo 3 cosas" > "Tengo 5 compromisos sin saber de qué IPR."
3. **Pipeline > task list para ANALISTA**: La formulación es secuencial (F0→F1→F2), no una lista plana. El pipeline muestra progresión.
4. **Click navega > acción inline**: La IPR detail page es donde se trabaja. El dashboard orienta, no reemplaza.
5. **suggested_action server-side**: El backend sabe qué falta (mecanismo, partes, evaluación) — no exponer esa lógica al frontend.
