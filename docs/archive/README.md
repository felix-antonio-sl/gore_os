# Archive

Historical documentation preserved for traceability. **Not operational** — do not use these documents as guides for current development.

## Folders

### plans-implemented/

Planes y diseños ya ejecutados (de `docs/plans/` y `docs/superpowers/`). Diseño superado por el código entregado; conservado solo por trazabilidad. Ver su propio `README.md`.

### audits-closed/

Auditorías y specs cerradas o superadas por CLAUDE.md:
- `GORE_OS_Specification_v1.0.md` — spec funcional original (Ciclo 12), superseded por CLAUDE.md.
- `GORE_OS_Audit_C59.md` — auditoría C59 (2026-03-22); sus 10 hallazgos críticos fueron remediados.
- `GORE_OS_Audit_Detail_v1.0.md` — detalle per-story, superseded por `GORE_OS_Audit_v3.0.md`.
- `GORE_OS_UX_Audit_v2.0.md` — closure record UX (54/55 cerrados).
- `mockups/` — prototipos HTML post-implementación.

### normalization-completed/

Auditorías y planes de la normalización JSONB→relacional, **completada** (100% univocidad categorial, 159 CHECK constraints): `AUDITORIA_CATEGORIAL_v3.0.md`, `AUDITORIA_CATEGORIAL_NORMALIZACION_JSONB.md`, `PLAN_NORMALIZACION_JSONB_v2.0.md`.

### planning-feb2026/

ETL execution reports, backend test suite design, and early UI/UX design from February 2026. These plans were executed and completed; the reports document what was done.

Key artifacts:
- ETL phases 2-2C execution reports
- Backend test suite design (precursor to ADR-005)
- DGI dashboard MVP design

### legacy-model-tel/

Legacy ETL source documentation, normalization v2/v3 reports, and migration docs from the `model-tel` era. These document the extraction, transformation, and loading pipeline for the legacy TEL system data.

Key artifacts:
- ETL source structures and dictionaries (progs, partes, convenios, fril, idis, modificaciones)
- JSONB normalization v2.0/v3.0 reports (completed — 100% categorical univocity now)
- Relational navigator v1.0
- Performance audits v3.0

**Current state**: All normalization work documented here is **completed**. The current system has 98 CHECK constraints and 100% categorical univocity.