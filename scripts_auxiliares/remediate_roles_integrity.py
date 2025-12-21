import yaml
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

FILE_PATH = "historias_usuarios/historias_usuarios.yml"

# Canonical Role Mappings (based on audit)
# Target: Shortest/Cleanest Canonical Form
ROLE_NORMALIZATION = {
    "custodio_evidencia": "custodio_de_evidencia",  # Standardize on 'de' for consistency if chosen, or simpler? Let's pick ONE. 'custodio_de_evidencia' seems more formal.
    "encargado_abastecimiento": "encargado_de_abastecimiento",
    "encargado_bodega": "encargado_de_bodega",
    "encargado_comunicaciones": "encargado_de_comunicaciones",
    "encargado_control_gestión": "encargado_de_control_de_gestión",  # Or simpler? Let's use longest for clarity or shortest? existing seems mixed. Let's standarize on 'encargado_de_X'
    "encargado_rendiciones": "encargado_de_rendiciones",
    "encargado_transparencia": "encargado_de_transparencia",
    "monitor_sistema": "monitor_de_sistema",
    "operador_sistema": "operador_de_sistema",
}

# Also need to fix 'encargado_oficina_de_partes' vs 'oficial_de_partes'?
# The audit showed 'oficial_de_partes_/_oficial_de_partes' which is ugly.


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=150)


def remediate_roles():
    data = load_yaml(FILE_PATH)
    stories = data.get("atomic_stories", [])
    bundles = data.get("capability_bundles", [])

    # 1. Normalize Roles in Stories
    normalized_count = 0
    for s in stories:
        role = s.get("role")
        if role in ROLE_NORMALIZATION:
            s["role"] = ROLE_NORMALIZATION[role]
            normalized_count += 1

    # 2. Normalize Roles in Bundle Beneficiaries
    # We must be careful to remove duplicates after normalization
    for b in bundles:
        if not b.get("beneficiaries"):
            continue
        new_beneficiaries = set()
        for ben in b["beneficiaries"]:
            if ben in ROLE_NORMALIZATION:
                new_beneficiaries.add(ROLE_NORMALIZATION[ben])
            else:
                new_beneficiaries.add(ben)
        b["beneficiaries"] = sorted(list(new_beneficiaries))

    logging.info(f"Normalized {normalized_count} roles in stories.")

    # 3. Synchronize: Ensure strict inclusion
    # We loop via stories again
    synced_count = 0

    # helper to find bundle by ID
    bundle_dict = {b["id"]: b for b in bundles}

    for s in stories:
        b_id = s.get("capability_bundle_id")
        role = s.get("role")

        if not b_id or not role:
            continue

        target_bundle = bundle_dict.get(b_id)
        if target_bundle:
            current_bens = set(target_bundle.get("beneficiaries") or [])
            if role not in current_bens:
                current_bens.add(role)
                target_bundle["beneficiaries"] = sorted(list(current_bens))
                synced_count += 1

    logging.info(
        f"Synchronized {synced_count} missing roles into bundle beneficiaries."
    )

    # Update Manifest
    data["_manifest"]["role_integrity_audit"] = "Completed"

    save_yaml(data, FILE_PATH)
    logging.info("Role remediation completed.")


if __name__ == "__main__":
    remediate_roles()
