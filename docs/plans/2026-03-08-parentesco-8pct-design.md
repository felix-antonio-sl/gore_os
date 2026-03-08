# HΩ-02 Parentesco 8% — Design Document

**Date**: 2026-03-08
**Status**: Approved
**HΩ Finding**: HΩ-02 (último HΩ completamente pendiente)

## Goal

Digitalizar la declaración jurada de parentesco para mecanismo SUBV8 (Subvención 8% FNDR). Cada evaluador o representante legal debe declarar si tiene parentesco con autoridades GORE. Un gate en F1→F2 bloquea si faltan declaraciones o si alguna declara conflicto.

## Regulatory Basis

- **Omega v2.6.0 FRPD/SUBV8**: Inhabilidad hasta 4° consanguinidad / 3° afinidad con Gobernador, CORE o directivos GORE
- **PPR Transferencia** (futuro, fuera de alcance): 3° consanguinidad / 2° afinidad

## Architecture

Declaración jurada (sworn declaration) — cada persona declara si tiene o no conflicto. No se modela el grafo de parentesco completo (requeriría integración con Registro Civil).

## Data Model

### New table: `core.kinship_declaration`

```sql
CREATE TABLE core.kinship_declaration (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id          UUID NOT NULL REFERENCES core.ipr(id),
    person_id       UUID NOT NULL REFERENCES core.person(id),
    declaration_type VARCHAR(32) NOT NULL,  -- EVALUADOR | REPRESENTANTE_LEGAL | PERSONAL_CONTRATADO
    declares_no_conflict BOOLEAN NOT NULL,
    related_authority_id UUID REFERENCES core.person(id),
    relationship_type VARCHAR(16),          -- CONSANGUINIDAD | AFINIDAD
    relationship_degree INT,                -- 1-4
    declared_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    validated_by_id UUID REFERENCES core."user"(id),
    validated_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_kinship_decl UNIQUE (ipr_id, person_id, declaration_type)
);
```

### New ref.category scheme: `kinship_declaration_type`

3 codes: EVALUADOR, REPRESENTANTE_LEGAL, PERSONAL_CONTRATADO

### Authority roles (5)

GOBERNADOR, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO, ADMIN_REGIONAL, JEFE_DIVISION

## API Endpoints (4)

| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| GET | `/api/ipr/{id}/parentesco` | List declarations | Any authenticated |
| POST | `/api/ipr/{id}/parentesco` | Create declaration | ADMIN_SISTEMA, ADMIN_REGIONAL |
| PATCH | `/api/ipr/{id}/parentesco/{decl_id}` | Validate declaration | ADMIN_SISTEMA |
| DELETE | `/api/ipr/{id}/parentesco/{decl_id}` | Delete declaration | ADMIN_SISTEMA |

## Gate Function

`_check_kinship_declarations()` in `ipr.py`:
- **Phase**: F1→F2 (SUBV8 only)
- **Blocking**: Yes
- Checks: at least 1 EVALUADOR declaration exists, all declare no conflict

## Frontend

New tab "Parentesco" (#12) in IPR detail, visible only for SUBV8 track IPRs. ComboboxAsync for person search by RUT/name.

## Decisions

1. **Scope**: SUBV8 only (PPR deferred)
2. **Model**: Sworn declaration, not kinship graph
3. **Declarant**: Must exist in `core.person` (FK, not inline text)
4. **Authorities**: 5 roles (no JEFE_DEPARTAMENTO)
5. **Gate phase**: F1→F2 bloqueante
6. **Declaration type**: VARCHAR, not FK to ref.category (only 3 values, rarely changes)
