# Guía de Inicio - GORE_OS Development

Esta guía te ayudará a configurar tu entorno de desarrollo local para trabajar con GORE_OS.

---

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Docker 24+** y **Docker Compose 2.x**
  - Instalar desde: https://www.docker.com/get-started
- **Python 3.11+**
  - Verificar: `python3 --version`
- **PostgreSQL client** (psql) para verificaciones y consultas directas
  - macOS: `brew install postgresql@16`
  - Ubuntu: `sudo apt install postgresql-client-16`
- **Git** para control de versiones

---

## 🏛️ Fundamento: El Modelo PostgreSQL

**IMPORTANTE**: GORE_OS se construye sobre un modelo de datos PostgreSQL excepcional en `/model/model_goreos`.

### Características del Modelo

- **54 tablas** en 4 schemas semánticos (`meta`, `ref`, `core`, `txn`)
- **100% derivado** de 819 User Stories validadas
- **Category Pattern** (Gist 14.0) para 75+ vocabularios controlados
- **Event Sourcing** híbrido con particionamiento
- **Auditado exhaustivamente** (ver `/model/model_goreos/docs/auditorias/`)

Este modelo es la base de toda la aplicación. Sin él, no hay GORE_OS.

---

## Instalación Rápida (15 minutos)

### 1. Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/gorenuble/goreos.git
cd goreos

# Ejecutar script de setup automatizado
./scripts/setup_dev_env.sh
```

El script automáticamente:
- ✅ Verifica prerrequisitos (Docker, Python)
- ✅ Crea archivo `.env` desde plantilla
- ✅ Levanta PostgreSQL con Docker Compose
- ✅ Ejecuta el DDL del modelo (8 archivos SQL)
- ✅ Levanta PgAdmin para administración

### 2. Editar Credenciales

```bash
# Editar .env con tus credenciales reales
nano .env

# Mínimo requerido para desarrollo local:
# DB_NAME=goreos
# DB_USER=goreos
# DB_PASSWORD=tu_password_seguro
```

### 3. Verificar Instalación

```bash
# Ejecutar script de verificación
./scripts/verify_model.sh
```

**Salida esperada:**
```
✅ PostgreSQL está corriendo y listo
   meta: 5 tablas
   ref: 3 tablas
   core: 40+ tablas
   txn: 2+ tablas
✅ Total: 54 tablas
✅ Schemes de categorías: 75+
✅ Territorio de Región de Ñuble cargado
✅ Modelo PostgreSQL GORE_OS verificado exitosamente
```

---

## Instalación Manual (Paso a Paso)

Si prefieres control total, sigue estos pasos:

### 1. Configurar .env

```bash
cp .env.example .env
nano .env  # Editar credenciales
```

### 2. Levantar PostgreSQL

```bash
docker-compose up -d postgres
```

### 3. Esperar a que PostgreSQL esté listo

```bash
# Verificar estado
docker exec goreos_db pg_isready -U goreos

# Ver logs si hay problemas
docker-compose logs -f postgres
```

### 4. Ejecutar DDL manualmente (solo si no se auto-ejecutó)

```bash
cd model/model_goreos/sql

# Ejecutar archivos en orden estricto (CRÍTICO)
psql -h localhost -U goreos -d goreos -f goreos_ddl.sql
psql -h localhost -U goreos -d goreos -f goreos_seed.sql
psql -h localhost -U goreos -d goreos -f goreos_seed_agents.sql
psql -h localhost -U goreos -d goreos -f goreos_seed_territory.sql
psql -h localhost -U goreos -d goreos -f goreos_triggers.sql
psql -h localhost -U goreos -d goreos -f goreos_triggers_remediation.sql
psql -h localhost -U goreos -d goreos -f goreos_indexes.sql
psql -h localhost -U goreos -d goreos -f goreos_remediation_ontological.sql

