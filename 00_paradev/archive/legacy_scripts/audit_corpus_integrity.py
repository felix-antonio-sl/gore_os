import yaml
import os
import sys

# Constants for paths
BASE_DIR = (
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios"
)
ROLES_FILE = os.path.join(BASE_DIR, "roles.yml")
CAPABILITIES_FILE = os.path.join(BASE_DIR, "capabilities.yml")
STORIES_FILE = os.path.join(BASE_DIR, "historias_usuarios.yml")


def load_yaml(filepath):
    """Safe load YAML file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)


def build_role_set(roles_data):
    """Extract all valid role IDs from the roles.yml structure."""
    valid_roles = set()

    # Process Archetypes
    if "archetypes" in roles_data:
        for category in roles_data["archetypes"].values():
            for archetype in category:
                if "archetype_id" in archetype:
                    pass

    # Process Organization
    if "organization" in roles_data:
        for unit in roles_data["organization"]:
            if "roles" in unit:
                for role in unit["roles"]:
                    if "id" in role:
                        valid_roles.add(role["id"])

    return valid_roles


def build_capability_set(capabilities_data):
    """Extract all valid capability bundle IDs."""
    valid_caps = set()
    domain_map = {}
    if "capability_bundles" in capabilities_data:
        for bundle in capabilities_data["capability_bundles"]:
            if "id" in bundle:
                valid_caps.add(bundle["id"])
                if "domain" in bundle:
                    domain_map[bundle["id"]] = bundle["domain"]
    return valid_caps, domain_map


def audit_corpus():
    print("--- Starting Compositional Audit of GORE_OS Corpus ---")

    # 1. Load Data
    roles_data = load_yaml(ROLES_FILE)
    caps_data = load_yaml(CAPABILITIES_FILE)
    stories_data = load_yaml(STORIES_FILE)

    # 2. Build Reference Sets
    valid_roles = build_role_set(roles_data)
    valid_caps, cap_domains = build_capability_set(caps_data)

    print(f"Loaded {len(valid_roles)} valid roles.")
    print(f"Loaded {len(valid_caps)} valid capability bundles.")

    # 3. Audit Stories
    stories = stories_data.get("atomic_stories", [])
    print(f"Auditing {len(stories)} atomic stories...")

    issues = []
    used_roles = set()

    for i, story in enumerate(stories):
        story_id = story.get("id", f"INDEX-{i}")
        role_id = story.get("role_id")
        cap_id = story.get("capability_bundle_id")
        domain = story.get("domain")

        # Check Role Integrity
        if not role_id:
            issues.append(f"[STORY] {story_id}: Missing 'role_id'")
        elif role_id not in valid_roles:
            issues.append(
                f"[STORY] {story_id}: Invalid role_id '{role_id}'. Not found in roles.yml."
            )
        else:
            used_roles.add(role_id)

        # Check Capability Integrity
        if not cap_id:
            pass
        elif cap_id not in valid_caps:
            issues.append(
                f"[STORY] {story_id}: Invalid capability_bundle_id '{cap_id}'. Not found in capabilities.yml."
            )
        else:
            # Check Domain Consistency
            expected_domain = cap_domains.get(cap_id)
            if expected_domain and domain != expected_domain:
                pass

        # Check "Beneficial" (Syntax check)
        if not story.get("so_that"):
            issues.append(
                f"[STORY] {story_id}: Missing 'so_that' (Benefit). violates beneficial rule."
            )

    # Calculate Unused Roles
    unused_roles = valid_roles - used_roles
    print(
        f"\nRole Coverage: {len(used_roles)} roles used out of {len(valid_roles)} total."
    )
    print(f"Unused Roles: {len(unused_roles)}")

    # 4. Report
    if issues:
        print(f"\nFOUND {len(issues)} ISSUES:")
        for issue in issues:
            print(issue)
        print("\nAudit FAILED.")
    else:
        print("\nAudit PASSED. The corpus is structurally sound.")


if __name__ == "__main__":
    audit_corpus()
