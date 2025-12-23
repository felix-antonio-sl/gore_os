#!/bin/bash
# generate_domain_free_entities.sh
# Genera esqueletos YAML para candidatos domain-free

ENTITIES_DIR="/Users/felixsanhueza/fx_felixiando/gore_os/model/entities"
CANDIDATES_FILE="$ENTITIES_DIR/candidates_domain_free.csv"
OUTPUT_DIR="$ENTITIES_DIR/candidates"

mkdir -p "$OUTPUT_DIR"

echo "=== Generador de Entidades Domain-Free ==="
echo ""

# Procesar solo candidatos únicos (sin colisión)
cut -d'|' -f1 "$CANDIDATES_FILE" | sort | uniq -c | awk '$1 == 1 {print $2}' | while read new_id; do
    # Obtener info del CSV
    line=$(grep "^$new_id|" "$CANDIDATES_FILE" | head -1)
    tag=$(echo "$line" | cut -d'|' -f2)
    old_id=$(echo "$line" | cut -d'|' -f3)
    
    # Convertir ID a nombre de archivo (ent-nombre.yml)
    filename=$(echo "$new_id" | sed 's/ENT-/ent-/' | tr '[:upper:]' '[:lower:]' | tr '-' '_')
    filepath="$OUTPUT_DIR/${filename}.yml"
    
    # Generar esqueleto YAML
    cat > "$filepath" << EOF
---
_meta:
  urn: urn:goreos:entity:$(echo "$tag" | tr '[:upper:]' '[:lower:]'):$(echo "$new_id" | sed 's/ENT-//' | tr '[:upper:]' '[:lower:]' | tr '-' '_'):1.0.0
  type: Entity
  schema: urn:goreos:schema:entity:2.0.0
  origin: candidate
  source_id: "$old_id"
id: $new_id
name: "$(echo "$new_id" | sed 's/ENT-//' | tr '-' ' ' | sed 's/.*/\L&/; s/[a-z]*/\u&/g')"
tags: [$tag]
category: Master
attributes:
  - { name: id, type: UUID, key: true }
  # TODO: Definir atributos específicos
EOF
    
    echo "Generado: $filepath"
done

echo ""
echo "=== Resumen ==="
echo "Candidatos procesados: $(ls -1 $OUTPUT_DIR/*.yml 2>/dev/null | wc -l)"
echo "Ubicación: $OUTPUT_DIR"
