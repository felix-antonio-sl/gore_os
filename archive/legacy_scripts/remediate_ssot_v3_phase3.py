import yaml
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("remediation_phase3_log.txt"),
        logging.StreamHandler(),
    ],
)

SOURCE_FILE = "historias_usuarios_v3.yml"
OUTPUT_FILE = "historias_usuarios_v3.yml"  # Overwrite

# Specific ID repairs based on manual analysis
ID_REPAIRS = {
    ("US-BOD-001-01", "D-FIN"): "US-BOD-002-01",
    ("US-COMP-001-01", "D-BACK"): "US-COMPT-001-01",  # Competencias vs Compras
    (
        "US-APT-001-01",
        "D-NORM",
    ): "US-NORM-ATT-001",  # Apoyo Tecnico Transparencia vs Analista Planif. Terr.
    ("US-DEV-001-01", "D-TDE"): "US-TDE-DEV-001",
    ("US-QA-001-01", "D-TDE"): "US-TDE-QA-001",
}


def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=120)


def match_role_to_bundle(role, story_text, bundles):
    """
    Heuristic to assign a role to the best fitting bundle within the domain.
    """
    best_bundle = None
    max_score = 0

    for bundle in bundles:
        score = 0
        b_text = (
            bundle.get("capability", "") + " " + bundle.get("description", "")
        ).lower()
        s_text = story_text.lower()
        r_text = role.lower()

        # Simple word intersection score
        b_words = set(b_text.split())
        s_words = set(s_text.split())
        r_words = set(r_text.split())

        score += len(b_words.intersection(s_words))
        score += (
            len(b_words.intersection(r_words)) * 2
        )  # Role match in bundle desc is strong

        if score > max_score:
            max_score = score
            best_bundle = bundle

    return best_bundle


def remediate_phase3():
    logging.info("Starting Phase 3 Remediation...")

    data = load_yaml(SOURCE_FILE)
    stories = data.get("atomic_stories", [])
    bundles = data.get("capability_bundles", [])

    # 1. Fix Duplicate IDs
    logging.info("--- Fixing Duplicate IDs ---")

    # Create a lookup for duplicates to target specific occurrences
    # We iterate and apply fixes if (id, domain) matches our target pairs

    changed_ids = 0
    for story in stories:
        key = (story["id"], story.get("domain"))
        if key in ID_REPAIRS:
            new_id = ID_REPAIRS[key]
            logging.info(f"Renaming {story['id']} in {story['domain']} to {new_id}")
            story["id"] = new_id
            changed_ids += 1

    logging.info(f"Fixed {changed_ids} duplicate IDs.")

    # 2. Fix Role Gaps in Bundles
    logging.info("--- Fixing Role Gaps in Bundles ---")

    # Group bundles by domain
    bundles_by_domain = {}
    for b in bundles:
        d = b.get("domain")
        if d not in bundles_by_domain:
            bundles_by_domain[d] = []
        bundles_by_domain[d].append(b)

    # Track roles added
    roles_added_count = 0

    for story in stories:
        domain = story.get("domain")
        role = story.get("role")
        i_want = story.get("i_want", "")

        if not domain or not role:
            continue

        domain_bundles = bundles_by_domain.get(domain)
        if not domain_bundles:
            # Should look for "generic" bundle or skip
            logging.warning(
                f"No bundles found for domain {domain}, skipping role {role}"
            )
            continue

        # Check if role is present in ANY of the domain bundles
        found = False
        for b in domain_bundles:
            if role in (b.get("beneficiaries") or []):
                found = True
                break

        if not found:
            # Assign to best bundle
            target_bundle = match_role_to_bundle(role, i_want, domain_bundles)
            if not target_bundle:
                target_bundle = domain_bundles[0]  # Fallback to first

            if (
                "beneficiaries" not in target_bundle
                or target_bundle["beneficiaries"] is None
            ):
                target_bundle["beneficiaries"] = []

            if role not in target_bundle["beneficiaries"]:
                target_bundle["beneficiaries"].append(role)
                # Sort for tidiness
                target_bundle["beneficiaries"].sort()
                roles_added_count += 1
                logging.info(
                    f"Added role '{role}' to bundle '{target_bundle['id']}' in {domain}"
                )

    logging.info(f"Added {roles_added_count} missing roles to bundles.")

    # Update Manifest
    data["remediation_phase3_date"] = datetime.now().strftime("%Y-%m-%d")
    data["_manifest"][
        "remediation_phase3"
    ] = "Completed duplicate fixes and role synchronization"

    save_yaml(data, OUTPUT_FILE)
    logging.info("Phase 3 Remediation Complete.")


if __name__ == "__main__":
    remediate_phase3()
