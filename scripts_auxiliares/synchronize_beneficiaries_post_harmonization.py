import yaml
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

FILE_PATH = "historias_usuarios/historias_usuarios.yml"


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=150)


def synchronize_beneficiaries():
    data = load_yaml(FILE_PATH)
    stories = data.get("atomic_stories", [])
    bundles = data.get("capability_bundles", [])

    # Map Bundle ID -> Set of Roles from its Associated Stories
    bundle_roles_map = {}

    # 1. Build the map from stories
    story_map = {s["id"]: s for s in stories}

    for b in bundles:
        b_id = b["id"]
        associated_ids = b.get("associated_stories", [])

        roles_in_stories = set()
        for s_id in associated_ids:
            story = story_map.get(s_id)
            if story and story.get("role"):
                roles_in_stories.add(story["role"])

        bundle_roles_map[b_id] = roles_in_stories

    # 2. Update Bundles
    updates_count = 0
    total_roles_removed = 0
    total_roles_added = 0

    for b in bundles:
        b_id = b["id"]
        derived_roles = bundle_roles_map.get(b_id, set())

        current_beneficiaries = set(b.get("beneficiaries") or [])

        # Determine exact set:
        # Strategy: Strict Synchronization?
        # The user asked to "ensure beneficiaries are updated".
        # Usually, beneficiaries should be exactly the roles in the stories + potentially some excessive ones if they are future placeholders?
        # Given strict SSOT nature, strictly syncing to used roles is cleaner for consistency.
        # However, let's keep it safe: We definitely ADD missing derived roles.
        # Should we REMOVE roles that are no longer in stories?
        # Yes, because if we renamed 'analista_x' to 'analista_y', 'analista_x' should theoretically disappear from beneficiaries.

        if derived_roles != current_beneficiaries:
            # Calculate diffs for logging
            added = derived_roles - current_beneficiaries
            removed = current_beneficiaries - derived_roles

            if added or removed:
                b["beneficiaries"] = sorted(list(derived_roles))
                updates_count += 1
                total_roles_added += len(added)
                total_roles_removed += len(removed)
                if added:
                    logging.info(f"Bundle {b_id}: Added {added}")
                if removed:
                    logging.info(f"Bundle {b_id}: Removed {removed}")

    logging.info(f" beneficialries sync finished.")
    logging.info(f"Bundles updated: {updates_count}")
    logging.info(f"Total Roles Added: {total_roles_added}")
    logging.info(f"Total Roles Pruned (Post-Harmonization): {total_roles_removed}")

    # Update Manifest
    data["_manifest"]["beneficiary_synchronization"] = "Strict Sync Applied"

    save_yaml(data, FILE_PATH)


if __name__ == "__main__":
    synchronize_beneficiaries()
