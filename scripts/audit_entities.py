import os
import glob
import re
from collections import defaultdict

# CORRECTED PATH
ENTITIES_DIR = "/Users/felixsanhueza/fx_felixiando/gore_os/model/entities"


def parse_yaml_entity(content):
    entity = {}
    id_match = re.search(r"^id:\s*([A-Z0-9_-]+)", content, re.MULTILINE)
    if id_match:
        entity["id"] = id_match.group(1).strip()

    attrs = []
    attr_section_match = re.search(r"attributes:(.*)", content, re.DOTALL)
    if attr_section_match:
        attr_section = attr_section_match.group(1)
        attr_matches = re.finditer(r"-\s*\{(.*?)\}", attr_section, re.DOTALL)
        for match in attr_matches:
            attr_str = match.group(1)
            attr = {}
            parts = attr_str.split(",")
            for part in parts:
                if ":" in part:
                    k, v = part.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip("\"'")
                    attr[k] = v
            if "name" in attr:
                attrs.append(attr)

    entity["attributes"] = attrs
    return entity


def load_entities():
    if not os.path.isdir(ENTITIES_DIR):
        print(f"ERROR: Directory {ENTITIES_DIR} does not exist!")
        return {}
    files = glob.glob(os.path.join(ENTITIES_DIR, "*.yml"))
    print(f"DEBUG: Found {len(files)} files in {ENTITIES_DIR}")

    entities = {}
    for f in files:
        try:
            with open(f, "r") as stream:
                content = stream.read()
                data = parse_yaml_entity(content)
                if "id" in data:
                    entities[data["id"]] = {"file": f, "attributes": data["attributes"]}
        except Exception as e:
            print(f"Error loading {f}: {e}")
    return entities


def audit_entities(entities):
    errors = []
    entity_ids = set(entities.keys())

    # Whitelist
    entity_ids.add("ENT-SYS-ACTOR")
    entity_ids.add("ENT-SYS-DOCUMENTO")
    entity_ids.add("ENT-SYS-ENTIDAD")

    for ent_id, info in entities.items():
        for attr in info["attributes"]:
            # Check FK
            if "fk" in attr:
                target = attr["fk"].strip()
                if target and " " in target:
                    target = target.split(" ")[0]
                if target not in entity_ids:
                    errors.append(f"[FK_ERROR] {ent_id}.{attr['name']} -> {target}")

            # Check Types
            t = attr.get("type", "Unknown")
            if t not in [
                "UUID",
                "String",
                "Integer",
                "Decimal",
                "Date",
                "DateTime",
                "Boolean",
                "JSON",
                "Text",
            ]:
                errors.append(
                    f"[TYPE_WARN] {ent_id}.{attr['name']} has non-standard type '{t}'"
                )

            # Check Naming (snake_case)
            if not re.match(r"^[a-z_][a-z0-9_]*$", attr["name"]):
                errors.append(
                    f"[NAMING_WARN] {ent_id}.{attr['name']} is not snake_case"
                )

            # Check Doc for JSON
            if t == "JSON" and "description" not in attr:
                errors.append(
                    f"[DOC_WARN] {ent_id}.{attr['name']} (JSON) missing description"
                )

    return errors


if __name__ == "__main__":
    entities = load_entities()
    if not entities:
        exit(1)

    print(f"Loaded {len(entities)} parsed entities.")
    errors = audit_entities(entities)

    if errors:
        print("\n=== AUDIT FINDINGS ===")
        seen = set()
        for err in sorted(errors):
            if err not in seen:
                print(err)
                seen.add(err)
    else:
        print("\n=== NO ISSUES FOUND ===")
