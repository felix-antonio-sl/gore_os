import json
import os
import re

# Categorías de Dominios GORE_OS
DOMAINS = {
    "FIN": "D-FIN",
    "NORM": "D-NORM",
    "EJEC": "D-EJEC",
    "EJE": "D-EJEC",
    "PLAN": "D-PLAN",
    "TDE": "D-TDE",
    "TERR": "D-TERR",
    "SEG": "D-SEG",
    "SOC": "DIDESO",
    "GOV": "D-GOB",
    "GOB": "D-GOB",
    "BACK": "D-BACK",
    "DEV": "D-EVOL",
    "ORG": "D-GESTION",
    "OPS": "D-OPS",
    "FENIX": "FENIX",
}


def clean_name(name):
    name = name.replace("P1", "Proceso 1")
    name = name.replace("-", " ").title()
    return name


def systematize():
    base_path = "/Users/felixsanhueza/Developer/goreos/model/processes"
    stories_path = "/Users/felixsanhueza/Developer/goreos/model/stories"

    index_file = os.path.join(base_path, "_index.yml")
    ref_file = os.path.join(stories_path, "_us_process_ref_ids_extracted.txt")
    output_file = os.path.join(base_path, "catalog_processes_goreos.json")

    catalog = {}

    # 1. Parsear _index.yml manualmente (sin yaml)
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            content = f.read()
            # Simple regex to extract id, name, domain
            items = re.findall(
                r"- id: ([^\n]+)\n\s+urn: ([^\n]+)\n\s+name: \"([^\"]+)\"\n\s+domain: ([^\n]+)",
                content,
            )
            for proc_id, urn, name, domain in items:
                catalog[proc_id.strip()] = {
                    "id": proc_id.strip(),
                    "name": name.strip(),
                    "domain": domain.strip(),
                    "urn": urn.strip(),
                    "source_stories": [],
                    "is_canonical": True,
                }

    # 2. Parsear referencias de US
    if os.path.exists(ref_file):
        with open(ref_file, "r") as f:
            lines = f.readlines()
            current_us = None
            for line in lines:
                line = line.strip()
                if line.startswith("##"):
                    current_us = line.replace("##", "").strip()
                elif "id: PROC-" in line:
                    proc_id = line.split("id:")[1].strip()

                    if proc_id not in catalog:
                        parts = proc_id.split("-")
                        if len(parts) >= 3:
                            domain_tag = parts[1]
                            proc_name_parts = parts[2:]
                            proc_name = "-".join(proc_name_parts)

                            domain = DOMAINS.get(domain_tag, f"UNKNOWN-{domain_tag}")

                            catalog[proc_id] = {
                                "id": proc_id,
                                "name": clean_name(proc_name),
                                "domain": domain,
                                "source_stories": [],
                                "is_canonical": False,
                            }

                    if current_us and proc_id in catalog:
                        if current_us not in catalog[proc_id]["source_stories"]:
                            catalog[proc_id]["source_stories"].append(current_us)

    # 3. Formatear para salida
    final_list = []
    sorted_ids = sorted(catalog.keys(), key=lambda x: (catalog[x]["domain"], x))
    for pid in sorted_ids:
        catalog[pid]["source_stories"].sort()
        final_list.append(catalog[pid])

    with open(output_file, "w") as f:
        json.dump({"processes": final_list}, f, indent=2, ensure_ascii=False)

    print(f"Sistematización completada. {len(final_list)} procesos procesados.")


if __name__ == "__main__":
    systematize()
