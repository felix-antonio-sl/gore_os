# GORE_OS - Sistema Operativo Institucional del Gobierno Regional de Ñuble

> **Version 3.2** | **Story-First & Radical Minimalism**

---

## La Base: Modelo de Datos PostgreSQL

El corazon del sistema es el modelo PostgreSQL en `/model/model_goreos`:
- **71 tablas** en 4 schemas semanticos (`meta`, `ref`, `core`, `txn`)
- **78+ vocabularios** controlados (Category Pattern, Gist 14.0)
- **100% trazable** a 820 User Stories validadas
- **Event Sourcing** hibrido con particionamiento

**Documentacion del modelo**:
- [model/model_goreos/README.md](model/model_goreos/README.md) - Guia del modelo
- [model/model_goreos/docs/GOREOS_ERD_v3.md](model/model_goreos/docs/GOREOS_ERD_v3.md) - ERD + Data Dictionary
- [architecture/decisions/ADR-003-modelo-como-base.md](architecture/decisions/ADR-003-modelo-como-base.md) - Decision arquitectonica

---

## Por donde empezar?

### Para Nuevos Desarrolladores

1. **[README.md](README.md)** - Introduccion general al proyecto
2. **[MANIFESTO.md](MANIFESTO.md)** - Filosofia Story-First y las 5 Funciones Motoras
3. **[CLAUDE.md](CLAUDE.md)** - Guia para Claude Code (arquitectura, modelo, comandos)

### Para Arquitectos y Disenadores de Datos

1. **[model/model_goreos/README.md](model/model_goreos/README.md)** - Modelo de datos v3.2 ejecutable
2. **[architecture/Omega_GORE_OS_Definition_v3.0.0.md](architecture/Omega_GORE_OS_Definition_v3.0.0.md)** - Definicion omega del sistema
3. **[model/GLOSARIO.yml](model/GLOSARIO.yml)** - Glosario autoritativo de 244 terminos
4. **[docs/AUDITORIA_CATEGORIAL_v3.0.md](docs/AUDITORIA_CATEGORIAL_v3.0.md)** - Auditoria categorial completa

### Para Product Owners y Analistas

1. **[model/stories/](model/stories/)** - 820+ historias de usuario validadas (fuente de verdad)
2. **[model/entities/aceptadas/](model/entities/aceptadas/)** - 141 entidades aceptadas
3. **[model/processes/](model/processes/)** - 92 procesos del dominio

---

## Estructura del Repositorio

```
goreos/
├── model/                     # EL CORAZON - Modelo semantico del dominio
│   ├── stories/               # 820 historias YAML (fuente de verdad)
│   ├── entities/aceptadas/    # 141 entidades aceptadas
│   ├── processes/             # 92 procesos
│   ├── model_goreos/          # Modelo ejecutable v3.2 (DDL PostgreSQL)
│   │   ├── sql/               # DDL, indexes, seed, triggers
│   │   └── docs/              # ERD, Design Decisions
│   ├── omega/                 # Definiciones ontologicas
│   └── GLOSARIO.yml           # 244 terminos (Gist 14.0 + GNUB + TDE)
├── architecture/
│   ├── decisions/             # ADRs (Architecture Decision Records)
│   ├── Omega_GORE_OS_Definition_v3.0.0.md
│   └── legacy/                # Docs del stack anterior (frozen)
├── docs/
│   ├── AUDITORIA_CATEGORIAL_v3.0.md
│   ├── PLAN_NORMALIZACION_JSONB_v2.0.md
│   └── legacy/                # ETL sources, migration SQL, docs historicos
├── docker-compose.yml         # PostgreSQL + PgAdmin
├── .env.example               # Variables de entorno
├── CLAUDE.md                  # Guia para Claude Code
├── INDEX.md                   # Este archivo
├── MANIFESTO.md               # Identidad y genesis
└── README.md                  # Introduccion general
```

---

## Principios Fundamentales

### Story-First Development

> **"Si no hay Historia, no existe el requerimiento."**

La derivacion es unidireccional: **Stories → Entities → Artifacts → Modules**

### Minimalismo Radical

Solo 4 atomos fundamentales:
1. **Story** (Historia de Usuario) - Origen absoluto del valor
2. **Entity** (Entidad) - Estructura de informacion
3. **Role** (Rol) - Agente activo (humano o algoritmico)
4. **Process** (Proceso) - Perspectiva dinamica

### Las 5 Funciones Motoras

El GORE ejecuta 5 funciones esenciales que GORE_OS soporta:
1. **PLANIFICAR** - ERD, PROT, ARI
2. **FINANCIAR** - FNDR, FRIL, fondos regionales
3. **EJECUTAR** - Convenios, obras, programas
4. **COORDINAR** - Municipios, servicios, gabinete
5. **NORMAR** - Resoluciones, reglamentos

---

## Modelo de Datos v3.2

El sistema se centra en **IPR (Intervencion Publica Regional)** como entidad abstracta polimorfica:

- **Tipos**: PROYECTO (inversion capital) vs PROGRAMA (gasto corriente)
- **Fondos**: FNDR, FRIL, FRPD, ISAR
- **Evaluacion**: SNI, C33, FRIL, Glosa 06, 8% FNDR
- **Estados**: 31 estados del ciclo de vida

DDL ejecutable en: [model/model_goreos/sql/](model/model_goreos/sql/)

---

## Integraciones TDE (Transformacion Digital del Estado)

GORE_OS se integra con sistemas nacionales chilenos:
- **ClaveUnica** - Autenticacion ciudadana
- **PISEE** - Interoperabilidad (Once-Only Principle)
- **DocDigital** - Firma electronica
- **SIGFE/DIPRES** - Integracion presupuestaria
- **SIAPER/CGR** - Toma de razon CGR

---

## Licencia y Contacto

GORE_OS es desarrollado por el Gobierno Regional de Nuble, Chile.

Para consultas tecnicas, ver [CLAUDE.md](CLAUDE.md) o contactar al equipo de desarrollo.
