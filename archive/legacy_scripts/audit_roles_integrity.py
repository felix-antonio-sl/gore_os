import yaml
import difflib
from collections import defaultdict

FILE_PATH = "historias_usuarios/historias_usuarios.yml"


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def audit_roles():
    data = load_yaml(FILE_PATH)
    stories = data.get("atomic_stories", [])
    bundles = data.get("capability_bundles", [])

    # helper map
    bundle_map = {b["id"]: set(b.get("beneficiaries") or []) for b in bundles}
    bundle_name_map = {b["id"]: b.get("capability") for b in bundles}

    # 1. Check strict inclusion (Story Role in Bundle Beneficiaries)
    missing_in_bundle = []

    # 2. Collect all roles for normalization check
    all_story_roles = set()
    all_beneficiaries = set()

    for b in bundles:
        if b.get("beneficiaries"):
            for ben in b["beneficiaries"]:
                all_beneficiaries.add(ben)

    for s in stories:
        role = s.get("role")
        if not role:
            print(f"❌ Story {s['id']} has NO ROLE")
            continue

        all_story_roles.add(role)

        b_id = s.get("capability_bundle_id")
        if not b_id:
            print(f"❌ Story {s['id']} has no capability_bundle_id")
            continue

        if b_id in bundle_map:
            if role not in bundle_map[b_id]:
                missing_in_bundle.append(
                    f"Story {s['id']} role '{role}' NOT in bundle {b_id} beneficiaries"
                )
        else:
            print(f"❌ Bundle {b_id} not found for story {s['id']}")

    # 3. Analyze potential synonyms / normalization issues
    # We combine all roles seen anywhere
    all_roles = list(all_story_roles.union(all_beneficiaries))
    all_roles.sort()

    possible_duplicates = []
    seen = set()

    # Simple strategy: Normalized string comparison
    normalized_map = defaultdict(list)
    for r in all_roles:
        # removal of "de ", "el ", "la " and underscores
        norm = (
            r.lower()
            .replace("_", " ")
            .replace("de ", "")
            .replace("del ", "")
            .replace("la ", "")
            .strip()
        )
        normalized_map[norm].append(r)

    for norm, variants in normalized_map.items():
        if len(variants) > 1:
            possible_duplicates.append(f"Variants for '{norm}': {variants}")

    print("=" * 60)
    print("AUDIT REPORT: ROLES & BENEFICIARIES")
    print("=" * 60)

    print(
        f"\n1. Inconsistencies (Story Role not in Bundle Beneficiaries): {len(missing_in_bundle)}"
    )
    for m in missing_in_bundle[:10]:
        print(f"  - {m}")
    if len(missing_in_bundle) > 10:
        print(f"  ... and {len(missing_in_bundle)-10} more.")

    print(f"\n2. Total Unique Roles matched: {len(all_story_roles)}")
    print(f"3. Potential Normalization Issues (Synonyms?): {len(possible_duplicates)}")
    for d in possible_duplicates:
        print(f"  ⚠️  {d}")


if __name__ == "__main__":
    audit_roles()
