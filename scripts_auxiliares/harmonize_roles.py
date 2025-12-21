import yaml
import logging
from difflib import SequenceMatcher

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

ROLES_INVENTORY_PATH = "inventario_roles_v8.yml"
STORIES_SSOT_PATH = "historias_usuarios/historias_usuarios.yml"


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=150)


def extract_inventory_role_keys(data):
    """Extracts all role_key and role_key_alias from the inventory."""
    keys = set()

    # From archetypes (external)
    for arch in data.get("archetypes", {}).get("external", []):
        for inst in arch.get("instances", []):
            if inst.get("role_key_alias"):
                keys.add(inst["role_key_alias"])

    # From archetypes (municipal)
    for arch in data.get("archetypes", {}).get("municipal", []):
        for role in arch.get("member_roles", []):
            keys.add(role)

    # From internal_bases
    for base in data.get("archetypes", {}).get("internal_bases", []):
        for inh in base.get("inheritors", []):
            if inh.get("role_key_alias"):
                keys.add(inh["role_key_alias"])

    # From organization
    for unit in data.get("organization", []):
        for role_entry in unit.get("roles", []):
            if role_entry.get("role_key"):
                keys.add(role_entry["role_key"])

    # From direct_roles (if exists)
    for role_entry in data.get("direct_roles", []):
        if isinstance(role_entry, dict) and role_entry.get("role_key"):
            keys.add(role_entry["role_key"])

    return keys


def normalize_key(s):
    """Normalizes a role key for fuzzy matching."""
    s = s.lower()
    # Remove common prepositions and articles
    s = s.replace("de_", "_").replace("_de_", "_").replace("del_", "_")
    s = s.replace("la_", "_").replace("el_", "_")
    s = s.replace("(", "").replace(")", "").replace("/", "_")
    # Collapse multiple underscores
    while "__" in s:
        s = s.replace("__", "_")
    s = s.strip("_")
    return s


def build_canonical_map(inventory_roles, ssot_roles):
    """
    Builds a map from SSOT roles to Inventory canonical roles.
    Uses fuzzy matching when exact match is not found.
    """
    canonical_map = {}
    inv_normalized = {normalize_key(r): r for r in inventory_roles}

    for ssot_role in ssot_roles:
        # 1. Exact match
        if ssot_role in inventory_roles:
            canonical_map[ssot_role] = ssot_role
            continue

        # 2. Normalized match
        ssot_norm = normalize_key(ssot_role)
        if ssot_norm in inv_normalized:
            canonical_map[ssot_role] = inv_normalized[ssot_norm]
            continue

        # 3. Fuzzy match (best similarity > 0.85)
        best_match = None
        best_score = 0
        for inv_role in inventory_roles:
            score = SequenceMatcher(None, ssot_norm, normalize_key(inv_role)).ratio()
            if score > best_score and score >= 0.85:
                best_score = score
                best_match = inv_role

        if best_match:
            canonical_map[ssot_role] = best_match
        else:
            # No match found - keep as is or flag for manual review
            canonical_map[ssot_role] = ssot_role  # Keep original if no match

    return canonical_map


def apply_normalization(ssot_data, canonical_map):
    """Applies the canonical map to stories and bundles."""
    changes = 0

    # Stories
    for s in ssot_data.get("atomic_stories", []):
        role = s.get("role")
        if role and role in canonical_map and canonical_map[role] != role:
            s["role"] = canonical_map[role]
            changes += 1

    # Bundles - beneficiaries
    for b in ssot_data.get("capability_bundles", []):
        if b.get("beneficiaries"):
            new_bens = set()
            for ben in b["beneficiaries"]:
                if ben in canonical_map:
                    new_bens.add(canonical_map[ben])
                else:
                    new_bens.add(ben)
            b["beneficiaries"] = sorted(list(new_bens))

    return changes


def main():
    inv_data = load_yaml(ROLES_INVENTORY_PATH)
    ssot_data = load_yaml(STORIES_SSOT_PATH)

    inventory_roles = extract_inventory_role_keys(inv_data)

    # Get all SSOT roles
    ssot_roles = set()
    for s in ssot_data.get("atomic_stories", []):
        if s.get("role"):
            ssot_roles.add(s["role"])
    for b in ssot_data.get("capability_bundles", []):
        for ben in b.get("beneficiaries") or []:
            ssot_roles.add(ben)

    logging.info(f"Inventory has {len(inventory_roles)} canonical roles.")
    logging.info(f"SSOT has {len(ssot_roles)} unique roles.")

    canonical_map = build_canonical_map(inventory_roles, ssot_roles)

    # Report changes
    to_change = {k: v for k, v in canonical_map.items() if k != v}
    logging.info(f"Roles to normalize: {len(to_change)}")

    for old, new in sorted(to_change.items())[:20]:
        logging.info(f"  '{old}' -> '{new}'")
    if len(to_change) > 20:
        logging.info(f"  ... and {len(to_change) - 20} more.")

    changes = apply_normalization(ssot_data, canonical_map)
    logging.info(f"Applied {changes} role normalizations to stories.")

    # Update manifest
    ssot_data["_manifest"]["role_harmonization"] = "Phase 18 Applied"
    ssot_data["_manifest"]["canonical_source"] = "inventario_roles_v8.yml"

    save_yaml(ssot_data, STORIES_SSOT_PATH)
    logging.info("SSOT saved with harmonized terminology.")


if __name__ == "__main__":
    main()
