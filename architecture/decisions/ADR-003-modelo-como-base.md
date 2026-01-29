# ADR-003: El Modelo de Datos PostgreSQL es la Base de GORE_OS

**Estado:** Aceptado
**Fecha:** 2026-01-29
**Supersede:** ADR-001 (Rechazado)

## Contexto

GORE_OS tiene un modelo de datos PostgreSQL excepcional en `/model/model_goreos`:
- 54 tablas lógicas en 4 schemas semánticos (`meta`, `ref`, `core`, `txn`)
- Category Pattern (Gist 14.0) para vocabularios controlados (75+ schemes)
- Event Sourcing híbrido con particionamiento mensual/trimestral
- 100% derivado de 819 User Stories validadas
- Auditado exhaustivamente (ver `/model/model_goreos/docs/AUDITORIA_CONSOLIDADA_v3_2026-01-27.md`)

Este modelo es el activo más valioso del proyecto y representa años de trabajo de modelado semántico story-first.

## Decisión

**El modelo PostgreSQL `/model/model_goreos` es la base arquitectónica de GORE_OS.**

Todas las aplicaciones (Streamlit tooling, Flask productiva futura) deben:
1. Conectarse al mismo PostgreSQL
2. Usar los mismos modelos SQLAlchemy derivados del DDL
3. Respetar las constraints y triggers definidos
4. Mantener trazabilidad Story → Entidad → Tabla

### Stack de Aplicaciones

- **Streamlit** para tooling interno (existente, mantener)
  - Exploración de datos
  - Herramientas de desarrollo
  - Prototipado rápido

- **Flask + HTMX** para aplicación productiva (construcción incremental)
  - Server-side rendering con Jinja2
  - Interactividad con HTMX 2.0
  - Estilo con Tailwind CSS
  - 6 Blueprints modulares (BP-FIN, BP-EJEC, BP-TERR, BP-NORM, BP-BACK, BP-AUTH)

- **PostgreSQL 16 + PostGIS** compartido (ya existe, es la verdad)
  - Único punto de verdad para datos
  - Geo-capacidades con PostGIS
  - Category Pattern para vocabularios
  - Event Sourcing para auditoría

### Pipeline de Datos

```
/etl/sources/               # Datos legacy (Excel, CSV)
      ↓
/etl/scripts/               # 470 scripts de transformación Python
      ↓
/etl/normalized/            # Datos limpios y validados
      ↓
model/model_goreos (PostgreSQL)   # Modelo canónico
      ↓
apps/flask_app/blueprints/bp_fin/ # Primer módulo productivo
```

El pipeline ETL en `/etl` alimenta el modelo PostgreSQL, que a su vez sirve como base para todas las aplicaciones.

## Consecuencias

### Positivas

- **Modelo probado**: El DDL ha sido auditado y ejecutado exitosamente
- **Trazabilidad story-first**: Cada tabla deriva de historias de usuario validadas
- **Construcción incremental**: Aplicaciones pueden construirse paso a paso sobre base sólida
- **Datos migrados listos**: El ETL ha normalizado datos legacy para alimentar BP-FIN
- **No hay reescritura**: No es necesario rediseñar el modelo de datos

### Negativas

- **Rigidez necesaria**: Aplicaciones deben respetar constraints (esto es deseable)
- **Curva de aprendizaje**: Requiere entender Category Pattern para desarrollo efectivo
- **Mantenimiento PL/pgSQL**: Triggers y funciones deben mantenerse actualizados

## Implementación

### Estructura Propuesta

```
goreos/
├── shared/
│   └── db_models/          # Modelos SQLAlchemy derivados del DDL
│       ├── __init__.py
│       ├── meta.py         # Tablas meta.*
│       ├── ref.py          # Tablas ref.*
│       ├── core.py         # Tablas core.*
│       └── txn.py          # Tablas txn.*
├── apps/
│   ├── streamlit_tooling/  # Apps Streamlit existentes
│   └── flask_app/          # Aplicación Flask (a construir)
│       ├── blueprints/
│       │   ├── bp_fin/     # Módulo Finanzas (primero)
│       │   ├── bp_ejec/
│       │   ├── bp_terr/
│       │   ├── bp_norm/
│       │   ├── bp_back/
│       │   └── bp_auth/
│       ├── static/
│       ├── templates/
│       └── __init__.py     # Application Factory
└── docker-compose.yml      # PostgreSQL + Apps
```

### Pasos de Implementación

1. **Fase 1: Entorno Base** (Semana 1)
   - Crear `docker-compose.yml` con PostgreSQL + PgAdmin
   - Crear scripts de setup y verificación
   - Documentar instalación en `GETTING_STARTED.md`

2. **Fase 2: Modelos Compartidos** (Semana 2)
   - Derivar modelos SQLAlchemy del DDL en `/shared/db_models/`
   - Crear tests de integridad referencial
   - Documentar uso de Category Pattern

3. **Fase 3: Primer Módulo BP-FIN** (Semanas 3-6)
   - Implementar módulo Finanzas según `/docs/technical/especificaciones.md`
   - Usar datos migrados de `/etl/normalized/`
   - Endpoints: presupuesto, modificaciones, estados de pago

4. **Fase 4: Iteración** (Meses 2-6)
   - Completar 6 blueprints
   - Integrar ClaveÚnica
   - Desplegar en producción

## Referencias

- **DDL canónico**: `/model/model_goreos/sql/goreos_ddl.sql`
- **Documentación modelo**: `/model/model_goreos/README.md`
- **ERD completo**: `/model/model_goreos/docs/GOREOS_ERD_v3.md`
- **Auditoría**: `/model/model_goreos/docs/AUDITORIA_CONSOLIDADA_v3_2026-01-27.md`
- **Especificaciones BP-FIN**: `/docs/technical/especificaciones.md`
- **Pipeline ETL**: `/etl/README.md`

## Alternativas Consideradas

### Alternativa 1: Reescribir en TypeScript (ADR-001 - Rechazada)
Propuesta de usar Bun + Hono para construir desde cero.
- **Rechazada**: No alineado con capacidades del equipo ni ecosistema gubernamental.

### Alternativa 2: Solo Streamlit
Usar solo Streamlit para todo.
- **Rechazada**: Streamlit no es adecuado para aplicaciones productivas de misión crítica con autenticación compleja y volumen alto de usuarios.

### Alternativa 3: Modelo híbrido (Adoptada - Esta ADR)
PostgreSQL como base + Streamlit para tooling + Flask para producción.
- **Adoptada**: Aprovecha activos existentes (modelo, ETL) mientras construye aplicación productiva robusta.
