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
    "SOC": "DIDESO",  # División Desarrollo Social y Humano
    "GOV": "D-GOB",
    "GOB": "D-GOB",
    "BACK": "D-BACK",
    "DEV": "D-EVOL",
    "ORG": "D-GESTION",  # Gestión de Personas/Interno
}

# Fases Omega
PHASES = {
    "F0": "Formulación",
    "F1": "Admisibilidad",
    "F2": "Evaluación",
    "F3": "Priorización",
    "F4": "Ejecución",
    "F5": "Cierre",
}


def clean_name(name):
    return name.replace("-", " ").title()


def systematize():
    input_file = "/Users/felixsanhueza/Developer/goreos/model/processes/_procesos_extraidos_us.txt"
    ref_file = "/Users/felixsanhueza/Developer/goreos/model/stories/_us_process_ref_ids_extracted.txt"
    output_file = "/Users/felixsanhueza/Developer/goreos/model/processes/catalog_processes_goreos.yml"

    # Diccionario para almacenar procesos canónicos
    # key: canonical_id, value: data
    catalog = {}

    # Primero leer las referencias para tener el dominio y nombre original
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
                    parts = proc_id.split("-")
                    if len(parts) >= 3:
                        domain_tag = parts[1]
                        proc_name_parts = parts[2:]
                        proc_name = "-".join(proc_name_parts)

                        domain = DOMAINS.get(domain_tag, f"UNKNOWN-{domain_tag}")

                        if proc_id not in catalog:
                            catalog[proc_id] = {
                                "id": proc_id,
                                "name": clean_name(proc_name),
                                "domain": domain,
                                "description": f"Proceso de {clean_name(proc_name)} del dominio {domain}.",
                                "source_stories": set(),
                            }
                        if current_us:
                            catalog[proc_id]["source_stories"].add(current_us)

    # Convertir sets a listas para YAML
    for pid in catalog:
        catalog[pid]["source_stories"] = sorted(list(catalog[pid]["source_stories"]))

    # Guardar el catálogo
    with open(output_file, "w") as f:
        yaml.dump(
            {"processes": list(catalog.values())},
            f,
            sort_keys=False,
            allow_unicode=True,
        )

    print(f"Catálogo generado con {len(catalog)} procesos únicos.")


if __name__ == "__main__":
    systematize()
