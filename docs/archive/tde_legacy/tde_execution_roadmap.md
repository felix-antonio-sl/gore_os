# Roadmap de Ejecución — Cumplimiento TDE (P0/P1)

## Propósito
Secuenciar la ejecución de cumplimiento TDE en fases **implementables**, con:

- dependencias explícitas
- gates verificables (checkpoints)
- trazabilidad a `user_stories.md`, `tde_backlog.md`, ontología y scripts de verificación

## Convenciones
- **Gate**: condición “no avanzar si no está cumplida”.
- **Evidencia**: qué debe existir (doc/registro/salida de verificador) para cerrar el gate.

---

# Fase 0 — Preparación (P0.0)

## Gate 0.1 — Base documental y modelo
- **Evidencia**
  - `gore_os/docs/tde_backlog.md` actualizado.
  - `gore_os/docs/tde_implementation_map.md` presente.
  - Ontología TDE: `L_tde_representacion.yaml`, `L_tde_compliance.yaml`, `F_tde_mapping.yaml` sin inconsistencias semánticas conocidas.

---

# Fase 1 — Backbone DS10 (P0.1)

## Objetivo
Habilitar el **Expediente Electrónico** como estructura transversal (IUIe + índice + metadatos + trazabilidad), que es dependencia directa de DS8 y componente central de DS4.

## Trabajo
- **Historias**: `AS-009`, `AS-010`, `AS-011`, `CTD-03`.
- **Axiomas**: `AX_DS10_001..006` + `AX_DS4_001`.

## Gate 1.1 — IUIe
- **Evidencia**
  - Generación/persistencia de IUIe definida y usable transversalmente.
  - Verificación: `AX_DS10_001_EXPEDIENTE_IUIe` (conceptual + pruebas).

## Gate 1.2 — Índice + metadatos
- **Evidencia**
  - Índice electrónico definido (mínimos) y metadatos mínimos DS10 (nombres consistentes).
  - Verificación: `AX_DS10_002`, `AX_DS10_003`.

## Gate 1.3 — Trazabilidad
- **Evidencia**
  - Eventos registrables definidos (creación/incorporación/modificación/eliminación/acceso/autorización_poderes).
  - Verificación: `AX_DS10_004`.

---

# Fase 2 — Identidad DS9 (P0.2)

## Objetivo
Autenticación oficial y trazable (ClaveÚnica / Clave Tributaria), prerequisito de exposición segura y de notificaciones.

## Trabajo
- **Historias**: `tic-006..tic-011`, `CISO-05`.
- **Axiomas**: `AX_DS9_001..005`.

## Gate 2.1 — Ciudadanía por ClaveÚnica
- **Evidencia**
  - Flujo OIDC documentado e integrado.
  - Prohibición de auth propia para ciudadanía.
  - Verificación: `AX_DS9_001`, `AX_DS9_003`, `AX_DS9_004`.

## Gate 2.2 — Auditoría accesos
- **Evidencia**
  - Registro de accesos con hora oficial.
  - Verificación: `AX_DS9_005`.

---

# Fase 3 — Seguridad DS7 (P0.3)

## Objetivo
Asegurar que la plataforma pueda operar e interoperar con garantías mínimas.

## Trabajo
- **Historias**: `tic-024..tic-028`, `CISO-06..CISO-10`.
- **Axiomas**: `AX_DS7_001..006`.

## Gate 3.1 — Gobernanza seguridad
- **Evidencia**
  - Política aprobada y CISO designado (no externalizable).
  - Verificación: `AX_DS7_001`, `AX_DS7_002`.

## Gate 3.2 — CIA + cifrado
- **Evidencia**
  - Activos clasificados CIA.
  - TLS 1.2+ y cifrado reposo datos sensibles.
  - Verificación: `AX_DS7_003`, `AX_DS7_006`.

## Gate 3.3 — Incidentes
- **Evidencia**
  - Proceso operativo y trazable de reporte de incidentes.
  - Verificación: `AX_DS7_004`.

---

# Fase 4 — Interoperabilidad DS12 (P0.4)

## Objetivo
Nodo + catálogo + trazabilidad central + acuerdos/consentimiento. Habilita DS8 vía PISEE.

## Trabajo
- **Historias**: `tic-019..tic-023`, `CTD-04..CTD-08`.
- **Axiomas**: `AX_DS12_001..006`.

## Gate 4.1 — Nodo
- **Evidencia**
  - Nodo dev/prod y roles responsables.
  - Verificación: `AX_DS12_001`.

## Gate 4.2 — Catálogo + trazabilidad
- **Evidencia**
  - Registro en catálogo de servicios.
  - Registro de trazabilidad central por transacción.
  - Verificación: `AX_DS12_002`, `AX_DS12_003`.

## Gate 4.3 — Acuerdos + consentimiento
- **Evidencia**
  - Acuerdo previo para consumo.
  - Autorización titular para datos sensibles.
  - Verificación: `AX_DS12_005`, `AX_DS12_004`.

---

# Fase 5 — Notificaciones DS8 vía PISEE (P0.5)

## Objetivo
Notificar por canal oficial, con DDU y constancia, sobre procedimientos con expediente (IUIe) y código CPAT.

## Trabajo
- **Historias**: `tic-012..tic-018`.
- **Axiomas**: `AX_DS8_001..005`.

## Gate 5.1 — Canal oficial + DDU
- **Evidencia**
  - Resolución DDU y canalización oficial.
  - Verificación: `AX_DS8_001`, `AX_DS8_002`.

## Gate 5.2 — Constancia + plazo 3 días hábiles
- **Evidencia**
  - Constancia (`codigo_tx`, timestamps) y regla de practicada.
  - Verificación: `AX_DS8_003`, `AX_DS8_004`.

## Gate 5.3 — Datos obligatorios
- **Evidencia**
  - Notificación incluye: código OAE, IUIe, CPAT.
  - Verificación: `AX_DS8_005`.

---

# Fase 6 — Calidad DS11 (P1)

## Objetivo
Operación sostenible: catálogo de plataformas, ciclo de calidad, plan anual, gate EvalTIC.

## Trabajo
- **Historias**: `tic-029..tic-032`, `CTD-09..CTD-12`, `tic-005` (agregación).
- **Axiomas**: `AX_DS11_001..005`.

## Gate 6.1 — Catálogo + línea base
- **Evidencia**
  - Catálogo con baseline.
  - Verificación: `AX_DS11_003`.

## Gate 6.2 — Plan y ciclo
- **Evidencia**
  - Plan anual y ejecución ciclo.
  - Verificación: `AX_DS11_002`, `AX_DS11_004`.

## Gate 6.3 — Gate presupuestario (EvalTIC)
- **Evidencia**
  - Proyectos con presupuesto pasan EvalTIC.
  - Verificación: `AX_DS11_005`.

---

# Fase 7 — Datos Personales (P1)

## Objetivo
RAT operativo y anonimización para analítica/publicación.

## Trabajo
- **Historias**: `DPO-05..DPO-08`.
- **Modelo**: `L_data_governance.yaml` → `RAT`, `AX_ANONIMIZACION`, `INV_DATA_02`.

## Gate 7.1 — RAT mínimo + versionado
- **Evidencia**
  - RAT con campos mínimos y registro de versiones.

## Gate 7.2 — Anonimización
- **Evidencia**
  - Política/criterios y proceso de anonimización previo a publicación/analítica.

