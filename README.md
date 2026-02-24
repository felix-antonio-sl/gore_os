# GORE_OS — Sistema Operativo del Gobierno Regional de Ñuble

> Para navegacion completa del repositorio, ver [INDEX.md](INDEX.md)

**Version:** 3.2.0
**Estado:** En transicion a stack de agentes LLM
**Filosofia:** Story-First & Minimalismo Radical

---

## La Base: Modelo de Datos PostgreSQL

**Todo se construye sobre el modelo de datos**:

- **Ubicacion**: `/model/model_goreos`
- **71 tablas** organizadas en 4 schemas semanticos (`meta`, `ref`, `core`, `txn`)
- **100% derivado** de 820 User Stories validadas
- **Category Pattern** (Gist 14.0) para 78+ vocabularios controlados
- **Event Sourcing** hibrido con particionamiento temporal
- **Univocidad categorial** verificada al 100%

### Quick Start

```bash
# Levantar PostgreSQL
docker compose up -d postgres

# Verificar conexion
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT version();"

# Ver tablas por schema
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT schemaname, COUNT(*) AS tables FROM pg_tables
WHERE schemaname IN ('meta','ref','core','txn') GROUP BY schemaname;"
```

**Documentacion del modelo**: [model/model_goreos/README.md](model/model_goreos/README.md)

---

## Que es GORE_OS?

GORE_OS es el **sistema operativo institucional** del Gobierno Regional de Nuble. No es un software tradicional, sino un **modelo integrado de datos, procesos y capacidades** que permite al GORE funcionar de manera coherente, auditable y evolucionar organicamente.

> Para la vision politica y estrategica, ver [MANIFESTO.md](MANIFESTO.md)

---

## Principio Rector: Story-First

```
Stories → Entities → Artifacts → Modules
```

1. **Story**: El punto de partida absoluto. Si no hay story, no existe el requerimiento.
2. **Entity**: El modelo de datos necesario para soportar la story.
3. **Role**: El agente (humano o maquina) que interactua con la story.
4. **Process**: La orquestacion temporal de la story.

---

## Estructura del Repositorio

```
goreos/
├── model/                     # EL CORAZON - Modelo semantico
│   ├── stories/               # 820 historias de usuario
│   ├── entities/aceptadas/    # 141 entidades validadas
│   ├── processes/             # 92 procesos
│   ├── model_goreos/          # DDL PostgreSQL ejecutable
│   ├── omega/                 # Definiciones ontologicas
│   └── GLOSARIO.yml           # 244 terminos
├── architecture/              # ADRs, definicion Omega
├── docs/                      # Auditorias categoriales
├── docker-compose.yml         # PostgreSQL + PgAdmin
└── MANIFESTO.md               # Constitucion del sistema
```

---

## Estado del Proyecto

El modelo de datos PostgreSQL (71 tablas, 78+ category schemes) y las 820 user stories son los activos de valor permanente. El codigo de aplicacion esta en transicion de un legacy (Flask+Streamlit) a un stack de agentes LLM (Next.js + FastAPI + MCP + PostgreSQL + pgvector).

Los artefactos del stack anterior se preservan en `docs/legacy/` y `architecture/legacy/` como referencia historica.

---

*GORE_OS Dev Team — Febrero 2026*
