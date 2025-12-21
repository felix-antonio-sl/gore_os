import yaml

ROLES_INVENTORY_PATH = "inventario_roles_v8.yml"
STORIES_SSOT_PATH = "historias_usuarios/historias_usuarios.yml"


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def extract_ssot_roles(data):
    """Extracts all unique roles from the SSOT stories and bundle beneficiaries."""
    story_roles = set()
    bundle_roles = set()

    for s in data.get("atomic_stories", []):
        if s.get("role"):
            story_roles.add(s["role"])

    for b in data.get("capability_bundles", []):
        for ben in b.get("beneficiaries") or []:
            bundle_roles.add(ben)

    return story_roles, bundle_roles


def main():
    inv_data = load_yaml(ROLES_INVENTORY_PATH)
    ssot_data = load_yaml(STORIES_SSOT_PATH)

    inventory_roles = extract_inventory_role_keys(inv_data)
    story_roles, bundle_roles = extract_ssot_roles(ssot_data)

    all_ssot_roles = story_roles.union(bundle_roles)

    # Analysis
    in_inventory_not_ssot = inventory_roles - all_ssot_roles
    in_ssot_not_inventory = all_ssot_roles - inventory_roles
    overlap = inventory_roles.intersection(all_ssot_roles)

    print("=" * 70)
    print("CROSS-ANALYSIS: inventario_roles_v8.yml vs historias_usuarios.yml")
    print("=" * 70)

    print(f"\n📊 INVENTORY (inventario_roles_v8.yml):")
    print(f"   - Total Unique Role Keys: {len(inventory_roles)}")

    print(f"\n📊 SSOT (historias_usuarios.yml):")
    print(f"   - Unique Roles in Stories: {len(story_roles)}")
    print(f"   - Unique Roles in Bundles (Beneficiaries): {len(bundle_roles)}")
    print(f"   - Total Unique Roles (Union): {len(all_ssot_roles)}")

    print(f"\n🔗 COVERAGE:")
    print(
        f"   - Roles in BOTH (Overlap): {len(overlap)} ({100*len(overlap)/len(all_ssot_roles):.1f}% of SSOT is in Inventory)"
    )
    print(f"   - In Inventory but NOT in SSOT: {len(in_inventory_not_ssot)}")
    print(f"   - In SSOT but NOT in Inventory: {len(in_ssot_not_inventory)}")

    if in_ssot_not_inventory:
        print(f"\n⚠️  SSOT roles missing from Inventory (Top 15):")
        for r in sorted(in_ssot_not_inventory)[:15]:
            print(f"     - {r}")
        if len(in_ssot_not_inventory) > 15:
            print(f"     ... and {len(in_ssot_not_inventory)-15} more.")

    if in_inventory_not_ssot:
        print(f"\n📉 Inventory roles NOT used in SSOT (Top 15):")
        for r in sorted(in_inventory_not_ssot)[:15]:
            print(f"     - {r}")
        if len(in_inventory_not_ssot) > 15:
            print(f"     ... and {len(in_inventory_not_ssot)-15} more.")


if __name__ == "__main__":
    main()