cd ../../..
```

### 5. Levantar PgAdmin (opcional)

```bash
docker-compose up -d pgadmin
```

---

## Estructura del Modelo

El modelo en `/model/model_goreos` está organizado en 4 schemas:

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `meta` | 5 | Átomos fundamentales (Role, Process, Entity, Story, Story-Entity) |
| `ref` | 3 | Vocabularios controlados (Category, Actor, Commitment Types) |
| `core` | 40+ | Entidades de negocio (IPR, Agreements, Budget, Work Items, etc.) |
| `txn` | 2+ | Event Sourcing (Event, Magnitude) - Particionadas por mes/trimestre |

**Documentación completa del modelo**:
- [model/model_goreos/README.md](../../model/model_goreos/README.md) - Guía completa
- [model/model_goreos/docs/GOREOS_ERD_v3.md](../../model/model_goreos/docs/GOREOS_ERD_v3.md) - ERD + Data Dictionary
- [model/model_goreos/docs/DESIGN_DECISIONS.md](../../model/model_goreos/docs/DESIGN_DECISIONS.md) - Decisiones de diseño

---

## Desarrollo de Módulos

GORE_OS está organizado en 6 módulos funcionales (Blueprints Flask):

### Módulos Principales

1. **BP-FIN (Finanzas)** - Presupuesto, modificaciones, estados de pago ⭐ **EMPEZAR AQUÍ**
2. **BP-EJEC (Ejecución)** - Convenios, obras, supervisión
3. **BP-TERR (Territorial)** - Gemelo digital, mapas, análisis territorial
4. **BP-NORM (Normativo)** - Resoluciones, expedientes electrónicos
5. **BP-BACK (Backoffice)** - RR.HH., compras
6. **BP-AUTH (Autenticación)** - ClaveÚnica, roles, permisos

**Ver especificaciones completas**: [docs/technical/especificaciones.md](../technical/especificaciones.md)

### Pipeline de Datos: ETL → PostgreSQL → Apps

GORE_OS utiliza un pipeline ETL robusto para migrar datos legacy:

```
/etl/sources/               # Datos legacy (Excel, CSV)
      ↓
/etl/scripts/               # 470 scripts de transformación Python
      ↓
/etl/normalized/            # Datos limpios y validados
      ↓
model/model_goreos (PostgreSQL)   # Modelo canónico (LA VERDAD)
      ↓
apps/streamlit_tooling/     # Tooling interno existente
apps/flask_app/             # Aplicación productiva (a construir)
```

**Documentación ETL**: [etl/README.md](../../etl/README.md)

---

## Herramientas de Desarrollo

### PgAdmin (Explorador de Base de Datos)

- **URL**: http://localhost:5050
- **Email**: `admin@gorenuble.cl` (configurable en `.env`)
- **Password**: `admin` (configurable en `.env`)

#### Conectar PgAdmin a PostgreSQL

1. Acceder a http://localhost:5050
2. Login con credenciales de `.env`
3. **Add Server**:
   - **Name**: GORE_OS Local
   - **Connection tab**:
     - Host: `postgres` (nombre del servicio en Docker) o `localhost` (desde host)
     - Port: `5432`
     - Database: `goreos`
     - Username: `goreos`
     - Password: [el configurado en `.env`]

### psql (Cliente CLI)

```bash
# Conectar desde host
psql -h localhost -U goreos -d goreos

# Consultas útiles
\dt core.*                              # Listar tablas del schema core
SELECT * FROM ref.category LIMIT 10;   # Ver categorías
\d core.ipr                             # Describir tabla IPR
```

### Python Virtual Environment

```bash
# Crear virtual env
python3.11 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar GORE_OS con dependencias de desarrollo
pip install -e .[dev]

# O instalar solo lo necesario para tu trabajo:
pip install -e .[flask]      # Flask app
pip install -e .[streamlit]  # Streamlit tooling
pip install -e .[etl]        # ETL scripts
```

---

## Comandos Docker Útiles

```bash
# Levantar servicios
docker-compose up -d postgres pgadmin    # Solo PostgreSQL + PgAdmin
docker-compose up -d                     # Todos los servicios

# Ver logs
docker-compose logs -f postgres          # Logs de PostgreSQL
docker-compose logs -f                   # Logs de todos

# Detener servicios
docker-compose down                      # Detener (mantiene datos)
docker-compose down -v                   # Detener y eliminar volúmenes (⚠️  BORRA DATOS)

# Reiniciar servicios
docker-compose restart postgres

# Estado de servicios
docker-compose ps

