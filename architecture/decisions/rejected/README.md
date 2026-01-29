# Decisiones Rechazadas

Este directorio contiene ADRs de propuestas evaluadas y descartadas.

## ADR-001: Stack TypeScript (Bun + Hono) - RECHAZADO

**Razón**: No alineado con capacidades del equipo ni ecosistema gubernamental.

**Decisión final**: Ver ADR-003 (Python + Flask + PostgreSQL)

El stack TypeScript propuesto (Bun runtime + Hono framework) fue evaluado pero rechazado porque:

1. **Capacidades del Equipo**: El equipo tiene experiencia consolidada en Python y ecosistema Flask
2. **Ecosistema Gubernamental**: Python es estándar de facto en instituciones públicas chilenas
3. **Modelo Existente**: El modelo PostgreSQL en `/model/model_goreos` está diseñado para trabajar con Python/SQLAlchemy
4. **ETL Pipeline**: Los 470 scripts ETL están escritos en Python (Pandas, DuckDB)
5. **Integraciones TDE**: Las integraciones con sistemas nacionales (ClaveÚnica, PISEE, SIGFE) tienen librerías maduras en Python

**Fecha de rechazo**: 2026-01-29

**Alternativa adoptada**: ADR-003 establece PostgreSQL + Python como base arquitectónica
