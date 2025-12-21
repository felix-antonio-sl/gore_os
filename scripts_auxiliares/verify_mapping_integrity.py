import yaml


def verify_bidirectional_mapping(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    stories = data.get("atomic_stories", [])
    bundles = data.get("capability_bundles", [])

    errors = []

    # 1. Check stories -> bundles
    for s in stories:
        b_id = s.get("capability_bundle_id")
        if not b_id:
            errors.append(f"Story {s['id']} missing capability_bundle_id")
            continue

        found = False
        for b in bundles:
            if b["id"] == b_id:
                if s["id"] not in b.get("associated_stories", []):
                    errors.append(
                        f"Story {s['id']} references bundle {b_id}, but bundle does not list story"
                    )
                found = True
                break
        if not found:
            errors.append(f"Story {s['id']} references non-existent bundle {b_id}")

    # 2. Check bundles -> stories
    for b in bundles:
        for s_id in b.get("associated_stories", []):
            found = False
            for s in stories:
                if s["id"] == s_id:
                    if s.get("capability_bundle_id") != b["id"]:
                        errors.append(
                            f"Bundle {b['id']} lists story {s_id}, but story references {s.get('capability_bundle_id')}"
                        )
                    found = True
                    break
            if not found:
                errors.append(f"Bundle {b['id']} lists non-existent story {s_id}")

    if not errors:
        print("✅ Bidirectional mapping is 100% consistent.")
    else:
        print(f"❌ Found {len(errors)} inconsistencies:")
        for err in errors[:10]:
            print(f"  - {err}")


if __name__ == "__main__":
    verify_bidirectional_mapping("historias_usuarios/historias_usuarios.yml")
