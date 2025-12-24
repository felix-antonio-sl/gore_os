import os
import glob
import re

STORY_DIR = "model/stories"
ENTITY_DIR = "model/entities"
AUTO_GEN_DIR = os.path.join(ENTITY_DIR, "auto_generated")

TEMPLATE = """_meta:
  urn: urn:goreos:atom:entity:{id_slug}:1.0.0
  type: Entity
  schema: urn:goreos:schema:entity:2.0.0

id: {id}
name: {name}
description: Entidad identificada desde Historias de Usuario (Auto-generada)
type: DIGITAL # Default
domain: {domain}

fields:
  - name: id
    type: UUID
    required: true

relationships: []

verification:
  status: draft
  source_story: {story_source}
"""


def extract_id(content):
    match = re.search(r"^id:\s*[\"']?([^\"'\\n]+)[\"']?", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def slugify(text):
    return text.lower().replace("-", "_")


def infer_domain(eid):
    # ENT-FIN-XYZ -> D-FIN
    parts = eid.split("-")
    if len(parts) > 2:
        return f"D-{parts[1]}"
    return "D-GENERIC"


def infer_name(eid):
    # ENT-FIN-BALANCE-ANUAL -> Balance Anual
    parts = eid.split("-")
    if len(parts) > 2:
        return " ".join([p.capitalize() for p in parts[2:]])
    return eid


def generate_entities():
    print("Scanning for missing entities...")

    # 1. Index existing entities
    existing_ids = set()
    files = glob.glob(os.path.join(ENTITY_DIR, "**/*.yml"), recursive=True)
    for f in files:
        with open(f, "r") as file:
            content = file.read()
        eid = extract_id(content)
        if eid:
            existing_ids.add(eid)

    print(f"Index: {len(existing_ids)} existing entities.")

    if not os.path.exists(AUTO_GEN_DIR):
        os.makedirs(AUTO_GEN_DIR)

    # 2. Find missing from stories
    missing_map = {}  # ID -> Source Story
    story_files = glob.glob(os.path.join(STORY_DIR, "*.yml"))

    for f in story_files:
        with open(f, "r") as file:
            content = file.read()

        mentions = re.findall(r"-\s+id:\s*([A-Za-z0-9\-_]+)", content)
        for mid in mentions:
            if mid not in existing_ids:
                if mid not in missing_map:
                    missing_map[mid] = os.path.basename(f)

    print(f"Found {len(missing_map)} missing entities.")

    # 3. Generate
    generated_count = 0
    for eid, source in missing_map.items():
        fname = f"{slugify(eid)}.yml"
        fpath = os.path.join(AUTO_GEN_DIR, fname)

        content = TEMPLATE.format(
            id=eid,
            id_slug=slugify(eid),
            name=infer_name(eid),
            domain=infer_domain(eid),
            story_source=source,
        )

        with open(fpath, "w") as f:
            f.write(content)
        generated_count += 1

    print(f"Generated {generated_count} files in {AUTO_GEN_DIR}")


if __name__ == "__main__":
    generate_entities()
