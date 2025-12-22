#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Logic Scope Recalibrator
==============================================================================

Propósito:
- Refinar logic_scope para corregir los 97 mismatches detectados
- Aplicar reglas más estrictas basadas en keywords

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import re
from pathlib import Path


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"


def run():
    print("=== Logic Scope Recalibrator ===")

    fixed_count = 0

    for f in Config.ROLES_DIR.glob("*.yml"):
        if f.name == "_index.yml":
            continue
        try:
            content = f.read_text()

            # Detectar campos actuales
            title_m = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
            scope_m = re.search(r"^logic_scope:\s*(.+)$", content, re.MULTILINE)
            unit_type_m = re.search(r"^unit_type:\s*(.+)$", content, re.MULTILINE)

            if not (title_m and scope_m):
                continue

            title = title_m.group(1).lower()
            current_scope = scope_m.group(1).strip()
            unit_type = unit_type_m.group(1).strip() if unit_type_m else ""

            new_scope = current_scope

            # Regla 1: "Analista" siempre es OPERATIONAL, salvo excepción
            if (
                "analista" in title
                or "administrativo" in title
                or "auxiliar" in title
                or "conductor" in title
            ):
                new_scope = "OPERATIONAL"

            # Regla 2: "Jefe", "Encargado", "Coordinador" siempre TACTICAL
            if "jefe" in title or "encargado" in title or "coordinador" in title:
                new_scope = "TACTICAL"

            # Regla 3: "Gobernador", "Consejero", "Jefe División" (ojo override) siempre STRATEGIC
            if (
                "gobernador" in title
                or "consejero" in title
                or "jefe división" in title
            ):
                new_scope = "STRATEGIC"

            # Regla 4: Unit Type overrides (weak)
            # Solo si no hay keyword fuerte

            if new_scope != current_scope:
                # Aplicar cambio
                new_content = re.sub(
                    r"^logic_scope:\s*.+$",
                    f"logic_scope: {new_scope}",
                    content,
                    flags=re.MULTILINE,
                )
                f.write_text(new_content)
                fixed_count += 1
                # print(f"Fixed {f.name}: {current_scope} -> {new_scope}")

        except Exception as e:
            print(f"Error {f}: {e}")

    print(f"✅ Recalibrados {fixed_count} roles.")


if __name__ == "__main__":
    run()
