import yaml
import os

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
    # Specialized cleaning for common patterns
    name = name.replace("P1", "Proceso 1")
    name = name.replace("-", " ").title()
    return name


def systematize():
    base_path = "/Users/felixsanhueza/Developer/goreos/model/processes"
    stories_path = "/Users/felixsanhueza/Developer/goreos/model/stories"

    index_file = os.path.join(base_path, "_index.yml")
    ref_file = os.path.join(stories_path, "_us_process_ref_ids_extracted.txt")
    output_file = os.path.join(base_path, "catalog_processes_goreos.yml")

    # 1. Cargar el índice base
    catalog = {}
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            index_data = yaml.safe_load(f)
            if index_data and "items" in index_data:
                for item in index_data["items"]:
                    catalog[item["id"]] = {
                        "id": item["id"],
                        "name": item["name"],
                        "domain": item["domain"],
                        "urn": item.get("urn", ""),
                        "source_stories": set(),
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

                    # Normalizar ID si es necesario (ej: PROC-EJE -> PROC-EJEC)
                    # No lo normalizaremos por ahora para mantener trazabilidad exacta con US

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
                                "source_stories": set(),
                                "is_canonical": False,
                            }

                    if current_us and proc_id in catalog:
                        catalog[proc_id]["source_stories"].add(current_us)

    # 3. Formatear para salida
    final_list = []
    # Ordenar por Dominio, luego por ID
    sorted_ids = sorted(catalog.keys(), key=lambda x: (catalog[x]["domain"], x))

    for pid in sorted_ids:
        item = catalog[pid]
        item["source_stories"] = sorted(list(item["source_stories"]))
        final_list.append(item)

    # Guardar el catálogo
    with open(output_file, "w") as f:
        yaml.dump(
            {
                "_meta": {
                    "urn": "urn:goreos:catalog:processes:2.6.0",
                    "title": "Catálogo Sistematizado de Procesos GORE_OS",
                    "base_model": "Omega v2.6.0",
                },
                "processes": final_list,
            },
            f,
            sort_keys=False,
            allow_unicode=True,
        )

    print(f"Sistematización completada. {len(final_list)} procesos procesados.")


if __name__ == "__main__":
    systematize()
