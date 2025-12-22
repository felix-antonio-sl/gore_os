#!/usr/bin/env python3
"""
GORE_OS Atom Extraction Audit Script
Verifica que la extracción de módulos, procesos y entidades sea completa.
"""

import re
import yaml
from pathlib import Path
from collections import defaultdict
import glob

BLUEPRINT_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint")
DOMAINS_DIR = BLUEPRINT_DIR / "domains"
ATOMS_DIR = BLUEPRINT_DIR / "atoms"


def count_source_items(domain_file: Path):
    with open(domain_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Modules: ### N. Name
    module_count = len(re.findall(r"### (\d+)\. ([^\n]+)\n", content))

    # Processes: BPMN tables + inline Process patterns
    bpmn_section = re.search(
        r"(?:## 📋 Procesos BPMN|## Procesos)\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    process_count = 0
    if bpmn_section:
        section_text = bpmn_section.group(1)

        # 1. Try to find explicit "Índice de Procesos" table
        # Buscamos la tabla que empieza con el header específico
        index_table_match = re.search(
            r"\|\s*Dominio\s*\|\s*ID\s*\|\s*Nombre\s*\|\s*Líneas\s*\|\s*\n\|[-\s|]+\|\s*\n((?:\|[^\n]+\|\s*\n)+)",
            section_text,
        )

        if index_table_match:
            rows = index_table_match.group(1).strip().split("\n")
            process_count = len(rows)
        else:
            # 2. If no index table found, count explicit headers used for processes
            # Matches: ### D01: ..., #### P1: ..., ### P3: ...
            headers = re.findall(
                r"(?:^|\n)(?:###|####)\s*(?:[DP]\d+(?:\.[A-Z])?|[DP]\d+)\s*:",
                section_text,
            )
            process_count = len(headers)

            # 3. Also check for "Mapa General del Dominio (Dxx)" pattern if count is low
            map_headers = re.findall(r"### .*?\((D\d+)\)", section_text)
            # Add unique map headers that weren't caught by the previous regex
            for mh in map_headers:
                if not any(mh in h for h in headers):
                    process_count += 1

    # Entities: Glossary table
    glossary_section = re.search(
        r"## Glosario[^\n]*\n\n\|[^\n]+\|\s*\n\|[-\s|]+\|\s*\n((?:\|[^\n]+\|\s*\n)+)",
        content,
    )
    entity_count = 0
    if glossary_section:
        rows = glossary_section.group(1).strip().split("\n")
        # Rough heuristic: count rows that look like entities
        for row in rows:
            cols = [c.strip() for c in row.split("|")[1:-1]]
            if (
                len(cols) >= 2
                and len(cols[0].strip()) > 2
                and not cols[0].strip().isupper()
            ):
                entity_count += 1

    return module_count, process_count, entity_count


def count_extracted_atoms():
    modules = len(list(ATOMS_DIR.glob("modules/*.yml"))) - 1  # exclude _index.yml
    processes = len(list(ATOMS_DIR.glob("processes/*.yml"))) - 1
    entities = len(list(ATOMS_DIR.glob("entities/*.yml"))) - 1
    return modules, processes, entities


def main():
    print("=" * 60)
    print("AUDITORÍA DE EXTRACCIÓN DE ÁTOMOS v1.0")
    print("=" * 60)

    total_exp_mod = 0
    total_exp_proc = 0
    total_exp_ent = 0

    domain_files = list(DOMAINS_DIR.glob("domain_*.md"))
    print(
        f"{'DOMAIN':<15} | {'MOD (Src)':<10} | {'PROC (Src)':<10} | {'ENT (Src)':<10}"
    )
    print("-" * 55)

    for f in sorted(domain_files, key=lambda x: x.name):
        m, p, e = count_source_items(f)
        total_exp_mod += m
        total_exp_proc += p
        total_exp_ent += e
        print(
            f"{f.name.replace('domain_', '').replace('.md', ''):<15} | {m:<10} | {p:<10} | {e:<10}"
        )

    print("-" * 55)
    print(
        f"{'TOTAL SOURCE':<15} | {total_exp_mod:<10} | {total_exp_proc:<10} | {total_exp_ent:<10}"
    )

    act_mod, act_proc, act_ent = count_extracted_atoms()

    print("\n" + "=" * 60)
    print("COMPARATIVA vs ÁTOMOS GENERADOS")
    print("=" * 60)
    print(f"{'TIPO':<15} | {'ESPERADO':<10} | {'ACTUAL':<10} | {'DELTA':<10}")
    print("-" * 55)
    print(
        f"{'Modules':<15} | {total_exp_mod:<10} | {act_mod:<10} | {act_mod - total_exp_mod:<10}"
    )
    print(
        f"{'Processes':<15} | {total_exp_proc:<10} | {act_proc:<10} | {act_proc - total_exp_proc:<10}"
    )
    print(
        f"{'Entities':<15} | {total_exp_ent:<10} | {act_ent:<10} | {act_ent - total_exp_ent:<10}"
    )
    print("=" * 60)

    if (
        act_mod == total_exp_mod
        and act_proc >= total_exp_proc
        and act_ent >= total_exp_ent
    ):
        print("\n✅ AUDITORÍA APROBADA: Extracción completa y consistente.")
    else:
        print("\n⚠️ AUDITORÍA CON OBSERVACIONES: Revisar deltas.")


if __name__ == "__main__":
    main()
