# GORE_OS - Sistema Operativo Institucional del Gobierno Regional de Ñuble

> **Versión 3.0** | **Filosofía: Story-First & Radical Minimalism**

---

## ¿Por dónde empezar?

### Para Nuevos Desarrolladores

1. **[README.md](README.md)** - Introducción general al proyecto
2. **[MANIFESTO.md](MANIFESTO.md)** - Filosofía Story-First y las 5 Funciones Motoras
3. **[CLAUDE.md](CLAUDE.md)** - Guía para Claude Code (stack, arquitectura, comandos)
4. **[architecture/stack.md](architecture/stack.md)** - Stack tecnológico detallado
5. **[architecture/standards/stack-tecnico-propuesto.md](architecture/standards/stack-tecnico-propuesto.md)** - Stack completo con ejemplos de código
6. **[architecture/standards/antipatrones-y-deuda-tecnica.md](architecture/standards/antipatrones-y-deuda-tecnica.md)** - Errores a evitar y mejores prácticas

### Para Arquitectos y Diseñadores de Datos

1. **[model/model_goreos/README.md](model/model_goreos/README.md)** - Modelo de datos v3.0 ejecutable
2. **[docs/technical/planclaude.md](docs/technical/planclaude.md)** - Plan maestro KODA-CARTOGRAPHER
3. **[architecture/Omega_GORE_OS_Definition_v3.0.0.md](architecture/Omega_GORE_OS_Definition_v3.0.0.md)** - Definición omega del sistema
4. **[model/GLOSARIO.yml](model/GLOSARIO.yml)** - Glosario autoritativo de términos

### Para Product Owners y Analistas

1. **[model/stories/](model/stories/)** - 819+ historias de usuario validadas (fuente de verdad)
2. **[docs/technical/gestion.md](docs/technical/gestion.md)** - Modelo de datos operativo
3. **[docs/technical/especificaciones.md](docs/technical/especificaciones.md)** - Requisitos funcionales y técnicos

### Para Ingenieros de Datos / ETL

1. **[etl/README.md](etl/README.md)** - Pipeline ETL para migración de datos legacy
2. **[etl/sources/](etl/sources/)** - Datos fuente (convenios, FRIL, IDIS)
3. **[etl/scripts/](etl/scripts/)** - ~30 scripts de transformación Python

---

## Estructura del Repositorio

```
goreos/
├── architecture/          # Documentación C1-C4, ADRs, design system
│   ├── stack.md           # Stack tecnológico oficial
│   ├── diagrams/          # Diagramas Mermaid y visualizaciones
│   └── standards/         # Estándares técnicos y guías de calidad
├── model/                 # ⭐ EL CORAZÓN - Modelo semántico del dominio
│   ├── stories/           # 819+ historias YAML (fuente de verdad)
│   ├── entities/          # 139+ entidades del dominio
│   ├── model_goreos/      # Modelo ejecutable v3.0 (DDL PostgreSQL)
│   └── GLOSARIO.yml       # Terminología autoritativa
├── etl/                   # Pipeline ETL para migración legacy
├── db/                    # Configuración base de datos (ver db/README.md)
├── docs/                  # Documentación técnica consolidada
│   ├── technical/         # Especificaciones, planes maestros
│   └── archive/           # Análisis históricos
└── catalog/               # Catálogo federado KODA
```

---

## Stack Tecnológico (Resumen)

| Capa | Tecnología |
|------|------------|
| **Backend** | Python 3.11+, Flask 3.0.3, SQLAlchemy 2.0.30 |
| **Frontend** | Jinja2 (SSR), HTMX 2.0.0, Alpine.js 3.x, Tailwind CSS 3.4.0 |
| **Base de Datos** | PostgreSQL 16 + PostGIS |
| **Infraestructura** | Docker, Gunicorn, Nginx, Celery + Redis |
| **ETL** | Pandas, DuckDB, NetworkX |

**Documentación detallada**:
- [architecture/stack.md](architecture/stack.md) - Resumen del stack
- [architecture/standards/stack-tecnico-propuesto.md](architecture/standards/stack-tecnico-propuesto.md) - Propuesta completa con ejemplos, Docker Compose, requirements.txt
- [architecture/standards/antipatrones-y-deuda-tecnica.md](architecture/standards/antipatrones-y-deuda-tecnica.md) - Cómo usar el stack correctamente

---

## Principios Fundamentales

### Story-First Development

> **"Si no hay Historia, no existe el requerimiento."**

La derivación es unidireccional: **Stories → Entities → Artifacts → Modules**

### Minimalismo Radical

Solo 4 átomos fundamentales:
1. **Story** (Historia de Usuario) - Origen absoluto del valor
2. **Entity** (Entidad) - Estructura de información
3. **Role** (Rol) - Agente activo (humano o algorítmico)
4. **Process** (Proceso) - Perspectiva dinámica

### Las 5 Funciones Motoras

El GORE ejecuta 5 funciones esenciales que GORE_OS soporta:
1. **PLANIFICAR** - ERD, PROT, ARI
2. **FINANCIAR** - FNDR, FRIL, fondos regionales
3. **EJECUTAR** - Convenios, obras, programas
4. **COORDINAR** - Municipios, servicios, gabinete
5. **NORMAR** - Resoluciones, reglamentos

---

## Modelo de Datos v3.0

El sistema se centra en **IPR (Intervención Pública Regional)** como entidad abstracta polimórfica:

- **Tipos**: PROYECTO (inversión capital) vs PROGRAMA (gasto corriente)
- **Fondos**: FNDR, FRIL, FRPD, ISAR
- **Evaluación**: SNI, C33, FRIL, Glosa 06, 8% FNDR
- **Estados**: 31 estados del ciclo de vida

DDL ejecutable en: [model/model_goreos/sql/](model/model_goreos/sql/)

---

## Integraciones TDE (Transformación Digital del Estado)

GORE_OS se integra con sistemas nacionales chilenos:
- **ClaveÚnica** - Autenticación ciudadana
- **PISEE** - Interoperabilidad (Once-Only Principle)
- **DocDigital** - Firma electrónica
- **SIGFE/DIPRES** - Integración presupuestaria
- **SIAPER/CGR** - Toma de razón CGR

---

## Changelog y Evolución

Ver [JOURNAL.md](JOURNAL.md) para log de decisiones arquitectónicas y pivots técnicos.

Versión actual: **v3.0.0 (Enero 2026)**

---

## Licencia y Contacto

GORE_OS es desarrollado por el Gobierno Regional de Ñuble, Chile.

Para consultas técnicas, ver [CLAUDE.md](CLAUDE.md) o contactar al equipo de desarrollo.
