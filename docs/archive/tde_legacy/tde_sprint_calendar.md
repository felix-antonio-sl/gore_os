# Calendario de Sprints (2 semanas) — Ejecución Cumplimiento TDE

## Propósito
Aterrizar `tde_execution_roadmap.md` en un calendario de ejecución por sprints (2 semanas), con entregables claros y gates verificables.

## Supuestos
- Cada sprint tiene 2 semanas.
- Alcance: planificación y entregables por gate (la implementación real puede variar según capacidad del equipo).
- Dependencias: DS10 → DS9 → DS7 → DS12 → DS8 → DS11 → Privacidad.

---

# Sprint 0 (Semana 0-2) — Preparación y alineamiento base

## Objetivo
Dejar el baseline listo para comenzar ejecución técnica sin ambigüedades.

## Entregables
- `gore_os/docs/tde_backlog.md` validado y congelado para P0.
- `gore_os/docs/tde_implementation_map.md` validado.
- `gore_os/docs/tde_execution_roadmap.md` validado.
- Matriz de dependencias confirmada (DS8 vía PISEE).

## Gate (Go/No-Go)
- **Gate 0.1**: Base documental y modelo lista.

---

# Sprint 1 (Semana 2-4) — DS10 Gate 1.1 (IUIe)

## Objetivo
Implementar el identificador IUIe y su contrato transversal.

## Historias foco
- `AS-009`, `CTD-03`.

## Entregables
- Diseño de IUIe (patrón, colisiones, secuencia) y contrato de persistencia.
- Especificación de endpoints/servicios internos que exponen IUIe.
- Evidencia: casos de prueba/validación de unicidad.

## Gates
- **Gate 1.1**: IUIe implementado y verificable.

---

# Sprint 2 (Semana 4-6) — DS10 Gate 1.2/1.3 (Índice + Metadatos + Trazabilidad)

## Objetivo
Cerrar el backbone de expediente para habilitar DS8.

## Historias foco
- `AS-010`, `AS-011`.

## Entregables
- Diseño e implementación del índice electrónico.
- Metadatos mínimos DS10 (nombres consistentes con ontología).
- Registro de trazabilidad (eventos mínimos y actor/timestamp).

## Gates
- **Gate 1.2**: Índice + metadatos mínimos.
- **Gate 1.3**: Trazabilidad de acciones.

---

# Sprint 3 (Semana 6-8) — DS9 (Autenticación) Gates 2.1/2.2

## Objetivo
Habilitar autenticación oficial (ClaveÚnica/CT) y auditoría.

## Historias foco
- `tic-006..tic-011`, `CISO-05`.

## Entregables
- Integración OIDC (flujo completo) + logout.
- Gestión de credenciales por ambiente.
- Prohibición de auth propia ciudadanía.
- Auditoría accesos con hora oficial.

## Gates
- **Gate 2.1**: Ciudadanía por ClaveÚnica + prohibición de auth propia.
- **Gate 2.2**: Auditoría accesos.

---

# Sprint 4 (Semana 8-10) — DS7 (Seguridad) Gates 3.1/3.2

## Objetivo
Asegurar gobernanza de seguridad y controles mínimos para operar/interoperar.

## Historias foco
- `tic-024..tic-028`, `CISO-06..CISO-10`.

## Entregables
- Política de seguridad aprobada (acto administrativo) + CISO designado.
- Inventario de activos + clasificación CIA.
- TLS 1.2+ y cifrado en reposo para sensibles.

## Gates
- **Gate 3.1**: Gobernanza (política + CISO).
- **Gate 3.2**: CIA + cifrado.

---

# Sprint 5 (Semana 10-12) — DS7 Gate 3.3 + DS12 Gate 4.1 (Nodo)

## Objetivo
Cerrar respuesta a incidentes y habilitar nodo interoperabilidad.

## Historias foco
- `tic-027` (incidentes), `tic-019` (nodo), CTD `CTD-04`.

## Entregables
- Proceso operativo de incidentes y reportabilidad.
- Nodo PISEE dev/prod habilitado (mínimo: consumidor) con roles definidos.

## Gates
- **Gate 3.3**: Incidentes.
- **Gate 4.1**: Nodo.

---

# Sprint 6 (Semana 12-14) — DS12 Gates 4.2/4.3

## Objetivo
Completar interoperabilidad: catálogo, trazabilidad central, acuerdos, consentimiento.

## Historias foco
- `tic-020..tic-023`, `CTD-05..CTD-08`.

## Entregables
- Registro de servicios en catálogo.
- Registro de trazabilidad central por transacción.
- Gestión de acuerdos previos.
- Gestión de consentimiento para sensibles.

## Gates
- **Gate 4.2**: Catálogo + trazabilidad.
- **Gate 4.3**: Acuerdos + consentimiento.

---

# Sprint 7 (Semana 14-16) — DS8 vía PISEE Gates 5.1/5.2

## Objetivo
Habilitar notificaciones oficiales con DDU y constancia.

## Historias foco
- `tic-012..tic-017`.

## Entregables
- Resolución DDU y canal.
- Envío y consulta de estado vía nodo.
- Constancia y regla 3 días hábiles.

## Gates
- **Gate 5.1**: Canal oficial + DDU.
- **Gate 5.2**: Constancia + plazo.

---

# Sprint 8 (Semana 16-18) — DS8 Gate 5.3 + DS11 Gate 6.1

## Objetivo
Cerrar datos obligatorios de notificación y levantar catálogo de plataformas.

## Historias foco
- `tic-018` + `tic-029`.

## Entregables
- Validación de campos obligatorios DS8 (Gestor Códigos, IUIe, CPAT).
- Catálogo de plataformas con línea base.

## Gates
- **Gate 5.3**: Datos obligatorios DS8.
- **Gate 6.1**: Catálogo + baseline.

---

# Sprint 9 (Semana 18-20) — DS11 Gates 6.2/6.3

## Objetivo
Operación sostenible: plan anual, ciclo, gate presupuestario.

## Historias foco
- `tic-030..tic-032`, `CTD-10..CTD-12`.

## Entregables
- Plan anual de mejora.
- Evidencia de ejecución del ciclo.
- Gate EvalTIC para iniciativas con presupuesto.

## Gates
- **Gate 6.2**: Plan + ciclo.
- **Gate 6.3**: EvalTIC.

---

# Sprint 10 (Semana 20-22) — Privacidad (RAT + anonimización) Gates 7.1/7.2

## Objetivo
Trazabilidad de tratamientos y protección para analítica/publicación.

## Historias foco
- `DPO-05..DPO-08`.

## Entregables
- RAT mínimo con versionado.
- Proceso/política de anonimización/seudonimización.

## Gates
- **Gate 7.1**: RAT mínimo + versionado.
- **Gate 7.2**: Anonimización.
