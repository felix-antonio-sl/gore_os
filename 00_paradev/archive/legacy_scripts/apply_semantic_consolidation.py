import yaml
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

FILE_SSOT = "historias_usuarios/historias_usuarios.yml"
FILE_INVENTORY = "inventario_roles_v9.yml"

# === SECTION 1: FALSE POSITIVES TO REVERT ===
# These were incorrectly mapped and should be treated as new roles
FALSE_POSITIVES = {
    "director_conaf": "director_corfo",  # CORFO ≠ CONAF
    "director_ind": "director_indap",  # INDAP ≠ IND
}

# === SECTION 2: CONSOLIDATION MAP ===
# Map from verbose/variant form to canonical form in inventory
CONSOLIDATION_MAP = {
    "gobernador_regional": "gobernador",
    "tesorero": "tesorero_regional",
    "funcionario_gore": "funcionario",
    "administrador_de_plataforma": "admin_plataforma",
    "administrador_ti": "admin_ti",
    "administrador_de_sistemas": "admin_ti",
    "administrador_sistema": "admin_ti",
    "sre": "ingeniero_sre",
    "devops": "desarrollador_devops",
    "jefe_gestión_personas": "jefe_rrhh",
    "jefe_de_división": "jefe_division",
    "encargado_servicios_generales": "encargado_servicios",
    "analista_de_seguimiento": "analista_seguimiento",
    "analista_de_convenios": "analista_convenios",
    "analista_de_inversión": "analista_inversion",
    "analista_de_evaluación": "analista_evaluacion",
    "analista_de_preinversión": "analista_preinversion",
    "analista_de_bienestar": "analista_bienestar",
    "analista_de_capacitación": "analista_capacitacion",
    "analista_de_tesorería": "analista_tesoreria",
    "analista_de_transporte": "analista_transporte",
    "analista_de_educación": "analista_educacion",
    "analista_de_honorarios": "analista_honorarios",
    "analista_de_inventario": "analista_inventario",
    "analista_de_modificaciones": "analista_modificaciones",
    "analista_de_observatorio": "analista_observatorio",
    "analista_de_pesca": "analista_pesca",
    "analista_de_presupuesto": "analista_presupuesto",
    "analista_de_remuneraciones": "analista_remuneraciones",
    "analista_de_transferencias": "analista_transferencias",
    "analista_planificación_territorial": "analista_planif_territorial",
    "analista_planificación": "analista_planificacion",
    "analista_prevención": "analista_prevencion",
    "analista_preinversión_dipir": "analista_preinversion",
    "analista_ppr_técnico": "analista_ppr_tecnico",
    "analista_8%_técnico": "analista_8_tecnico",
    "profesional_ñuble_250": "profesional_nuble_250",
    "profesional_de_apoyo_core": "profesional_apoyo_core",
    "jefe_de_auditoría": "jefe_auditoria",
    "líder_técnico": "lider_tecnico",
    "oficial_de_seguridad_(ciso)": "ciso",
    "coordinador_transformación_digital": "ctd_daf",
    "coordinador_transformación_digital_gore": "ctd_daf",
}


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=150)


def apply_consolidation():
    ssot = load_yaml(FILE_SSOT)
    inventory = load_yaml(FILE_INVENTORY)

    revert_count = 0
    consolidate_count = 0

    # 1. Apply to SSOT Stories
    for s in ssot.get("atomic_stories", []):
        role = s.get("role")
        if not role:
            continue

        # Revert false positives
        if role in FALSE_POSITIVES:
            s["role"] = FALSE_POSITIVES[role]
            revert_count += 1
        # Apply consolidation
        elif role in CONSOLIDATION_MAP:
            s["role"] = CONSOLIDATION_MAP[role]
            consolidate_count += 1

    # 2. Apply to Capability Bundles beneficiaries
    for b in ssot.get("capability_bundles", []):
        if not b.get("beneficiaries"):
            continue
        new_bens = set()
        for ben in b["beneficiaries"]:
            if ben in FALSE_POSITIVES:
                new_bens.add(FALSE_POSITIVES[ben])
            elif ben in CONSOLIDATION_MAP:
                new_bens.add(CONSOLIDATION_MAP[ben])
            else:
                new_bens.add(ben)
        b["beneficiaries"] = sorted(list(new_bens))

    # 3. Update Inventory: Remove the "Roles Descubiertos" unit and rebuild it
    # Filter out roles that are now consolidated
    consolidated_keys = set(CONSOLIDATION_MAP.keys())
    false_positive_values = set(FALSE_POSITIVES.values())  # These should be added

    # Find the "Roles Descubiertos" unit and filter it
    for unit in inventory.get("organization", []):
        if "Roles Descubiertos" in unit.get("unit", ""):
            filtered_roles = []
            for r in unit.get("roles", []):
                role_key = r.get("role_key")
                if role_key not in consolidated_keys:
                    filtered_roles.append(r)
            # Add the false positives as new entries
            for fp in false_positive_values:
                filtered_roles.append(
                    {
                        "id": f"USR-NEW-{fp.upper().replace('_', '-')[:10]}",
                        "title": fp.replace("_", " ").title(),
                        "role_key": fp,
                        "description": "Rol corregido (era falso positivo de fuzzy match).",
                    }
                )
            unit["roles"] = filtered_roles
            logging.info(
                f"Filtered 'Roles Descubiertos' unit: {len(filtered_roles)} roles remain."
            )
            break

    # Update manifests
    ssot["_manifest"]["semantic_consolidation"] = "Applied v2"
    ssot["_manifest"]["last_refactor"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    inventory["_manifest"]["semantic_consolidation"] = "Applied v2"

    save_yaml(ssot, FILE_SSOT)
    save_yaml(inventory, FILE_INVENTORY)

    logging.info(f"Reverted {revert_count} false positives.")
    logging.info(f"Consolidated {consolidate_count} synonym roles.")
    logging.info("Semantic consolidation complete.")


if __name__ == "__main__":
    apply_consolidation()
