# Plan comprometible — Ejecución TDE (según capacidad)

## Propósito
Entregar 3 escenarios comprometibles (sprints de 2 semanas) para ejecutar el roadmap TDE, ajustado a capacidad de equipo.

**Entrada:** `tde_execution_roadmap.md`, `tde_sprint_calendar.md`.

---

# Escenario 1 — 1 Squad (secuencial, menor riesgo de coordinación)

## Horizonte recomendado
- **6 sprints (12 semanas)** para cerrar P0 operativo (sin DS11/Privacidad completa).

## Sprint a sprint
- **Sprint 1:** DS10 Gate 1.1 (IUIe)
- **Sprint 2:** DS10 Gate 1.2/1.3 (Índice + Metadatos + Trazabilidad)
- **Sprint 3:** DS9 Gate 2.1/2.2 (ClaveÚnica + auditoría)
- **Sprint 4:** DS7 Gate 3.1/3.2 (gobernanza + CIA + cifrado)
- **Sprint 5:** DS12 Gate 4.1/4.2 (Nodo + Catálogo + Trazabilidad central)
- **Sprint 6:** DS12 Gate 4.3 + DS8 Gate 5.1/5.2 (acuerdos/consentimiento + DDU + constancia)

## Queda fuera (post 12 semanas)
- DS8 Gate 5.3 (datos obligatorios completos) si no entra
- DS11 (calidad/operación) completo
- Privacidad (RAT + anonimización) completo

## Riesgo/observación
- Riesgo: DS8 se retrasa si DS12 Gate 4.3 se demora por acuerdos/consentimiento.

---

# Escenario 2 — 2 Squads (paralelización controlada)

## Horizonte recomendado
- **4 sprints (8 semanas)** para cerrar P0 operativo mínimo.

## División sugerida
- **Squad A (Backbone):** DS10 → DS9
- **Squad B (Plataforma/Seguridad/Interop):** DS7 → DS12

## Sprint a sprint
- **Sprint 1:**
  - A: DS10 Gate 1.1 (IUIe)
  - B: DS7 Gate 3.1 (política + CISO)
- **Sprint 2:**
  - A: DS10 Gate 1.2/1.3
  - B: DS7 Gate 3.2/3.3
- **Sprint 3:**
  - A: DS9 Gate 2.1/2.2
  - B: DS12 Gate 4.1/4.2
- **Sprint 4:**
  - A+B: DS12 Gate 4.3 + DS8 Gate 5.1/5.2

## Queda fuera (post 8 semanas)
- DS8 Gate 5.3
- DS11 completo
- Privacidad completo

## Riesgo/observación
- Riesgo: coordinación de integración DS8 depende de que DS10 y DS12 lleguen “on time”.

---

# Escenario 3 — Fast-track (3 sprints, enfoque demostración)

## Horizonte recomendado
- **3 sprints (6 semanas)** para una demo funcional con riesgos aceptados.

## Sprint a sprint
- **Sprint 1:** DS10 Gate 1.1 (IUIe) + DS7 Gate 3.1 (política + CISO) (mínimo documental + responsable)
- **Sprint 2:** DS12 Gate 4.1 (Nodo dev) + DS9 Gate 2.1 (ClaveÚnica) (mínimo viable)
- **Sprint 3:** DS8 Gate 5.1/5.2 (DDU + constancia) en un caso acotado (p.ej. IPR o CORE)

## Riesgo/observación
- Alta deuda técnica: auditoría/timestamps, trazabilidad central completa, acuerdos/consentimiento, DS11.

---

# Decisión requerida para congelar plan
Indica:
- **Escenario:** 1 / 2 / 3
- **Capacidad real:** nº personas (y perfiles) por squad
- **Fecha de inicio:** (semana calendario)
- **Caso piloto para DS8:** IPR / CORE / otro
