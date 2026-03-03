# ADR-001: Meta Schema Status and Retention

**Date**: 2026-03-03
**Status**: Accepted

## Context

The `meta` schema contains 5 tables defined in the DDL: `meta.role`, `meta.process`,
`meta.entity`, `meta.story`, and `meta.story_entity`. These were designed as ontological
atoms to support process traceability and institutional knowledge mapping.

## Decision

### Active table: `meta.role`

`meta.role` is **ACTIVE** and must be retained. It is referenced as a FK from
`core.administrative_act.signer_id`, which records the institutional role that signs
each administrative act (DECRETO, RESOLUCION, DECRETO_ALCALDICIO).

### Dormant tables: `meta.process`, `meta.entity`, `meta.story`, `meta.story_entity`

These four tables are **DORMANT**: they are populated with seed data (ontological mappings
from `goreos_ddl.sql` lines 21-37 and `model/GLOSARIO.yml`) but are not referenced by
any application router, query, or Pydantic schema.

They were created to support future traceability features (audit trail by process, entity
classification for DGI indicators). No application code reads from or writes to them
at runtime.

## Consequences

- All 5 `meta.*` tables are **retained** as-is. Dropping dormant tables risks losing
  ontological seed data and complicates future traceability features.
- A future cleanup cycle may drop `meta.process`, `meta.entity`, `meta.story`, and
  `meta.story_entity` if the traceability features are formally descoped.
- Any new feature that needs process/entity traceability SHOULD reference these tables
  rather than defining new ones.
