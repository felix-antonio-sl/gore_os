#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Governance Linker
==============================================================================

Propósito:
- Poblar model/profunctors/governed_by.yml
- Asignar leyes base según tipo de rol

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import re
from pathlib import Path


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"
    OUTPUT_FILE = GORE_OS_ROOT / "model" / "profunctors" / "governed_by.yml"

    # Leyes base (URNs conocidos o placeholders)
    LAW_ESTATUTO = "urn:knowledge:gorenuble:gn:law:estatuto_administrativo:1.0.0"
    LAW_LOC_GORE = "urn:knowledge:gorenuble:gn:law:loc_gore:1.0.0"
    LAW_COMPRAS = "urn:knowledge:gorenuble:gn:law:ley_compras:1.0.0"
    LAW_LOBBY = "urn:knowledge:gorenuble:gn:law:ley_lobby:1.0.0"


def run():
    print("=== Governance Linker ===")

    relations = []
    roles_count = 0

    # Recorrer roles
    for f in Config.ROLES_DIR.glob("*.yml"):
        if f.name == "_index.yml":
            continue
        try:
            content = f.read_text()
            urn_match = re.search(r'urn: "([^"]+)"', content)
            type_match = re.search(r"^type:\s*(.+)$", content, re.MULTILINE)
            scope_match = re.search(r"^logic_scope:\s*(.+)$", content, re.MULTILINE)

            if urn_match:
                urn = urn_match.group(1)
                rtype = type_match.group(1).strip() if type_match else "INTERNAL"
                scope = scope_match.group(1).strip() if scope_match else "OPERATIONAL"

                roles_count += 1

                # Regla 1: Todos los INTERNAL regidos por Estatuto Admin y LOC GORE
                if rtype == "INTERNAL":
                    relations.append((urn, Config.LAW_ESTATUTO))
                    relations.append((urn, Config.LAW_LOC_GORE))

                # Regla 2: STRATEGIC regidos por Ley de Lobby
                if scope == "STRATEGIC":
                    relations.append((urn, Config.LAW_LOBBY))

                # Regla 3: EXTERNAL que interactúan, regidos por acuerdos marco (placeholder)
                # (Omitido por ahora para no ensuciar)

        except Exception:
            pass

    # Escribir profunctor
    write_profunctor(relations)
    print(
        f"✅ Profunctor governed_by generado con {len(relations)} relaciones para {roles_count} roles."
    )


def write_profunctor(relations):
    lines = [
        "_meta:",
        '  urn: "urn:goreos:profunctor:governed_by:1.0.0"',
        "  type: Profunctor",
        '  schema: "urn:goreos:schema:profunctor:1.0.0"',
        '  ontology_version: "3.0.0"',
        "",
        "signature:",
        "  source_type: Role",
        "  target_type: Law",
        '  codomain: "2"',
        "",
        "relations:",
    ]

    for role_urn, law_urn in relations:
        lines.append(f'  - source: "{role_urn}"')
        lines.append(f'    target: "{law_urn}"')

    with open(Config.OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    run()
