#!/bin/bash
# migrate_to_domain_free.sh
# Migra entidades GORE_OS a modelo domain-free

ENTITIES_DIR="/Users/felixsanhueza/fx_felixiando/gore_os/model/entities"

echo "=== Migración a Modelo Domain-Free ==="
echo ""

# 1. Extraer mapping actual de IDs
echo "Paso 1: Generando mapping de IDs..."
for f in "$ENTITIES_DIR"/ent-*.yml; do
    if [[ -f "$f" ]]; then
        # Extraer ID actual (ej: ENT-FIN-IPR)
        current_id=$(grep "^id:" "$f" | head -1 | sed 's/id: //')
        # Extraer dominio del ID (ej: FIN)
        domain_code=$(echo "$current_id" | cut -d'-' -f2)
        # Extraer nombre base (ej: IPR)
        base_name=$(echo "$current_id" | cut -d'-' -f3-)
        # Nuevo ID domain-free (ej: ENT-IPR)
        new_id="ENT-$base_name"
        
        echo "$current_id -> $new_id (tag: $domain_code)"
    fi
done

echo ""
echo "Paso 2: Para ejecutar la migración real, use --execute"
echo ""
echo "Cambios pendientes:"
echo "  - Renombrar IDs en archivos YAML"
echo "  - Actualizar todas las referencias FK"
echo "  - Agregar campo 'tags' con dominio original"
echo "  - Renombrar archivos (ent-fin-ipr.yml -> ent-ipr.yml)"
