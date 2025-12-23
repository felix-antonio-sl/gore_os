#!/bin/bash
# resolve_collisions.sh
# Genera esqueletos para las 16 colisiones resueltas

OUTPUT_DIR="/Users/felixsanhueza/fx_felixiando/gore_os/model/entities/candidates"

echo "=== Resolver Colisiones Domain-Free ==="
echo ""

# Función para generar YAML
generate_entity() {
    local id="$1"
    local name="$2"
    local tags="$3"
    local filename=$(echo "$id" | sed 's/ENT-/ent-/' | tr '[:upper:]' '[:lower:]' | tr '-' '_')
    
    cat > "$OUTPUT_DIR/${filename}.yml" << EOF
---
_meta:
  urn: urn:goreos:entity:$(echo "$tags" | cut -d',' -f1 | tr '[:upper:]' '[:lower:]'):$(echo "$id" | sed 's/ENT-//' | tr '[:upper:]' '[:lower:]' | tr '-' '_'):1.0.0
  type: Entity
  schema: urn:goreos:schema:entity:2.0.0
  origin: candidate_collision_resolved
id: $id
name: "$name"
tags: [$tags]
category: Master
attributes:
  - { name: id, type: UUID, key: true }
  # TODO: Definir atributos específicos
EOF
    echo "Generado: $filename.yml"
}

# Mantener ambos (con sufijos)
generate_entity "ENT-ACCIDENTE_LABORAL_BACK" "Accidente Laboral (Back)" "BACK"
generate_entity "ENT-ACCIDENTE_LABORAL" "Accidente Laboral" "ORG"
generate_entity "ENT-ACTA_CONSEJO" "Acta Consejo" "GOB"
generate_entity "ENT-ACTA_CORE" "Acta CORE" "GOV"
generate_entity "ENT-AUDIT_LOG_FINANCIERO" "Audit Log Financiero" "FIN"
generate_entity "ENT-AUDIT_LOG_TECNICO" "Audit Log Técnico" "TDE"
generate_entity "ENT-CHECKLIST_CIERRE_PROYECTO" "Checklist Cierre Proyecto" "EJE"
generate_entity "ENT-CHECKLIST_CIERRE_GENERICO" "Checklist Cierre Genérico" "SYS"
generate_entity "ENT-DASHBOARD_SISTEMA" "Dashboard Sistema" "SYS"
generate_entity "ENT-DASHBOARD_ANALITICO" "Dashboard Analítico" "TDE"
generate_entity "ENT-NOTIFICACION_SISTEMA" "Notificación Sistema" "SYS"
generate_entity "ENT-NOTIFICACION_USUARIO" "Notificación Usuario" "TDE"

# Fusionados (multi-tag)
generate_entity "ENT-CERTIFICADO_RECEPTOR_FONDOS" "Certificado Receptor Fondos" "EJEC,EJE"
generate_entity "ENT-DESCUENTO_LEGAL" "Descuento Legal" "BACK,FIN"
generate_entity "ENT-ESTRATEGIA_COMUNICACIONAL" "Estrategia Comunicacional" "BACK,PLAN"
generate_entity "ENT-FONDO_CONCURSABLE" "Fondo Concursable" "EJEC,SOC"
generate_entity "ENT-INDICADOR_GENERO" "Indicador Género" "PLAN,SOC"
generate_entity "ENT-LIQUIDACION_SUELDO" "Liquidación Sueldo" "BACK,FIN"
generate_entity "ENT-PLAN_CAPACITACION" "Plan Capacitación" "BACK,ORG"
generate_entity "ENT-PLAN_INDUCCION" "Plan Inducción" "BACK,ORG"
generate_entity "ENT-REMUNERACION" "Remuneración" "BACK,FIN"
generate_entity "ENT-RENTABILIDAD_SOCIAL" "Rentabilidad Social" "FIN"

echo ""
echo "=== Resumen ==="
echo "Colisiones resueltas: 16"
echo "Entidades generadas: 22 (6 pares + 10 fusionadas)"
