import os
import glob
import re

MODEL_DIR = "model"
ROLE_DIR = os.path.join(MODEL_DIR, "roles")
STORY_DIR = os.path.join(MODEL_DIR, "stories")
ENTITY_DIR = os.path.join(MODEL_DIR, "entities")
PROCESS_DIR = os.path.join(MODEL_DIR, "processes")


def extract_id(content):
    match = re.search(r"^id:\s*[\"']?([^\"'\\n]+)[\"']?", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_field(content, field):
    match = re.search(
        f"^\\s*{field}:\\s*[\"']?([^\"'\\n]+)[\"']?", content, re.MULTILINE
    )
    return match.group(1).strip() if match else None


def verify_phase2():
    print("=== PHASE 2 VERIFICATION (DEBUG ENTITIES) ===\n")
    role_ids = set()
    role_files = glob.glob(os.path.join(ROLE_DIR, "**/*.yml"), recursive=True)
    for f in role_files:
        with open(f, "r") as file:
            content = file.read()
        rid = extract_id(content)
        if rid:
            role_ids.add(rid)

    story_files = glob.glob(os.path.join(STORY_DIR, "*.yml"))

    entity_ids = set()
    for f in glob.glob(os.path.join(ENTITY_DIR, "**/*.yml"), recursive=True):
        with open(f, "r") as file:
            content = file.read()
        eid = extract_id(content)
        if eid:
            entity_ids.add(eid)

    missing_entities = set()
    broken_roles = set()

    print(f"Known Entities: {len(entity_ids)}")
    print(f"Known Roles: {len(role_ids)}")

    for f in story_files:
        with open(f, "r") as file:
            content = file.read()

        s_rid = extract_field(content, "role_id")
        if s_rid and s_rid not in role_ids:
            broken_roles.add(s_rid)

        mentions = re.findall(r"-\s+id:\s*([A-Za-z0-9\-_]+)", content)
        for mid in mentions:
            if mid not in entity_ids:
                missing_entities.add(mid)

    print(f"\nMissing Unique Entities: {len(missing_entities)}")
    print(f"Broken Role Refs (Unique): {len(broken_roles)}")

    if len(missing_entities) > 0:
        print("\nTop 50 Missing Entities:")
        for e in sorted(list(missing_entities))[:50]:
            print(f"- {e}")

    if len(broken_roles) > 0:
        print("\nBroken Roles:")
        for r in sorted(list(broken_roles)):
            print(f"- {r}")


if __name__ == "__main__":
    verify_phase2()
