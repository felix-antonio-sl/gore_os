import os
import yaml
import re


def normalize_roles(root_dir):
    roles_dir = os.path.join(root_dir, "model/atoms/roles")
    count = 0

    # Keyword -> Domain
    domain_map = {
        "abogado": "D-NORM",
        "juridico": "D-NORM",
        "fiscal": "D-NORM",
        "norm": "D-NORM",
        "ley": "D-NORM",
        "finanza": "D-FIN",
        "presupuesto": "D-FIN",
        "tesor": "D-FIN",
        "compra": "D-FIN",
        "contab": "D-FIN",
        "territ": "D-TERR",
        "plan": "D-TERR",
        "infra": "D-TERR",
        "obra": "D-EJEC",
        "ejec": "D-EJEC",
        "inspector": "D-EJEC",
        "dev": "D-DEV",
        "arq": "D-DEV",
        "code": "D-DEV",
        "qa": "D-DEV",
        "soft": "D-DEV",
        "oper": "D-OPS",
        "soporte": "D-OPS",
        "admin": "D-OPS",
        "sys": "D-OPS",
        "seguridad": "D-SEG",
        "ciber": "D-SEG",
        "hack": "D-SEG",
        "gober": "D-GESTION",
        "consejo": "D-GESTION",
        "estrat": "D-GESTION",
        "jef": "D-GESTION",
        "direct": "D-GESTION",
        "persona": "D-BACK",
        "rrhh": "D-BACK",
        "bodega": "D-BACK",
        "invent": "D-BACK",
        "aux": "D-BACK",
    }

    for filename in os.listdir(roles_dir):
        if not filename.endswith(".yml"):
            continue
        filepath = os.path.join(roles_dir, filename)

        with open(filepath, "r") as f:
            try:
                data = yaml.safe_load(f)
            except:
                continue

        if not data:
            continue
        modified = False

        # 1. Inject URN at root
        if "urn" not in data:
            if "_meta" in data and "urn" in data["_meta"]:
                data["urn"] = data["_meta"]["urn"]
                modified = True
            else:
                data["urn"] = (
                    f"urn:goreos:atom:role:{filename.replace('.yml','')}:1.0.0"
                )
                modified = True

        # 2. Inject Domain at root
        if "domain" not in data:
            # Infer from filename/title
            text_to_search = (filename + " " + data.get("title", "")).lower()
            inferred = "D-GESTION"  # Default

            for key, dom in domain_map.items():
                if key in text_to_search:
                    inferred = dom
                    break

            data["domain"] = inferred
            modified = True

        # 3. Normalize Type (Human -> INTERNAL)
        if data.get("type") == "Human":
            data["type"] = "INTERNAL"
            modified = True
        elif "type" not in data:
            data["type"] = "INTERNAL"
            modified = True

        # 4. Check ID structure
        # If ID is missing, generate one
        if "id" not in data:
            # Generate USR-DOMAIN-NAME
            dom_suffix = data["domain"].replace("D-", "")
            name_clean = filename.replace(".yml", "").upper()[:10]
            data["id"] = f"USR-{dom_suffix}-{name_clean}"
            modified = True

        if modified:
            with open(filepath, "w") as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            count += 1
            print(f"Normalized: {filename} -> {data['domain']}")

    print(f"Total roles normalized: {count}")


if __name__ == "__main__":
    normalize_roles("/Users/felixsanhueza/fx_felixiando/gore_os")