# Ejecutar comandos en contenedor
docker exec -it goreos_db psql -U goreos -d goreos
docker exec goreos_db pg_dump -U goreos goreos > backup.sql
```

---

## Troubleshooting

### PostgreSQL no inicia

```bash
# Ver logs
docker-compose logs postgres

# Verificar puerto ocupado
lsof -i :5432

# Eliminar volumen y reiniciar (⚠️  BORRA DATOS)
docker-compose down -v
docker-compose up -d postgres
```

### Modelo no se cargó automáticamente

```bash
# Ejecutar DDL manualmente
cd model/model_goreos/sql
for file in goreos_*.sql; do
    echo "Ejecutando $file..."
    psql -h localhost -U goreos -d goreos -f $file
done
cd ../../..

# Verificar
./scripts/verify_model.sh
```

### Errores de conexión PostgreSQL

```bash
# Verificar que el servicio esté corriendo
docker ps | grep goreos_db

# Verificar health check
docker inspect goreos_db | grep -A 10 Health

# Reiniciar servicio
docker-compose restart postgres
```

### PgAdmin no carga

```bash
# Verificar logs
docker-compose logs pgadmin

# Reiniciar
docker-compose restart pgadmin

# Limpiar caché del navegador
```

### Dependencias Python

```bash
# Reinstalar desde cero
pip install -e .[dev] --force-reinstall --no-cache-dir

# Verificar versiones instaladas
pip list | grep -i flask
pip list | grep -i sqlalchemy
```

---

## Próximos Pasos

1. **Estudiar el Modelo** (2-3 horas)
   - Leer [model/model_goreos/README.md](../../model/model_goreos/README.md)
   - Revisar [model/model_goreos/docs/GOREOS_ERD_v3.md](../../model/model_goreos/docs/GOREOS_ERD_v3.md)
   - Explorar tablas en PgAdmin

2. **Leer Especificaciones** (1-2 horas)
   - [docs/technical/especificaciones.md](../technical/especificaciones.md) - Requisitos de módulos
   - [docs/technical/planclaude.md](../technical/planclaude.md) - Plan maestro
   - [architecture/standards/stack-tecnico-propuesto.md](../../architecture/standards/stack-tecnico-propuesto.md) - Stack completo

3. **Comenzar Desarrollo de BP-FIN** (próximo sprint)
   - Crear `/apps/flask_app/blueprints/bp_fin/`
   - Derivar modelos SQLAlchemy del DDL
   - Implementar primer endpoint (modificación presupuestaria)
   - Usar datos migrados de `/etl/normalized/`

---

## Recursos Adicionales

### Documentación del Proyecto

- **[INDEX.md](../../INDEX.md)** - Punto de entrada con navegación completa
- **[README.md](../../README.md)** - Introducción al proyecto
- **[MANIFESTO.md](../../MANIFESTO.md)** - Filosofía Story-First
- **[CLAUDE.md](../../CLAUDE.md)** - Guía para Claude Code

### Documentación Técnica

- **[architecture/stack.md](../../architecture/stack.md)** - Stack tecnológico oficial
- **[architecture/standards/antipatrones-y-deuda-tecnica.md](../../architecture/standards/antipatrones-y-deuda-tecnica.md)** - Errores a evitar
- **[architecture/decisions/ADR-003-modelo-como-base.md](../../architecture/decisions/ADR-003-modelo-como-base.md)** - Decisión arquitectónica

### Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| **Backend** | Python 3.11+, Flask 3.0.3, SQLAlchemy 2.0.30 |
| **Frontend** | Jinja2 (SSR), HTMX 2.0.0, Alpine.js 3.x, Tailwind CSS 3.4.0 |
| **Base de Datos** | PostgreSQL 16 + PostGIS |
| **Infraestructura** | Docker, Gunicorn, Nginx, Celery + Redis |
| **ETL** | Pandas 2.0+, DuckDB 0.9.2, NetworkX |

---

## Contacto y Soporte

Para consultas o problemas:
1. Revisar documentación en `/docs/`
2. Verificar troubleshooting en esta guía
3. Consultar [CLAUDE.md](../../CLAUDE.md) para guía de Claude Code
4. Contactar al equipo de desarrollo GORE_OS

---

*Guía creada: 2026-01-29*
*Última actualización: 2026-01-29*
*GORE_OS v3.1.0*
