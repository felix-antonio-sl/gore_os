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

# Mapping Dominios -> Capas Omega
DOMAIN_TO_LAYER = {
    "D-PLAN": 1,
    "D-GOB": 1,
    "D-FIN": 2,
    "D-EJEC": 3,
    "D-BACK": 4,
    "D-GESTION": 4,
    "D-TDE": 4,
    "D-OPS": 4,
    "D-SEG": 0,
    "D-TERR": 0,
    "DIDESO": 0,
    "D-NORM": 1,
    "D-EVOL": 5,
    "FENIX": 3,
}


def clean_name(name):
    name = name.replace("P1", "Proceso 1")
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    name = name.replace("-", " ").title()
    return name


def systematize():
    base_path = "/Users/felixsanhueza/Developer/goreos/model/processes"
    stories_path = "/Users/felixsanhueza/Developer/goreos/model/stories"

    index_file = os.path.join(base_path, "_index.yml")
    ref_file = os.path.join(stories_path, "_us_process_ref_ids_extracted.txt")
    output_file = os.path.join(base_path, "catalog_processes_goreos.yml")

    catalog = {}

    # 1. Parsear _index.yml manualmente
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            content = f.read()
            items = re.findall(
                r"- id: ([^\n]+)\n\s+urn: ([^\n]+)\n\s+name: \"([^\"]+)\"\n\s+domain: ([^\n]+)",
                content,
            )
            for proc_id, urn, name, domain in items:
                pid = proc_id.strip()
                catalog[pid] = {
                    "id": pid,
                    "name": name.strip(),
                    "domain": domain.strip(),
                    "urn": urn.strip(),
                    "layer": DOMAIN_TO_LAYER.get(domain.strip(), 4),
                    "source_stories": [],
                    "status": "canonical",
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
                            proc_name = "-".join(parts[2:])
                            domain = DOMAINS.get(domain_tag, f"UNKNOWN-{domain_tag}")

                            catalog[proc_id] = {
                                "id": proc_id,
                                "name": clean_name(proc_name),
                                "domain": domain,
                                "layer": DOMAIN_TO_LAYER.get(domain, 4),
                                "source_stories": [],
                                "status": "extracted",
                            }

                    if current_us and proc_id in catalog:
                        if current_us not in catalog[proc_id]["source_stories"]:
                            catalog[proc_id]["source_stories"].append(current_us)

    # 3. Formatear para salida YAML manual (para evitar dependencias)
    with open(output_file, "w") as f:
        f.write("_meta:\n")
        f.write('  urn: "urn:goreos:catalog:processes:2.6.0"\n')
        f.write('  title: "Catálogo Canónico de Procesos GORE_OS"\n')
        f.write('  base_model: "Omega v2.6.0"\n')
        f.write("processes:\n")

        sorted_ids = sorted(
            catalog.keys(), key=lambda x: (catalog[x]["layer"], catalog[x]["domain"], x)
        )
        for pid in sorted_ids:
            item = catalog[pid]
            f.write(f"  - id: {item['id']}\n")
            f.write(f"    name: \"{item['name']}\"\n")
            f.write(f"    domain: {item['domain']}\n")
            f.write(f"    layer: {item['layer']}\n")
            f.write(f"    status: {item['status']}\n")
            if item["source_stories"]:
                f.write("    source_stories:\n")
                for us in sorted(item["source_stories"]):
                    f.write(f"      - {us}\n")

    print(f"Sistematización completada: {len(catalog)} procesos únicos.")


if __name__ == "__main__":
    systematize()
