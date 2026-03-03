# ADR-003: Advisory Locks for Sequential Code Generators

**Status**: Accepted
**Date**: 2026-03-03
**Deciders**: GORE_OS development team

## Context

Five code generators use a `SELECT MAX(code) + 1` pattern to produce sequential human-readable codes (e.g., OC-0001, PR-0001, AGR-0001, ACT-0001, IPR BIP auto-gen). Under concurrent requests, two transactions can read the same MAX value simultaneously, both compute the same next code, and attempt to INSERT — causing a duplicate key violation or, worse, silently producing duplicate codes if there is no UNIQUE constraint.

## Decision

Wrap every `SELECT MAX(...) + 1` code generation block with `pg_advisory_xact_lock(hashtext('entity_lock_key'))` immediately before the SELECT. The lock is scoped to the transaction and released automatically on commit or rollback.

## Affected generators

| Generator | Lock key |
|-----------|----------|
| `_next_oc_code` (compromisos) | `'oc_code'` |
| `_next_pr_code` (problemas) | `'pr_code'` |
| `_next_agreement_number` (convenios) | `'agreement_number'` |
| `_next_act_number` (actos) | `'act_number'` |
| IPR BIP auto-generation (ipr) | `'ipr_bip'` |

## Consequences

- **Race condition eliminated**: Only one transaction at a time can execute the MAX+1 read for a given entity type.
- **Throughput**: Serialized code generation under concurrency; acceptable since code generation is infrequent.
- **No external state**: Lock lives entirely in PostgreSQL — no Redis or application-level locking needed.
- **Deadlock risk**: Negligible — locks are narrow (single key per entity) and short-lived (released on transaction end).
