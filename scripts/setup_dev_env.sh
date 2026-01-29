#!/bin/bash
# =============================================================================
# GORE_OS Development Environment Setup
# =============================================================================
# Este script configura el entorno de desarrollo completo:
# - Verifica prerrequisitos
# - Crea archivo .env si no existe
# - Levanta PostgreSQL con Docker Compose
# - Espera a que el modelo se cargue
#
# Uso: ./scripts/setup_dev_env.sh
# =============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# =============================================================================
# 1. VERIFICAR PRERREQUISITOS
# =============================================================================
log_info "Verificando prerrequisitos..."

# Docker
if ! command -v docker >/dev/null 2>&1; then
    log_error "Docker no está instalado"
    echo "Instalar desde: https://www.docker.com/get-started"
    exit 1
fi
log_success "Docker instalado: $(docker --version)"

# Docker Compose
if ! command -v docker-compose >/dev/null 2>&1; then
    log_error "Docker Compose no está instalado"
    exit 1
fi
log_success "Docker Compose instalado: $(docker-compose --version)"

# Python 3.11+
if ! command -v python3 >/dev/null 2>&1; then
    log_error "Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    log_warning "Python $PYTHON_VERSION detectado. Se recomienda Python 3.11+"
else
    log_success "Python $PYTHON_VERSION instalado"
fi

# =============================================================================
# 2. CONFIGURAR ARCHIVO .env
# =============================================================================
log_info "Configurando archivo .env..."

if [ ! -f .env ]; then
    log_info "Creando .env desde .env.example..."
    cp .env.example .env
    log_warning "IMPORTANTE: Editar .env con credenciales reales"
    log_warning "Comando: nano .env"
else
    log_success ".env ya existe"
fi

# =============================================================================
# 3. LEVANTAR POSTGRESQL
# =============================================================================
log_info "Levantando PostgreSQL..."

# Verificar si ya está corriendo
if docker ps | grep -q goreos_db; then
    log_success "PostgreSQL ya está corriendo"
else
    log_info "Iniciando contenedor PostgreSQL..."
    docker-compose up -d postgres

    log_info "Esperando que PostgreSQL esté listo (timeout: 30s)..."

    COUNTER=0
    MAX_TRIES=30

    while [ $COUNTER -lt $MAX_TRIES ]; do
        if docker exec goreos_db pg_isready -U goreos >/dev/null 2>&1; then
            log_success "PostgreSQL está listo"
            break
        fi

        COUNTER=$((COUNTER + 1))
        if [ $COUNTER -eq $MAX_TRIES ]; then
            log_error "Timeout esperando PostgreSQL"
            log_info "Ver logs: docker-compose logs postgres"
            exit 1
        fi

        echo -n "."
        sleep 1
    done
    echo ""
fi

# =============================================================================
# 4. VERIFICAR CARGA DEL MODELO
# =============================================================================
log_info "Verificando carga del modelo..."

# Dar tiempo adicional para que el initdb termine
sleep 2

TABLES_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*)
    FROM pg_tables
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn');
" 2>/dev/null | tr -d ' ')

if [ -z "$TABLES_COUNT" ] || [ "$TABLES_COUNT" -eq "0" ]; then
    log_warning "El modelo no se cargó automáticamente"
    log_info "Ejecutando DDL manualmente..."

    cd model/model_goreos/sql

    for SQL_FILE in goreos_ddl.sql goreos_seed.sql goreos_seed_agents.sql \
                    goreos_seed_territory.sql goreos_triggers.sql \
                    goreos_triggers_remediation.sql goreos_indexes.sql \
                    goreos_remediation_ontological.sql; do
        log_info "Ejecutando $SQL_FILE..."
        docker exec -i goreos_db psql -U goreos -d goreos < $SQL_FILE
    done

    cd ../../..
    log_success "DDL ejecutado manualmente"
else
    log_success "Modelo cargado: $TABLES_COUNT tablas detectadas"
fi

# =============================================================================
# 5. LEVANTAR PGADMIN (opcional)
# =============================================================================
log_info "Levantando PgAdmin..."

if docker ps | grep -q goreos_pgadmin; then
    log_success "PgAdmin ya está corriendo"
else
    docker-compose up -d pgadmin
    log_success "PgAdmin iniciado"
fi

# =============================================================================
# 6. RESUMEN
# =============================================================================
echo ""
echo "=========================================================================="
log_success "Entorno de desarrollo configurado exitosamente"
echo "=========================================================================="
echo ""
echo "📊 Accesos:"
echo "   - PostgreSQL: localhost:5432"
echo "   - PgAdmin:    http://localhost:5050"
echo ""
echo "🔑 Credenciales (ver .env):"
echo "   - DB User:     goreos"
echo "   - DB Name:     goreos"
echo "   - DB Password: (configurado en .env)"
echo ""
echo "🎯 Próximos pasos:"
echo "   1. Editar .env con credenciales reales: nano .env"
echo "   2. Verificar modelo: ./scripts/verify_model.sh"
echo "   3. Instalar dependencias Python: pip install -e .[dev]"
echo "   4. Conectar a DB: psql -h localhost -U goreos -d goreos"
echo ""
log_info "Modelo PostgreSQL en: /model/model_goreos"
log_info "Documentación: /model/model_goreos/README.md"
echo ""
