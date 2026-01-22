# Omega System Definition: GORE_OS
**Version**: 3.0.0 (Unified)
**Date**: 2026-01-22
**Status**: APPROVED
**Architect**: Agent Omega

---

## 1. Phase 1: Purpose (Vista Propósito)
> **Identity**: GORE_OS is the nervous system of the Regional Government. It is not just software, but an integrated model of data, processes, and capabilities.

### 1.1 The 4 Atoms (Ontology)
1.  **Story**: The origin of value. No code without a story.
2.  **Entity**: The structure of information (IPR, EEPP, Funcionario).
3.  **Role**: The active agent (Human or AI with human responsibility).
4.  **Process**: The dynamic orchestration of value.

### 1.2 Core Functions
1.  **PLANIFICAR** (Strategy)
2.  **FINANCIAR** (Resource Allocation)
3.  **EJECUTAR** (Implementation)
4.  **COORDINAR** (Alignment)
5.  **NORMAR** (Regulation)

---

## 2. Phase 2: Data (Vista Datos)
> **Principle**: Minimalist & Polymorphic. Centered on the IPR.

```yaml
context: GORE_OS Core Domain

entities:
  # --- INVERSION ASSETS ---
  IPR:
    type: Abstract Entity
    desc: "Intervención Pública Regional. The atomic unit of investment."
    properties:
      - codigo_bip: String (Unique)
      - nombre: String
      - estado: Enum [IDEA, EVALUACION, EJECUCION, CIERRE]
    relations:
      - mechanisms: HasOne Mecanismo
      - financial_state: HasMany EstadoPago

  # --- EXECUTION ARTIFACTS ---
  EstadoPago (EEPP):
    type: Transaction Entity
    desc: "Formal request for payment based on physical/financial progress."
    properties:
      - folio: String
      - monto: Money
      - estado_tramite: Enum [REVISION, OBSERVADO, APROBADO, PAGADO]
    relations:
      - parent_ipr: BelongsTo IPR
      - current_assignee: LinkTo Funcionario

  ResolucionModificatoria:
    type: Admin Entity
    desc: "Administrative act that alters the budget or legal timeframe."
    properties:
      - tipo: Enum [ITEMIZACION, PLAZO, SUPLEMENTO]
      - requires_cgr: Boolean
    relations:
      - target_ipr: BelongsTo IPR

  # --- STRUCTURE & ACTORS ---
  Funcionario:
    type: Actor Entity
    desc: "Human agent responsible for tasks."
    properties:
      - run: String
      - role: Enum [ANALISTA, JEFE, VISADOR]
  
  Unidad:
    type: Structural Entity
    instances: [DIPIR, DAF, JURIDICA]
```

---

## 3. Phase 3: Process (Vista Proceso)
> **Focus**: The critical path of Financial Execution (DIPIR).

```yaml
processes:
  PAYMENT_CYCLE (Ciclo de Pago):
    owner: DIPIR + DAF
    trigger: "Ingreso EEPP por Oficina de Partes"
    happy_path:
      1. S_INGRESO: Reception & Digitization.
      2. S_REV_TECNICA: Analista Inv verifies technical compliancy.
      3. S_REV_TERRENO: Validation of physical works (if applicable).
      4. S_APROBACION: Jefe Inv approves technical execution.
      5. S_FINANZAS: Analista Ppto emits CDP (Budget Availability).
      6. S_VISACION: Jefe DIPIR signs off.
      7. S_TESORERIA: DAF executes payment.
    exceptions:
      - OBSERVACION: Returns to Technical Unit -> Stops Clock.

  AMENDMENT_CYCLE (Modificación Presupuestaria):
    owner: DIPIR + JURIDICA + GORE
    trigger: "Need for budget/time change"
    critical_path:
      1. Availability Check (Analista Ppto).
      2. Circular Visation (5 signatures: Ppto->Legal->Dipir->Jur->Admin).
      3. Toma de Razón (CGR) [If > 5000 UTM].
      4. Activation (Resolution becomes binding).
```

---

## 4. Phase 4: Coherence Matrix (Trazabilidad)
> Verification that the model is consistent and complete.

| Purpose Requirement | Data Entity Support         | Process Support             | Status    |
| :------------------ | :-------------------------- | :-------------------------- | :-------- |
| **"Financiar"**     | `CDP`, `BudgetAccount`      | `PAYMENT_CYCLE` (Step 5)    | ✅ Covered |
| **"Ejecutar"**      | `IPR`, `Convenio`           | `PAYMENT_CYCLE` (Steps 2-3) | ✅ Covered |
| **"Normar"**        | `ResolucionModificatoria`   | `AMENDMENT_CYCLE`           | ✅ Covered |
| **"Human-in-Loop"** | `Funcionario`               | Assigned Roles in all Tasks | ✅ Covered |
| **"Story-First"**   | All entities map to Stories | N/A                         | ✅ Covered |

### 4.1 Detected Gaps & Recommendations
1.  **DIPIR Bottleneck**: The *Amendment Cycle* has a high friction point in the "Circular Visation".
    *   *Recommendation*: Implement "Fast-Track" for minor amendments (< 100 UTM) automating the first 2 signatures.
2.  **Orphaned EEPPs**: *EstadoPago* objects can get stuck in `S_OBSERVADO`.
    *   *Recommendation*: Implement an automated "Re-Ingreso Reminder" agent.

---
**End of Definition**
