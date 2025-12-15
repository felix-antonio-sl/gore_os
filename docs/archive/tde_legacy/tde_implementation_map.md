# Mapa de Implementación — TDE Compliance (GORE Ñuble)

## Propósito
Este documento traduce el backlog `tde_backlog.md` a un **mapa de implementación** (sin código), indicando por épico/ticket:

- repos/artefactos a tocar
- componentes típicos a implementar
- dependencias entre tickets
- evidencia/verificación sugerida (consistente con axiomas/ontología)

## Repos involucrados
- **Docs / Producto:** `gore_os/docs`
- **Ontología / Modelo:** `data-gore/ontology`
- **Verificación / scripts:** `data-gore/scripts` (p.ej. `verify_tde_axioms.py`, `verify_functors.py`, `verify_traceability.py`)

---

# 1) Backbone DS10 — Expediente Electrónico

## Ticket: TDE-P0-DS10-01 (Expediente + IUIe)
- **Docs (gore_os):**
  - `docs/user_stories.md` → `AS-009`, `CTD-03`.
  - `docs/tde_backlog.md` → DS10.
- **Modelo (data-gore):**
  - `ontology/.../L_tde_representacion.yaml` → `Expediente_Electronico_TDE`.
  - `ontology/.../L_tde_compliance.yaml` → `AX_DS10_001_EXPEDIENTE_IUIe`.
  - `ontology/.../F_tde_mapping.yaml` → `F_Exp_GORE_TDE.iuie_generation`.
- **Implementación (áreas típicas):**
  - Dominio `Expediente` transversal (IPR/Convenios/Compras/CORE).
  - Generador IUIe (patrón + secuencia) + persistencia.
- **Dependencias:** base para DS8 (`AX_DS8_005` exige `id_expediente ∈ IUIe`).
- **Evidencia/verificación:**
  - Pruebas de unicidad de IUIe + trazabilidad de creación.

## Ticket: TDE-P0-DS10-02 (Índice electrónico)
- **Docs:** `AS-010`.
- **Modelo:** `AX_DS10_002_INDICE_OBLIGATORIO` + `Indice_Electronico`.
- **Implementación:**
  - Servicio/tabla de índice y reglas de consistencia.
- **Dependencias:** DS10-01.

## Ticket: TDE-P0-DS10-03 (Metadatos mínimos)
- **Docs:** parte de `AS-009` y definición de mínimos.
- **Modelo:** `AX_DS10_003_METADATOS_DOCUMENTO`.
- **Implementación:**
  - Schema mínimo + no sobrescritura destructiva.

---

# 2) DS9 — Autenticación

## Tickets: DS9 (tic-006..011)
- **Docs:** `tic-006..tic-011`, `CISO-05`.
- **Modelo:** `AX_DS9_001..005` + `Identidad_Digital.ClaveUnica`.
- **Implementación:**
  - Integración OIDC (state, backend token/userinfo, logout)
  - Custodia secretos + ambientes
  - Auditoría accesos con hora oficial
- **Dependencias:** DS7 (cifrado/logs) refuerza.

---

# 3) DS8 — Notificaciones (vía PISEE)

## Tickets: DS8 (tic-012..018)
- **Docs:** `tic-012..tic-018` + referencias desde `FE-IPR-004`, `AD-IPR-004`, `CR-001`.
- **Modelo:** `AX_DS8_001..005` + `Notificacion_Electronica.constancia.codigo_tx`.
- **Mapping:** `F_Notif_GORE_TDE` (envío canalizado vía nodo PISEE).
- **Implementación:**
  - Resolver DDU (casilla/email/excepción/sin DDU)
  - Envío/estado usando endpoints de plataforma
  - Constancia + regla 3 días hábiles
  - Validación de campos obligatorios (Gestor Códigos, IUIe, CPAT)
- **Dependencias:** DS12 (nodo PISEE), DS10 (IUIe), DS9 (auth).

---

# 4) DS12 — Interoperabilidad

## Tickets: DS12 (tic-019..023)
- **Docs:** `tic-019..tic-023` + CTD `CTD-04..CTD-08`.
- **Modelo:** `AX_DS12_001..006` + `Interoperabilidad_Estado.*`.
- **Implementación:**
  - Nodo interoperabilidad dev/prod
  - Registro en catálogo servicios
  - Registro trazabilidad central por transacción
  - Gestor de acuerdos + gestor de autorizaciones (sensibles)
- **Referencias desde módulos:** `AD-IPR-005`, `PD-PPTO-008`, `UCR-001`, `CONT-01`, `ABS-COM-03`, `S-CTD-MUNI-001`.

---

# 5) DS7 — Seguridad y ciberseguridad

## Tickets: DS7 (tic-024..028)
- **Docs:** `tic-024..tic-028` + CISO `CISO-06..CISO-10`.
- **Modelo:** `AX_DS7_001..006` + `Seguridad_TDE`.
- **Implementación:**
  - Política firmada/acto administrativo
  - CISO designado no externalizable
  - Inventario activos + CIA
  - Protocolo reporte incidentes (CSIRT/ANCI)
  - TLS 1.2+ y cifrado reposo
- **Dependencias:** transversal.

---

# 6) DS11 — Calidad y operación

## Tickets: DS11 (tic-029..032)
- **Docs:** `tic-029..tic-032` + CTD `CTD-09..CTD-12`.
- **Modelo:** `AX_DS11_001..005` + `Calidad_Plataformas.*`.
- **Implementación:**
  - Catálogo plataformas con línea base
  - Plan anual mejora
  - Ejecución ciclo
  - Gate EvalTIC

---

# 7) Datos Personales — RAT + anonimización

## Tickets: PRIV (DPO-05..08)
- **Docs:** `DPO-05..DPO-08`.
- **Modelo:** `L_data_governance.yaml` → `RAT` + `AX_ANONIMIZACION`.
- **Implementación:**
  - Registro RAT (campos mínimos) + versionado
  - Workflow actualización
  - Política/criterios de anonimización previa a analítica/publicación

---

## Verificación recomendada (data-gore/scripts)
- `verify_tde_axioms.py`: validaciones de axiomas DS*
- `verify_functors.py`: preservación/mapeos functoriales
- `verify_traceability.py`: trazabilidad cruzada

