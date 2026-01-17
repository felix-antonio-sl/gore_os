import yaml
import os

# Paths
PROCESS_TXT = (
    "/Users/felixsanhueza/Developer/goreos/model/processes/_procesos_extraidos_us.txt"
)
PROCESS_YML = (
    "/Users/felixsanhueza/Developer/goreos/model/processes/catalog_processes_goreos.yml"
)
ENTITY_YML = (
    "/Users/felixsanhueza/Developer/goreos/model/entities/catalog_entities_goreos.yml"
)
ENTITY_YML_NEW = "/Users/felixsanhueza/Developer/goreos/model/entities/catalog_entities_goreos_improved.yml"


def verify_processes():
    print("--- Verifying Processes ---")
    with open(PROCESS_TXT, "r") as f:
        raw_processes = set(line.strip() for line in f if line.strip())

    try:
        with open(PROCESS_YML, "r") as f:
            proc_catalog = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading process catalog: {e}")
        return

    catalog_ids = set()
    if "processes" in proc_catalog:  # Flat structure?
        # Check structure, looking at file it has domains D-FIN, etc.
        pass

    # Iterate domains
    for key, value in proc_catalog.items():
        if key.startswith("D-") and "processes" in value:
            for p in value["processes"]:
                catalog_ids.add(p["id"])

    missing = raw_processes - catalog_ids
    if missing:
        print(f"WARNING: {len(missing)} processes missing from catalog:")
        for m in missing:
            print(f" - {m}")
    else:
        print("SUCCESS: All extracted processes are present in the catalog.")


def improve_entities():
    print("\n--- Improving Entities ---")
    try:
        with open(ENTITY_YML, "r") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading entity catalog: {e}")
        return

    count = 0
    if "domains" in data:
        for domain_key, domain_data in data["domains"].items():
            if "entities" in domain_data:
                for entity in domain_data["entities"]:
                    # Add label if missing
                    if "label" not in entity:
                        # Logic: Title Case, replace - with space
                        name_slug = entity.get("name", "")
                        label = name_slug.replace("-", " ").title()

                        # Custom fixups for common acronyms
                        # You can add more complex logic here if needed

                        # Insert label after name (conceptually, dict order matters in py 3.7+)
                        # We reconstruct the dict to control order
                        new_entity = {}
                        new_entity["id"] = entity.get("id")
                        new_entity["name"] = entity.get("name")
                        new_entity["label"] = label
                        new_entity["description"] = entity.get("description")
                        new_entity["type"] = entity.get("type")

                        # Copy any other keys
                        for k, v in entity.items():
                            if k not in new_entity:
                                new_entity[k] = v

                        # Update the list item in place (hacky but works for list of dicts)
                        entity.clear()
                        entity.update(new_entity)
                        count += 1

    print(f"Updated {count} entities with labels.")

    with open(ENTITY_YML_NEW, "w") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=1000)
    print(f"Saved improved catalog to {ENTITY_YML_NEW}")


if __name__ == "__main__":
    verify_processes()
    improve_entities()
