#!/bin/bash
# =============================================================================
# GORE_OS Model Verification Script
# =============================================================================
# Verifica que el modelo PostgreSQL esté correctamente instalado:
# - Tablas por schema (meta, ref, core, txn)
# - Seed data (categorías, territorio, agentes)
# - Triggers activos
# - Constraints funcionando
#
# Uso: ./scripts/verify_model.sh
# =============================================================================

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}🔍 $1${NC}"
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
# 1. VERIFICAR POSTGRESQL
# =============================================================================
log_info "Verificando PostgreSQL..."

if ! docker ps | grep -q goreos_db; then
    log_error "PostgreSQL no está corriendo"
    echo "Ejecutar: docker-compose up -d postgres"
    exit 1
fi

if ! docker exec goreos_db pg_isready -U goreos >/dev/null 2>&1; then
    log_error "PostgreSQL no está listo"
    exit 1
fi

log_success "PostgreSQL está corriendo y listo"

# =============================================================================
# 2. CONTAR TABLAS POR SCHEMA
# =============================================================================
echo ""
log_info "Contando tablas por schema..."

TABLES_RESULT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT schemaname, COUNT(*) AS tables
    FROM pg_tables
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn')
    GROUP BY schemaname
    ORDER BY schemaname;
")

echo "$TABLES_RESULT" | while read -r line; do
    SCHEMA=$(echo "$line" | awk '{print $1}')
    COUNT=$(echo "$line" | awk '{print $2}')

    if [ -n "$SCHEMA" ]; then
        echo "   $SCHEMA: $COUNT tablas"
    fi
done

TOTAL_TABLES=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*)
    FROM pg_tables
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn');
" | tr -d ' ')

if [ "$TOTAL_TABLES" -lt 50 ]; then
    log_warning "Solo $TOTAL_TABLES tablas detectadas (esperado: 54+)"
else
    log_success "Total: $TOTAL_TABLES tablas"
fi

# =============================================================================
# 3. VERIFICAR SEED DATA - CATEGORÍAS
# =============================================================================
echo ""
log_info "Verificando seed data de categorías..."

SCHEMES_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(DISTINCT scheme) FROM ref.category;
" | tr -d ' ')

if [ "$SCHEMES_COUNT" -lt 70 ]; then
    log_warning "Solo $SCHEMES_COUNT schemes detectados (esperado: 75+)"
else
    log_success "Schemes de categorías: $SCHEMES_COUNT"
fi

CATEGORIES_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*) FROM ref.category;
" | tr -d ' ')

log_info "Total de categorías: $CATEGORIES_COUNT"

# =============================================================================
# 4. VERIFICAR SEED DATA - TERRITORIO
# =============================================================================
echo ""
log_info "Verificando seed data de territorio..."

REGIONS_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*) FROM core.region WHERE deleted_at IS NULL;
" 2>/dev/null | tr -d ' ' || echo "0")

PROVINCES_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*) FROM core.province WHERE deleted_at IS NULL;
" 2>/dev/null | tr -d ' ' || echo "0")

COMMUNES_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*) FROM core.commune WHERE deleted_at IS NULL;
" 2>/dev/null | tr -d ' ' || echo "0")

echo "   Regiones:  $REGIONS_COUNT"
echo "   Provincias: $PROVINCES_COUNT (esperado: 3)"
echo "   Comunas:    $COMMUNES_COUNT (esperado: 21)"

if [ "$PROVINCES_COUNT" -eq "3" ] && [ "$COMMUNES_COUNT" -eq "21" ]; then
    log_success "Territorio de Región de Ñuble cargado"
else
    log_warning "Territorio incompleto"
fi

# =============================================================================
# 5. VERIFICAR AGENTES KODA
# =============================================================================
echo ""
log_info "Verificando agentes KODA..."

AGENTS_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*) FROM meta.role WHERE role_type = 'AGENT' AND deleted_at IS NULL;
" 2>/dev/null | tr -d ' ' || echo "0")

log_info "Agentes KODA: $AGENTS_COUNT"

# =============================================================================
# 6. VERIFICAR TRIGGERS
# =============================================================================
echo ""
log_info "Verificando triggers activos..."

TRIGGERS_RESULT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT n.nspname, COUNT(*) AS triggers
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname IN ('meta', 'ref', 'core', 'txn')
      AND NOT t.tgisinternal
    GROUP BY n.nspname
    ORDER BY n.nspname;
")

echo "$TRIGGERS_RESULT" | while read -r line; do
    SCHEMA=$(echo "$line" | awk '{print $1}')
    COUNT=$(echo "$line" | awk '{print $2}')

    if [ -n "$SCHEMA" ]; then
        echo "   $SCHEMA: $COUNT triggers"
    fi
done

TOTAL_TRIGGERS=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*)
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname IN ('meta', 'ref', 'core', 'txn')
      AND NOT t.tgisinternal;
" | tr -d ' ')

log_success "Total triggers: $TOTAL_TRIGGERS"

# =============================================================================
# 7. VERIFICAR FUNCIONES PL/pgSQL
# =============================================================================
echo ""
log_info "Verificando funciones PL/pgSQL..."

FUNCTIONS_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*)
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname IN ('meta', 'ref', 'core', 'txn')
      AND p.prokind = 'f';
" | tr -d ' ')

log_info "Funciones definidas: $FUNCTIONS_COUNT"

# =============================================================================
# 8. VERIFICAR ÍNDICES
# =============================================================================
echo ""
log_info "Verificando índices..."

INDEXES_COUNT=$(docker exec goreos_db psql -U goreos -d goreos -t -c "
    SELECT COUNT(*)
    FROM pg_indexes
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn');
" | tr -d ' ')

log_success "Índices creados: $INDEXES_COUNT"

# =============================================================================
# 9. RESUMEN FINAL
# =============================================================================
echo ""
echo "=========================================================================="

# Determinar estado general
ERRORS=0

if [ "$TOTAL_TABLES" -lt 50 ]; then ERRORS=$((ERRORS + 1)); fi
if [ "$SCHEMES_COUNT" -lt 70 ]; then ERRORS=$((ERRORS + 1)); fi
if [ "$PROVINCES_COUNT" -ne 3 ] || [ "$COMMUNES_COUNT" -ne 21 ]; then ERRORS=$((ERRORS + 1)); fi

if [ $ERRORS -eq 0 ]; then
    log_success "Modelo PostgreSQL GORE_OS verificado exitosamente"
else
    log_warning "Modelo verificado con $ERRORS advertencias"
fi

echo "=========================================================================="
echo ""
log_info "Documentación completa: /model/model_goreos/README.md"
log_info "ERD + Data Dictionary: /model/model_goreos/docs/GOREOS_ERD_v3.md"
echo ""
